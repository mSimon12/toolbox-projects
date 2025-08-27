package main

import (
	"flag"
	"fmt"
	"os"
)

func run() error {
	runMode := flag.String("mode", "server", "Select running mode [server, client]")
	flag.Parse()
	var err error = nil

	switch *runMode {
	case "server":
		fmt.Println("Running as server")
		err = Server()
	case "client":
		fmt.Println("Running as client")
		err = Client()
	default:
		fmt.Println("Invalid mode option")
	}

	return err
}

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "Error:", err)
		os.Exit(1)
	}
}
