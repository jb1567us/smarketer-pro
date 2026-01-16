package cli

import (
	"fmt"
	"github.com/spf13/cobra"
	"lite-dock/internal/runtime"
	"os"
)

var (
	runDetach  bool
	runInteractive bool
	runTTY     bool
	runName    string
	runPorts   []string
	runVolumes []string
	runEnv     []string
	runNetwork string
)

var runCmd = &cobra.Command{
	Use:   "run [IMAGE] [COMMAND]",
	Short: "Run a command in a new container",
	Args:  cobra.MinimumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		image := args[0]
		var command []string
		if len(args) > 1 {
			command = args[1:]
		}

		fmt.Printf("Starting container...\nImage: %s\nCommand: %v\n", image, command)
		
		home, _ := os.UserHomeDir()
		mgr := runtime.NewManager(home)
		
		// Generate a random ID or use name
		containerID := runName
		if containerID == "" {
			containerID = fmt.Sprintf("vigorous_container_%d", os.Getpid()) // Simple implementation
		}

		cfg := runtime.ContainerConfig{
			Args:    command,
			Env:     runEnv,
			Mounts:  runVolumes,
			Network: runNetwork,
		}

		if err := mgr.Run(containerID, image, cfg); err != nil {
			fmt.Printf("Error running container: %v\n", err)
			os.Exit(1)
		}
	},
}

func init() {
	runCmd.Flags().BoolVarP(&runDetach, "detach", "d", false, "Run container in background and print container ID")
	runCmd.Flags().BoolVarP(&runInteractive, "interactive", "i", false, "Keep STDIN open even if not attached")
	runCmd.Flags().BoolVarP(&runTTY, "tty", "t", false, "Allocate a pseudo-TTY")
	runCmd.Flags().StringVar(&runName, "name", "", "Assign a name to the container")
	runCmd.Flags().StringSliceVarP(&runPorts, "publish", "p", []string{}, "Publish a container's port(s) to the host")
	runCmd.Flags().StringSliceVarP(&runVolumes, "volume", "v", []string{}, "Bind mount a volume")
	runCmd.Flags().StringSliceVarP(&runEnv, "env", "e", []string{}, "Set environment variables")
	runCmd.Flags().StringVar(&runNetwork, "network", "", "Connect a container to a network (use 'host' for host networking)")

	rootCmd.AddCommand(runCmd)
}
