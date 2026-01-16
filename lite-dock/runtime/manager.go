package runtime

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"lite-dock/internal/image"
	"runtime"
)

type Manager struct {
	StateDir string
	ImageStore string
}

func NewManager(homeDir string) *Manager {
	return &Manager{
		StateDir: filepath.Join(homeDir, ".litedock", "containers"),
		ImageStore: filepath.Join(homeDir, ".litedock", "images"),
	}
}

func (m *Manager) Run(cmdID string, imgRef string, cfg ContainerConfig) error {
	// 1. Prepare bundle directory
	bundleDir := filepath.Join(m.StateDir, cmdID)
	if err := os.MkdirAll(bundleDir, 0755); err != nil {
		return err
	}
	
	// 2. Setup RootFS
	// For MVP: Copy the extracted image to bundle/rootfs (Slow but simple)
	// TODO: Use OverlayFS for speed
	
	// Sanitize ref for path lookup
    // Using the same simple sanitization or need to resolve generic helper
    // For now assuming the stored format matches what we can guess or listing it.
    // Let's assume we can find it.
    // Re-parsing to get directory name.
    // This is duplicate logic from image manager, should be shared but keeping it inline for speed.
    // We will list the images dir and try to find a match if we can't guess exactly.
	// Actually, let's just rely on the user passing exact match for now or assume we can find it.
	
	// Better: We should probably ask the ImageManager to give us the path.
	// But let's verify path exists.
	// Hack: We need the proper directory name that ImageManager created.
	// Since I don't have the "sanitize" logic exposed, this is a risk.
	// I will just assume standard formatting: repo_tag. e.g. alpine_latest
	
	dirName, err := image.GetImageDirName(imgRef)
	if err != nil {
		return fmt.Errorf("resolving image path: %w", err)
	}
	
	imagePath := filepath.Join(m.ImageStore, dirName)
	
	// Verify image exists
	if _, err := os.Stat(imagePath); os.IsNotExist(err) {
		return fmt.Errorf("image %s not found. Try 'lite-dock pull %s' first. Path: %s", imgRef, imgRef, imagePath)
	}
	
	rootfs := filepath.Join(bundleDir, "rootfs")
	if err := os.MkdirAll(rootfs, 0755); err != nil {
		return err
	}
	
    // COPY (Naive)
    if runtime.GOOS == "windows" {
         // Windows-friendly copy
         powershellArgs := []string{"-Command", fmt.Sprintf("Copy-Item -Path '%s\\*' -Destination '%s' -Recurse", imagePath, rootfs)}
         cpCmd := exec.Command("powershell", powershellArgs...)
         if out, err := cpCmd.CombinedOutput(); err != nil {
             return fmt.Errorf("copying rootfs (windows): %v, %s", err, string(out))
         }
    } else {
        // Use 'cp -r' for simplicity via shell on Linux/Unix
        cpCmd := exec.Command("cp", "-r", imagePath + "/.", rootfs)
        if out, err := cpCmd.CombinedOutput(); err != nil {
             return fmt.Errorf("copying rootfs: %v, %s", err, string(out))
        }
    }

	// 3. Generate config.json (Spec)
	spec := GenerateSpec(cfg)
	
	specFile, err := os.Create(filepath.Join(bundleDir, "config.json"))
	if err != nil {
		return err
	}
	defer specFile.Close()
	
	enc := json.NewEncoder(specFile)
	enc.SetIndent("", "\t")
	if err := enc.Encode(spec); err != nil {
		return err
	}

	// 4. Run 'runc' or 'HCS'
    if runtime.GOOS == "windows" {
        fmt.Printf("Starting container %s via HCS (Lightweight VM)...\n", cmdID)
        launcher := NewHCSLauncher()
        return launcher.RunContainer(cmdID, bundleDir)
    }

	// runc run -b bundleDir containerID
	fmt.Printf("Starting container %s via runc...\n", cmdID)
	runcArgs := []string{"run", "-b", bundleDir, cmdID}
	runcCmd := exec.Command("runc", runcArgs...)
	runcCmd.Stdin = os.Stdin
	runcCmd.Stdout = os.Stdout
	runcCmd.Stderr = os.Stderr
	
	return runcCmd.Run()
}
