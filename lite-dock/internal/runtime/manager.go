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
	
    // COPY (Naive but robust on Windows)
    if runtime.GOOS == "windows" {
         // Robocopy is much better at handling symlinks and deep paths than Copy-Item
         // /E - Copy subdirectories, including empty ones.
         // /COPY:DAT - Copy Data, Attributes, Time stamps.
         // /XJ - Exclude junction points (can cause infinite loops if they point to parents).
         // /R:3 /W:5 - 3 retries, 5 seconds wait.
         // /NJH /NJS /NDL /NC /NS - Less verbose output.
         args := []string{imagePath, rootfs, "/E", "/COPY:DAT", "/R:3", "/W:5", "/NFL", "/NDL", "/NJH", "/NJS"}
         cpCmd := exec.Command("robocopy", args...)
         // Robocopy returns exit codes 0-7 for success (some files copied, etc)
         err := cpCmd.Run()
         if err != nil {
             if exitErr, ok := err.(*exec.ExitError); ok {
                 if exitErr.ExitCode() < 8 {
                     // Success!
                 } else {
                     return fmt.Errorf("copying rootfs (robocopy exit %d): %v", exitErr.ExitCode(), err)
                 }
             } else {
                 return fmt.Errorf("copying rootfs (robocopy): %v", err)
             }
         }
    } else {
        // Use 'cp -r' for simplicity via shell on Linux/Unix
        cpCmd := exec.Command("cp", "-r", imagePath + "/.", rootfs)
        if out, err := cpCmd.CombinedOutput(); err != nil {
             return fmt.Errorf("copying rootfs: %v, %s", err, string(out))
        }
    }

    // Helper to convert Windows path to WSL path
    toWSLPath := func(winPath string) string {
        if len(winPath) < 2 || winPath[1] != ':' {
            return winPath // Already relative or unix
        }
        drive := winPath[0]
        pathWithoutDrive := winPath[3:]
        // Naive assumption: standard /mnt/[drive]/ access
        return fmt.Sprintf("/mnt/%c/%s", drive+32, filepath.ToSlash(pathWithoutDrive))
    }

    // 3. Prepare DNS (resolv.conf)
    // Create a local resolv.conf in the bundle to ensure connectivity inside container
    // even if host's /etc/resolv.conf is a broken symlink or unreachable.
    dnsPath := filepath.Join(bundleDir, "resolv.conf")
    dnsContent := "nameserver 8.8.8.8\nnameserver 8.8.4.4\nnameserver 1.1.1.1\n"
    if err := os.WriteFile(dnsPath, []byte(dnsContent), 0644); err != nil {
        return fmt.Errorf("creating resolv.conf: %w", err)
    }

	// 4. Generate config.json (Spec)
	spec := GenerateSpec(cfg)
    
    // Override the resolv.conf mount to use our clean one
    for i, m := range spec.Mounts {
        if m.Destination == "/etc/resolv.conf" {
            // FIX: If on Windows, we must provide the WSL path, not the Win path
            // because this config.json is consumed by runc INSIDE WSL.
            if runtime.GOOS == "windows" {
                spec.Mounts[i].Source = toWSLPath(dnsPath)
            } else {
                spec.Mounts[i].Source = dnsPath
            }
        }
    }
	
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

	// 4. Run 'runc' (Native on Linux, via WSL on Windows)
    if runtime.GOOS == "windows" {
        fmt.Printf("Starting container %s via runc (WSL)...\n", cmdID)
        
        wslPath := toWSLPath(bundleDir)

        // On Windows, we need to run runc INSIDE WSL
        // wsl -u root runc run -b [bundle_path] [id]
        runcArgs := []string{"-u", "root", "runc", "run", "-b", wslPath, cmdID}
        runcCmd := exec.Command("wsl", runcArgs...)
        runcCmd.Stdin = os.Stdin
        runcCmd.Stdout = os.Stdout
        runcCmd.Stderr = os.Stderr
        
        return runcCmd.Run()
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
