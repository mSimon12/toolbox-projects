package main

import (
	"flag"
	"fmt"
	"os"
	"strconv"
	"tcpchat/tcp"
)

func run() error {
	var port int
	var maxClients int
	var err error = nil

	flag.IntVar(&port, "port", 8080, "Set server port")
	flag.IntVar(&maxClients, "maxClients", 50, "Define maximum concurrent connections")
	flag.Parse()

	fmt.Println("Running as server")
	err = tcp.Server(strconv.Itoa(port), maxClients)

	return err
}

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "Error:", err)
		os.Exit(1)
	}
}
