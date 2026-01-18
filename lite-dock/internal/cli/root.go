package cli

import (
	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "lite-dock",
	Short: "A lightweight container runtime compatible with Docker",
	Long:  `Lite-Dock is a lightweight implementation of a container runtime that mimics the Docker CLI.`,
}

func Execute() error {
	return rootCmd.Execute()
}

func init() {
	// Global flags can be defined here
}
