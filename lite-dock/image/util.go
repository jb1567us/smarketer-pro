package image

import (
	"fmt"
	"strings"
	"github.com/google/go-containerregistry/pkg/name"
)

// GetImageDirName converts an image reference to a safe directory name
func GetImageDirName(imageRef string) (string, error) {
	ref, err := name.ParseReference(imageRef)
	if err != nil {
		return "", fmt.Errorf("parsing reference: %w", err)
	}
	// Sanitize: "library/alpine:latest" -> "index.docker.io_library_alpine_latest"
	// or simplified: just replace / and : with _
	// The previous logic was: r.Context().RepositoryStr() + "_" + r.Identifier()
	
	// We need to match exactly what Pull used.
	// r.Context().RepositoryStr() usually includes registry if not implicit? 
	// name.ParseReference("alpine") -> index.docker.io/library/alpine:latest
	// Context().RepositoryStr() -> index.docker.io/library/alpine
	// Identifier() -> latest
	
	repo := ref.Context().RepositoryStr()
	tag := ref.Identifier()
	
	// Windows doesn't like colons in path
	safeRepo := strings.ReplaceAll(repo, "/", "_")
	safeRepo = strings.ReplaceAll(safeRepo, ":", "_") // usually not in repo str
	safeTag := strings.ReplaceAll(tag, ":", "_")
	
	return safeRepo + "_" + safeTag, nil
}
