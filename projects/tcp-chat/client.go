package main

import (
	"bufio"
	"errors"
	"fmt"
	"io"
	"net"
	"os"
	"strings"
)

func handleResponses(tcpConn net.Conn) {
	buf := make([]byte, 1024)
	for {
		n, err := tcpConn.Read(buf)
		if err != nil {
			if err == io.EOF {
				fmt.Println("Server disconnected:", tcpConn.RemoteAddr())
			} else {
				fmt.Println("Read error:", err)
			}
			return
		}

		msg := string(buf[:n])
		fmt.Printf("\n(%s)\n%s\n\t\t\t ", tcpConn.RemoteAddr(), msg)
	}

}

func Client(serverAddress string) error {
	tcpConn, err := net.Dial("tcp", serverAddress)
	if err != nil {
		return fmt.Errorf("failed connecting: %w", err)
	}
	defer tcpConn.Close()
	fmt.Println("Connected to Server", tcpConn.RemoteAddr())

	go handleResponses(tcpConn)

	for {
		reader := bufio.NewReader(os.Stdin)
		fmt.Print("\n\t\t\t ")
		cmdInput, _ := reader.ReadString('\n')
		cmdInput = strings.TrimSpace(cmdInput) // Remove any surrounding whitespace including the newline.

		if strings.Compare(cmdInput, "/exit") == 0 {
			return nil
		}

		msg := []byte(cmdInput)

		if _, err := tcpConn.Write(msg); err != nil {
			return errors.New("failed to send message")
		}
	}
}
