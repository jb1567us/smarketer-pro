package runtime

import (
	"encoding/json"
	"fmt"
	"github.com/Microsoft/hcsshim"
	"os"
	"path/filepath"
	"strings"
)

// HCSLauncher handles launching Linux containers in a lightweight Utility VM
type HCSLauncher struct {
	KernelPath string
}

func NewHCSLauncher() *HCSLauncher {
	// Try to find default WSL2 kernel path
	kernel := `C:\Windows\System32\lxss\lib\kernel`
	if _, err := os.Stat(kernel); err != nil {
		kernel = ""
	}
	return &HCSLauncher{
		KernelPath: kernel,
	}
}

// RunContainer launches a container using HCS
func (l *HCSLauncher) RunContainer(containerID string, bundleDir string) error {
	if l.KernelPath == "" {
		return fmt.Errorf("linux kernel not found. please ensure WSL2 is installed or specify kernel path")
	}

	// 1. Load OCI spec to get process info
	specPath := filepath.Join(bundleDir, "config.json")
	specData, err := os.ReadFile(specPath)
	if err != nil {
		return fmt.Errorf("failed to read spec: %w", err)
	}

	var ociSpec struct {
		Process struct {
			Args []string `json:"args"`
			Env  []string `json:"env"`
			Cwd  string   `json:"cwd"`
		} `json:"process"`
	}
	if err := json.Unmarshal(specData, &ociSpec); err != nil {
		return fmt.Errorf("failed to unmarshal spec: %w", err)
	}

	// 2. Define Container Configuration for HCS
	rootfsPath := filepath.Join(bundleDir, "rootfs")
	
	config := &hcsshim.ContainerConfig{
		SystemType:              "Container",
		Owner:                   "lite-dock",
		HostName:                "lite-dock",
		HvPartition:             true, // Use Hyper-V isolation for Linux on Windows
		ContainerType:           "linux",
		TerminateOnLastHandleClosed: true,
		Layers: []hcsshim.Layer{
			{Path: rootfsPath},
		},
	}

	// 3. Create the container
	hcsContainer, err := hcsshim.CreateContainer(containerID, config)
	if err != nil {
		return fmt.Errorf("failed to create HCS container: %w", err)
	}
	defer hcsContainer.Terminate()

	// 4. Start the container
	if err := hcsContainer.Start(); err != nil {
		return fmt.Errorf("failed to start HCS container: %w", err)
	}

	fmt.Printf("Lightweight VM Container %s started successfully via HCS\n", containerID)

	// 5. Create the process inside the container
	processConfig := &hcsshim.ProcessConfig{
		CommandLine:      fmt.Sprintf("%s", ociSpec.Process.Args[0]), // Simplified
		WorkingDirectory: ociSpec.Process.Cwd,
		Environment:      make(map[string]string),
		CreateStdInPipe:  true,
		CreateStdOutPipe: true,
		CreateStdErrPipe: true,
	}
	
	// Correctly handle args
	if len(ociSpec.Process.Args) > 1 {
		for i := 1; i < len(ociSpec.Process.Args); i++ {
			processConfig.CommandLine += " " + ociSpec.Process.Args[i]
		}
	}

	for _, e := range ociSpec.Process.Env {
		parts := strings.SplitN(e, "=", 2)
		if len(parts) == 2 {
			processConfig.Environment[parts[0]] = parts[1]
		}
	}

	hcsProcess, err := hcsContainer.CreateProcess(processConfig)
	if err != nil {
		return fmt.Errorf("failed to create process in HCS container: %w", err)
	}
	defer hcsProcess.Close()

	// 6. Wait for process to exit
	return hcsProcess.Wait()
}
