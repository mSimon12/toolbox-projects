package main

import (
	"flag"
	"fmt"
	"log/slog"
	"net"
	"os"
	"strconv"
	"tcpchat/transport"
)

type ChatClient struct {
	transport transport.TransportNode
	msgCh     chan transport.ChatMessage
}

func NewChatClient(serverAddress string) (*ChatClient, error) {
	conn, err := net.Dial("tcp", serverAddress)
	if err != nil {
		return nil, fmt.Errorf("failed connecting: %w", err)
	}
	slog.Info("Connected to Server", "address", conn.RemoteAddr())

	newClient := ChatClient{
		transport: transport.TransportNode{
			TcpConn: conn,
			NodeId:  conn.LocalAddr().String()},
		msgCh: make(chan transport.ChatMessage)}

	go newClient.transport.TcpReceive(newClient.msgCh)

	return &newClient, nil

}

func run() error {
	var host string
	var port int

	flag.StringVar(&host, "host", "localhost", "Set server address")
	flag.IntVar(&port, "port", 8080, "Set server port")
	flag.Parse()

	address := host + ":" + strconv.Itoa(port)

	client, err := NewChatClient(address)
	if err != nil {
		return err
	}

	if err := executeGUI(client); err != nil {
		return err
	}

	return nil
}

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "Error:", err)
		os.Exit(1)
	}
}
