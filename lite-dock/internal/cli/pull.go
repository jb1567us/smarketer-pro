package cli

import (
	"fmt"
	"lite-dock/internal/image"
	"os"
	"path/filepath"

	"github.com/spf13/cobra"
)

var pullCmd = &cobra.Command{
	Use:   "pull [IMAGE]",
	Short: "Pull an image from a registry",
	Args:  cobra.MinimumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		home, _ := os.UserHomeDir()
		storePath := filepath.Join(home, ".litedock")
		mgr := image.NewManager(storePath)
		
		if err := mgr.Pull(args[0]); err != nil {
			fmt.Printf("Error pulling image: %v\n", err)
			os.Exit(1)
		}
	},
}

func init() {
	rootCmd.AddCommand(pullCmd)
}
