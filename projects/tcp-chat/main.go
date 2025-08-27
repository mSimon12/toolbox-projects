package main

import (
	"flag"
	"fmt"
	"os"
	"strconv"
)

func run() error {
	var runMode string
	var host string
	var port int
	var maxClients int
	var err error = nil

	flag.StringVar(&runMode, "mode", "client", "Select running mode [server, client]")
	flag.StringVar(&host, "host", "localhost", "Set server address")
	flag.IntVar(&port, "port", 8080, "Set server port")
	flag.IntVar(&maxClients, "maxClients", 50, "Define maximum concurrent connections")
	flag.Parse()

	switch runMode {
	case "client":
		address := host + ":" + strconv.Itoa(port)
		err = Client(address)

	case "server":
		fmt.Println("Running as server")
		err = Server(strconv.Itoa(port), maxClients)

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
