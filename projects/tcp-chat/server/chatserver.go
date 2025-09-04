package main

import (
	"flag"
	"fmt"
	"net"
	"os"
	"strconv"
	"tcpchat/tcp"
)

type tcpServer struct {
	users map[string]tcp.TcpInterface
	msgCh chan tcp.ChatMessage
}

func (s *tcpServer) addUser(userConn net.Conn) {
	newUser := tcp.TcpInterface{TcpConn: userConn, Id: userConn.RemoteAddr().String()}
	s.users[userConn.RemoteAddr().String()] = newUser
	go newUser.TcpReceive(s.msgCh)
}

func (s *tcpServer) MsgsController() {
	for {
		msg := <-s.msgCh

		for _, user := range s.users {
			if user.Id != msg.Sender {
				user.TcpSend(msg)
			}
		}
	}
}

func NewTcpServer(port string, maxClients int) error {

	listener, err := net.Listen("tcp", ":"+port)
	if err != nil {
		return fmt.Errorf("failed starting listener: %w", err)
	}
	defer listener.Close()

	server := tcpServer{
		users: make(map[string]tcp.TcpInterface),
		msgCh: make(chan tcp.ChatMessage),
	}

	go server.MsgsController()

	for {
		conn, err := listener.Accept()
		if err != nil {
			return fmt.Errorf("failed accepting connection: %w", err)
		}
		fmt.Println("Accepted connection from:", conn.RemoteAddr())

		server.addUser(conn)
	}
}

func run() error {
	var port int
	var maxClients int
	var err error = nil

	flag.IntVar(&port, "port", 8080, "Set server port")
	flag.IntVar(&maxClients, "maxClients", 50, "Define maximum concurrent connections")
	flag.Parse()

	fmt.Println("Starting server")
	err = NewTcpServer(strconv.Itoa(port), maxClients)

	return err
}

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "Error:", err)
		os.Exit(1)
	}
}
