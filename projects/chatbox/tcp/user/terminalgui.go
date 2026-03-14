package main

import (
	"fmt"
	"strings"
	"tcpchat/transport"

	"github.com/charmbracelet/bubbles/textarea"
	"github.com/charmbracelet/bubbles/viewport"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

const gap = "\n\n"

type (
	errMsg error
)

type chatMsg transport.ChatMessage

// chatModel defines the state of the chat application
type chatModel struct {
	viewport    viewport.Model //Messages area
	messages    []string
	textarea    textarea.Model //Area for writing messages
	senderStyle lipgloss.Style
	receivedMsg <-chan transport.ChatMessage // channel for new messages
	transport   transport.TransportNode
	err         error
}

// listenForMessages creates a command that waits for a message from the provided channel
func listenForMessages(ch <-chan transport.ChatMessage) tea.Cmd {
	return func() tea.Msg {
		msg := <-ch
		return chatMsg(msg)
	}
}

// sendMessageCmd creates a command to send a message through the transport node
func sendMessageCmd(client transport.TransportNode, msg string) tea.Cmd {
	chatMsg := transport.ChatMessage{
		Sender:  client.NodeId,
		Content: msg,
	}

	return func() tea.Msg {
		if err := client.TcpSend(chatMsg); err != nil {
			return errMsg(err) // Bubbletea will handle this like other errors
		}
		return nil
	}
}

// initialModel sets up the initial state of the chat application
func initialModel(client *ChatClient) chatModel {
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
		receivedMsg: client.msgCh,
		transport:   client.transport,
		err:         nil,
	}
}

// Init is the initial command for the Bubbletea program
func (m chatModel) Init() tea.Cmd {
	return listenForMessages(m.receivedMsg)
}

// Update handles incoming messages and updates the model accordingly
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

			return m, sendMessageCmd(m.transport, newMsg)
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

// View renders the UI
func (m chatModel) View() string {
	return fmt.Sprintf(
		"%s%s%s",
		m.viewport.View(),
		gap,
		m.textarea.View(),
	)
}

// executeGUI runs the Bubbletea program with the provided ChatClient
func executeGUI(client *ChatClient) error {
	p := tea.NewProgram(initialModel(client))
	if _, err := p.Run(); err != nil {
		return fmt.Errorf("failed running program: %w", err)
	}
	return nil
}
