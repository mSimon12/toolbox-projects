package main

import (
	"flag"
	"fmt"
	"log/slog"
	"net"
	"os"
	"strconv"
	"strings"
	"tcpchat/tcp"

	"github.com/charmbracelet/bubbles/textarea"
	"github.com/charmbracelet/bubbles/viewport"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

const gap = "\n\n"

type (
	errMsg error
)

type chatMsg tcp.ChatMessage

func listenForMessages(ch <-chan tcp.ChatMessage) tea.Cmd {
	return func() tea.Msg {
		msg := <-ch
		return chatMsg(msg)
	}
}

func sendMessageCmd(client tcp.TcpInterface, msg string) tea.Cmd {
	chatMsg := tcp.ChatMessage{
		Sender:  client.Id,
		Content: msg,
	}

	return func() tea.Msg {
		if err := client.TcpSend(chatMsg); err != nil {
			return errMsg(err) // Bubbletea will handle this like other errors
		}
		return nil
	}
}

type chatModel struct {
	viewport    viewport.Model //Messages area
	messages    []string
	textarea    textarea.Model //Area for writing messages
	senderStyle lipgloss.Style
	receivedMsg <-chan tcp.ChatMessage // channel for new messages
	client      tcp.TcpInterface
	err         error
}

func initialModel(receivedMsg <-chan tcp.ChatMessage, client tcp.TcpInterface) chatModel {
	ta := textarea.New()
	ta.Placeholder = "Send a message..."
	ta.Focus()

	ta.Prompt = "┃ "
	ta.CharLimit = 280

	ta.SetWidth(30)
	ta.SetHeight(3)

	// Remove cursor line styling
	ta.FocusedStyle.CursorLine = lipgloss.NewStyle()

	ta.ShowLineNumbers = false

	vp := viewport.New(30, 5)
	vp.SetContent(`Welcome to the chat room!
Type a message and press Enter to send.`)

	ta.KeyMap.InsertNewline.SetEnabled(false)

	return chatModel{
		textarea:    ta,
		messages:    []string{},
		viewport:    vp,
		senderStyle: lipgloss.NewStyle().Foreground(lipgloss.Color("5")),
		receivedMsg: receivedMsg,
		client:      client,
		err:         nil,
	}
}

func (m chatModel) Init() tea.Cmd {
	return listenForMessages(m.receivedMsg)
}

func (m chatModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var (
		tiCmd tea.Cmd
		vpCmd tea.Cmd
	)

	m.textarea, tiCmd = m.textarea.Update(msg)
	m.viewport, vpCmd = m.viewport.Update(msg)

	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.viewport.Width = msg.Width
		m.textarea.SetWidth(msg.Width)
		m.viewport.Height = msg.Height - m.textarea.Height() - lipgloss.Height(gap)

		if len(m.messages) > 0 {
			// Wrap content before setting it.
			m.viewport.SetContent(lipgloss.NewStyle().Width(m.viewport.Width).Render(strings.Join(m.messages, "\n")))
		}
		m.viewport.GotoBottom()
	case tea.KeyMsg:
		switch msg.Type {
		case tea.KeyCtrlC, tea.KeyEsc:
			fmt.Println(m.textarea.Value())
			return m, tea.Quit
		case tea.KeyEnter:
			newMsg := m.textarea.Value()
			m.messages = append(m.messages, m.senderStyle.Render("You: ")+newMsg)
			m.viewport.SetContent(lipgloss.NewStyle().Width(m.viewport.Width).Render(strings.Join(m.messages, "\n")))
			m.textarea.Reset()
			m.viewport.GotoBottom()

			return m, sendMessageCmd(m.client, newMsg)
		}
	case chatMsg:
		m.messages = append(m.messages, m.senderStyle.Render(msg.Sender+": ")+msg.Content)
		m.viewport.SetContent(lipgloss.NewStyle().Width(m.viewport.Width).Render(strings.Join(m.messages, "\n")))
		m.textarea.Reset()
		m.viewport.GotoBottom()
		return m, listenForMessages(m.receivedMsg) // continue listening

	// We handle errors just like any other message
	case errMsg:
		m.err = msg
		return m, nil
	}

	return m, tea.Batch(tiCmd, vpCmd)
}

func (m chatModel) View() string {
	return fmt.Sprintf(
		"%s%s%s",
		m.viewport.View(),
		gap,
		m.textarea.View(),
	)
}

func NewTCPClient(serverAddress string) (*tcp.TcpInterface, error) {
	conn, err := net.Dial("tcp", serverAddress)
	if err != nil {
		return nil, fmt.Errorf("failed connecting: %w", err)
	}
	slog.Info("Connected to Server", "address", conn.RemoteAddr())

	return &tcp.TcpInterface{TcpConn: conn, Id: conn.LocalAddr().String()}, nil
}

func run() error {
	var host string
	var port int

	flag.StringVar(&host, "host", "localhost", "Set server address")
	flag.IntVar(&port, "port", 8080, "Set server port")
	flag.Parse()

	address := host + ":" + strconv.Itoa(port)

	receivedMsg := make(chan tcp.ChatMessage)

	client, err := NewTCPClient(address)
	if err != nil {
		return err
	}

	go client.TcpReceive(receivedMsg)

	p := tea.NewProgram(initialModel(receivedMsg, *client))
	if _, err := p.Run(); err != nil {
		fmt.Printf("Bad news, there's been an error: %v", err)
		os.Exit(1)
	}

	return nil
}

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "Error:", err)
		os.Exit(1)
	}
}
