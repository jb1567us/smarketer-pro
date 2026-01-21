package image

import (
	"fmt"
    "io"
	"os"
	"path/filepath"

	"github.com/google/go-containerregistry/pkg/crane"
	"github.com/google/go-containerregistry/pkg/v1/mutate"
)

// Manager handles image operations
type Manager struct {
	StorePath string
}

func NewManager(storePath string) *Manager {
	return &Manager{
		StorePath: storePath,
	}
}

// Pull downloads an image and unpacks it to the store
func (m *Manager) Pull(imageRef string) error {
	fmt.Printf("Pulling %s...\n", imageRef)
	
	img, err := crane.Pull(imageRef)
	if err != nil {
		return fmt.Errorf("pulling image: %w", err)
	}

	// For simple MVP: Flatten the image into a directory
	// Store at ~/.litedock/images/<tag>
	// Note: We need to sanitize the tag to be a valid directory name
	dirName, err := GetImageDirName(imageRef)
	if err != nil {
		return err
	}
	
	destDir := filepath.Join(m.StorePath, "images", dirName)
	if err := os.MkdirAll(destDir, 0755); err != nil {
		return err
	}

	// Clean directory if exists
	// os.RemoveAll(destDir) // Safety check needed

	fmt.Printf("Extracting to %s...\n", destDir)
	// Create a reader for the flattened filesystem (tar stream)
	rc := mutate.Extract(img)
	defer rc.Close()
    
    // SAVE TARBALL FOR WSL IMPORT
    // We tee the stream to a file so we have the tarball for wsl --import
    tarPath := destDir + ".tar"
    tarFile, err := os.Create(tarPath)
    if err != nil {
         return fmt.Errorf("creating tar file: %w", err)
    }
    defer tarFile.Close()
    
    // We can't easily Tee because Untar might consume differently or we want to buffer.
    // Simpler: Copy to file, then read from file to Untar (or just keep the file).
    // Actually, since we need the filesystem for 'settings.yml' checks in auto_runner?
    // auto_runner checks 'usr/local/...' in the extracted path.
    // So we need BOTH the tarball and the extracted files.
    
    // Let's copy stream to file first.
    fmt.Printf("Saving filesystem tarball to %s...\n", tarPath)
    if _, err := io.Copy(tarFile, rc); err != nil {
        return fmt.Errorf("saving tarball: %w", err)
    }
    // Sync to ensure flush
    tarFile.Sync()
    
    // Now re-open for Untar
	// (Since we consumed rc)
    tarReader, err := os.Open(tarPath)
    if err != nil {
        return fmt.Errorf("opening tarball for extraction: %w", err)
    }
    defer tarReader.Close()
    
	// Extract to directory
	if err := Untar(destDir, tarReader); err != nil {
		return fmt.Errorf("untaring image: %w", err)
	}
	
	fmt.Println("Image pulled and unpacked successfully.")
	return nil
}

func (m *Manager) List() error {
	// List directories in StorePath/images
	return nil
}
