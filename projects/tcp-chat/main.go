package main

import (
	"flag"
	"fmt"
	"os"
)

func run() error {
	runMode := flag.String("mode", "client", "Select running mode [server, client]")
	flag.Parse()
	var err error = nil

	switch *runMode {
	case "client":
		fmt.Println("Running as client")
		err = Client()
	case "server":
		fmt.Println("Running as server")
		err = Server()
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
