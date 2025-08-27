package main

import (
	"errors"
	"fmt"
	"net"
)

func Client(serverAddress string) error {
	tcpConn, err := net.Dial("tcp", serverAddress)
	if err != nil {
		return fmt.Errorf("failed connecting: %w", err)
	}
	defer tcpConn.Close()

	msg := []byte("Hello from Client")

	if _, err := tcpConn.Write(msg); err != nil {
		return errors.New("failed to send message")
	}

	return nil
}
