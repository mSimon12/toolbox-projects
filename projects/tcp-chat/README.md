# 💬 Go TCP Chat

A simple TCP-based chat application written in Go that supports multiple clients connecting to a server, sending messages, and broadcasting them to all participants in real time.

---
## 🚀 Features

- 📡 Server that accepts multiple clients on a TCP port
- 👥 Clients can send and receive messages in real time
- ⚡ Built with goroutines for concurrency
- 🛑 Handles client disconnects gracefully
- 🧩 Easily extendable with commands (/nick, /msg, /quit)

---
## 📦 Setup

Clone the repository and build the binaries:

```bash
git clone https://github.com/yourusername/tcp-chat.git
cd tcp-chat
go build -o tcp-chat .
```

---
## 🏃 Usage

**Start the server:**

```bash
./tcp-chat -mode server
```

By default, it listens on port 8080.

**Connect a client:**

```bash
./tcp-chat
```

*The client connects to localhost:8080 by default.

### 💡 Example
Open multiple terminals to simulate different users.

- Terminal 1 (server):

[INFO] Server started on :8080


- Terminal 2 (client A):


Welcome to GoChat!
> hello world

- Terminal 3 (client B):
Welcome to GoChat!
> (client A): hello world

### 🔧 Configuration

- --host: set server address - default:``localhost``
- --port: set server port - default: ``8080``
- --max-clients: limit concurrent connections - default: ``50`` 

You can make host/port configurable via CLI flags:

``./tcp-chat -mode server --port 9000``
``./tcp-chat --host 127.0.0.1 --port 9000``


Commands: ``/quit`` to leave, ``/list`` to see connected users.

---
## 🛠 Improvments ideas

- [] Nickname support (/nick myname)
- [] Private messages (/msg user hi)
- [] Command help system
- [] Persistent chat history
- [] WebSocket frontend for fun