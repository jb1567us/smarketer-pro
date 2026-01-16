package image

import (
	"fmt"
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
	// Create a reader for the flattened filesystem
	rc := mutate.Extract(img)
	defer rc.Close()
	
	// Extract to directory
	if err := Untar(destDir, rc); err != nil {
		return fmt.Errorf("untaring image: %w", err)
	}
	
	fmt.Println("Image pulled and unpacked successfully.")
	return nil
}

func (m *Manager) List() error {
	// List directories in StorePath/images
	return nil
}
