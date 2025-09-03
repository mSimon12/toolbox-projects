package tcp

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net"
)

func TcpSend(tcpConn net.Conn, msg string) error {
	chatMsg := ChatMessage{
		Sender:  tcpConn.LocalAddr().String(),
		Content: msg,
	}

	payload, err := json.Marshal(chatMsg)
	if err != nil {
		return fmt.Errorf("failed to marshal message: %w", err)
	}

	if _, err := tcpConn.Write(payload); err != nil {
		return errors.New("failed to send message")
	}

	return nil
}

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

		var chatMsg ChatMessage
		if err := json.Unmarshal(buf[:n], &chatMsg); err != nil {
			fmt.Println("Failed to unmarshal message:", err)
			continue
		}
		fmt.Printf("Received from %s: %s\n", chatMsg.Sender, chatMsg.Content)

		// optionally send back a reply
		_ = TcpSend(tcpConn, "Message received")
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
