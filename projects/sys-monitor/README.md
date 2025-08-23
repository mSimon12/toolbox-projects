# 🖥️ System Resource Monitor

Idea: A lightweight command-line tool that periodically checks system usage (CPU, memory, disk) and prints/logs it.
This is similar to top or htop, but much simpler.

## Why it’s good in Go:

Go is fast, so you can run it as a daemon or background service.

Easy to build as a single binary and run anywhere.

Great way to show you can integrate with system APIs via libraries.

## Tech details:

Use ``gopsutil`` (well-known Go library for system stats).

Use goroutines for periodic checks (time.Ticker).

Configurable refresh interval and output format (console vs log file).

## Example features:

``--interval 5s`` → sample every 5 seconds.

``--log usage.log`` → save output to a file.

``-format json`` → JSON or plain text output.

# 🖥️ System Resource Monitor (Go)

A lightweight CLI tool written in Go to monitor your system’s CPU, memory, and disk usage in real time. Logs are emitted in structured JSON, ready for ingestion into Elasticsearch, Kibana, or any log pipeline.

## 🚀 Features

- Monitor CPU usage, memory usage, and disk usage
- JSON logs with ISO8601 timestamps (@timestamp)
- Fully single-binary Go program — no dependencies, just run it anywhere
- Logs include source info for better traceability
- Easy to extend for more system metrics

## ⚡ Installation

```bash
git clone https://github.com/yourusername/sysmonitor.git
cd sysmonitor
go build -o sysmonitor main.go
```

This creates a standalone sysmonitor binary.


## 🏃 Usage

Run the tool from your terminal:

```bash
./sysmonitor
```

It prints system metrics every few seconds in structured JSON.

**Example Output:**
```
{
  "@timestamp": "2025-08-22T18:10:43.123Z",
  "log.level": "INFO",
  "message": "CPU usage collected",
  "cpu_pct": 42.1,
  "mem_pct": 63.4,
  "disk_pct": 57.8,
  "log.origin.file.name": "main.go",
  "log.origin.file.line": 34,
  "log.origin.function": "main.main"
}
```
