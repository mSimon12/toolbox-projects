package main

import (
	"errors"
	"fmt"
	"net"
)

func Client() error {
	tcpConn, err := net.Dial("tcp", "localhost:8080")
	if err != nil {
		return fmt.Errorf("failed connecting: %w", err)
	}
	defer tcpConn.Close()

	msg := []byte("Hello from Client")

	tcpConn.Write(msg)

	if _, err := tcpConn.Write([]byte("Hello, World!")); err != nil {
		return errors.New("failed to send message")
	}

	return nil
}
