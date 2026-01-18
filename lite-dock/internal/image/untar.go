package image

import (
	"archive/tar"
	"fmt"
	"io"
	"os"
	"path/filepath"
)

// Untar extracts a tar stream to a destination directory
func Untar(dst string, r io.Reader) error {
	tr := tar.NewReader(r)

	for {
		header, err := tr.Next()
		if err == io.EOF {
			break // End of archive
		}
		if err != nil {
			return err
		}

		target := filepath.Join(dst, header.Name)

		switch header.Typeflag {
		case tar.TypeDir:
			if err := os.MkdirAll(target, 0755); err != nil {
				return err
			}
		case tar.TypeReg:
			// Ensure destination file is removed before writing
			os.Remove(target)
			f, err := os.OpenFile(target, os.O_CREATE|os.O_RDWR, os.FileMode(header.Mode))
			if err != nil {
				return err
			}
			if _, err := io.Copy(f, tr); err != nil {
				f.Close()
				return err
			}
			f.Close()
		case tar.TypeSymlink:
			// Remove existing symlink/file if it exists
			os.Remove(target)
			err := os.Symlink(header.Linkname, target)
			if err != nil {
				// On Windows, creating symlinks requires special privileges or Developer Mode.
				// We log a warning but continue, as some symlinks might not be critical
				// or can be handled as regular files in a more advanced implementation.
				fmt.Printf("Warning: Failed to create symlink %s -> %s: %v\n", target, header.Linkname, err)
                if os.Getenv("OS") == "Windows_NT" {
                    fmt.Printf("  Tip: Try enabling Windows Developer Mode to allow symlink creation without admin rights.\n")
                }
			}
		case tar.TypeLink:
			// Handle hard links
			os.Remove(target)
			linkTarget := filepath.Join(dst, header.Linkname)
			if err := os.Link(linkTarget, target); err != nil {
				fmt.Printf("Warning: Failed to create hard link %s -> %s: %v\n", target, linkTarget, err)
			}
		}
	}
	return nil
}
