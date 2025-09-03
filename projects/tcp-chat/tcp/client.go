package tcp

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net"
)

type TcpClient struct {
	tcpConn net.Conn
}

func (client *TcpClient) TcpReceive(newMsg chan<- ChatMessage) {
	buf := make([]byte, 1024)
	for {
		n, err := client.tcpConn.Read(buf)
		if err != nil {
			if err == io.EOF {
				// fmt.Println("Server disconnected:", client.tcpConn.RemoteAddr())
			} else {
				// fmt.Println("Read error:", err)
			}
			return
		}

		msg := ChatMessage{}
		if err := json.Unmarshal(buf[:n], &msg); err != nil {
			// fmt.Println("Failed to unmarshal message:", err)
			continue
		}

		newMsg <- msg
	}
}

func (client *TcpClient) TcpSend(msg string) error {
	chatMsg := ChatMessage{
		Sender:  client.tcpConn.RemoteAddr().String(),
		Content: msg,
	}

	payload, err := json.Marshal(chatMsg)
	if err != nil {
		return fmt.Errorf("failed to marshal message: %w", err)
	}

	if _, err := client.tcpConn.Write(payload); err != nil {
		return errors.New("failed to send message")
	}

	return nil
}

func (client *TcpClient) Close() error {
	return client.tcpConn.Close()
}

func NewTCPClient(serverAddress string) (*TcpClient, error) {
	conn, err := net.Dial("tcp", serverAddress)
	if err != nil {
		return nil, fmt.Errorf("failed connecting: %w", err)
	}
	fmt.Println("Connected to Server", conn.RemoteAddr())

	return &TcpClient{tcpConn: conn}, nil
}
