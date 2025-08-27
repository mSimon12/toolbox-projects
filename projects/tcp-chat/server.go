package main

import (
	"fmt"
	"io"
	"net"
)

func ConnHandler(tcpConn net.Conn) {
	defer tcpConn.Close()

	buf := make([]byte, 1024)
	for {
		n, err := tcpConn.Read(buf)
		if err != nil {
			if err == io.EOF {
				fmt.Println("Client disconnected:", tcpConn.RemoteAddr())
			} else {
				fmt.Println("Read error:", err)
			}
			return
		}

		msg := string(buf[:n])
		fmt.Printf("Received from %s: %s\n", tcpConn.RemoteAddr(), msg)

		// optionally send back a reply
		_, _ = tcpConn.Write([]byte("Message received\n"))
	}
}

func Server(port string, maxClients int) error {

	listener, err := net.Listen("tcp", ":"+port)
	if err != nil {
		return fmt.Errorf("failed starting listener: %w", err)
	}
	defer listener.Close()

	for {
		tcpConn, err := listener.Accept()
		if err != nil {
			return fmt.Errorf("failed accepting connection: %w", err)
		}
		fmt.Println("Accepted connection from:", tcpConn.RemoteAddr())

		go ConnHandler(tcpConn)
	}
}
