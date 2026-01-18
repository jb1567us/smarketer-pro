package cli

import (
	"fmt"
	"github.com/spf13/cobra"
)

var imagesCmd = &cobra.Command{
	Use:   "images",
	Short: "List images",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("REPOSITORY   TAG       IMAGE ID   CREATED   SIZE")
		// TODO: List actual images
	},
}

func init() {
	rootCmd.AddCommand(imagesCmd)
}
