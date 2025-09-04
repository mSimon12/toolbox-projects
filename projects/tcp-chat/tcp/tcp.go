package tcp

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"net"
)

type TcpInterface struct {
	TcpConn net.Conn
	Id      string
}

func (client *TcpInterface) TcpReceive(newMsg chan<- ChatMessage) {
	buf := make([]byte, 1024)
	for {
		n, err := client.TcpConn.Read(buf)
		if err != nil {
			if err == io.EOF {
				slog.Error("Server disconnected", "address", client.TcpConn.RemoteAddr())
			} else {
				slog.Error("Read error", "error", err)
			}
			return
		}

		msg, err := decodeMsg(buf[:n])
		if err != nil {
			slog.Error("Failed to decode message", "error", err)
			continue
		}

		newMsg <- msg
	}
}

func (client *TcpInterface) TcpSend(msg ChatMessage) error {
	payload, err := encodeMsg(msg)
	if err != nil {
		return fmt.Errorf("failed to marshal message: %w", err)
	}

	if _, err := client.TcpConn.Write(payload); err != nil {
		return errors.New("failed to send message")
	}

	return nil
}

func (client *TcpInterface) Close() error {
	return client.TcpConn.Close()
}

func encodeMsg(msg ChatMessage) ([]byte, error) {
	payload, err := json.Marshal(msg)
	if err != nil {
		errMsg := fmt.Sprintf("failed to marshal message: %v", err)
		return nil, errors.New(errMsg)
	}

	return payload, nil
}

func decodeMsg(payload []byte) (ChatMessage, error) {
	n := len(payload)
	msg := ChatMessage{}
	if err := json.Unmarshal(payload[:n], &msg); err != nil {
		errMsg := fmt.Sprintf("failed to unmarshal message: %v", err)
		return ChatMessage{}, errors.New(errMsg)
	}

	return msg, nil
}
