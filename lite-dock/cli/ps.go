package cli

import (
	"fmt"
	"github.com/spf13/cobra"
)

var psAll bool

var psCmd = &cobra.Command{
	Use:   "ps",
	Short: "List containers",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES")
		// TODO: List actual containers
	},
}

func init() {
	psCmd.Flags().BoolVarP(&psAll, "all", "a", false, "Show all containers (default shows just running)")
	rootCmd.AddCommand(psCmd)
}
