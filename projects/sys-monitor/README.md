# 🖥️ System Resource Monitor (Go)

A lightweight CLI tool written in Go to monitor your system’s CPU, memory, and disk usage in real time. Logs are emitted in structured JSON, and can be output to cmd or to a .log file.

---
## ⚡ Setup

```bash
git clone https://github.com/mSimon12/toolbox-projects.git
cd projects/sys-monitor
go build -o sys-monitor .
```

This creates a standalone ``sys-monitor`` binary.

---
## 🏃 Usage

The app will print system metrics every few seconds in structured JSON. The output format is defined by the parameters added to the terminal command ``./sys-monitor``. It allows configuration of metrics interval and output format (console vs log file).

``--interval 5s`` → sample every 5 seconds.
``--outputFile usage`` → save output to a file **'usage.log'**.

> [!WARNING]  
> The scripts runs on an infinite loop until Ctrl + C is executed.


**Example 1:** 
``./sys-monitor -interval 2``

Output: **terminal**
```bash
{"time":"2025-08-25 22:01:19","level":"INFO","msg":"CPU","total":"23.56%","core1":"5.78%","core2":"6.44%","core3":"5.07%","core4":"4.73%"}
{"time":"2025-08-25 22:01:19","level":"INFO","msg":"Memory","total":"7.54 GB","free":"0.61 GB","used":"4.17 GB","percent":"55.31%"}
{"time":"2025-08-25 22:01:19","level":"INFO","msg":"Disk","total":"915.32 GB","free":"370.19 GB","used":"498.57 GB","percent":"57.39%"}
{"time":"2025-08-25 22:01:27","level":"INFO","msg":"CPU","total":"5.91%","core1":"5.41%","core2":"4.45%","core3":"4.35%","core4":"4.71%"}
{"time":"2025-08-25 22:01:27","level":"INFO","msg":"Memory","total":"7.54 GB","free":"0.63 GB","used":"4.16 GB","percent":"55.16%"}
{"time":"2025-08-25 22:01:27","level":"INFO","msg":"Disk","total":"915.32 GB","free":"370.19 GB","used":"498.57 GB","percent":"57.39%"}
```

**Example 2:** 
``go run . -interval 5 -outputFile metrics``

Output: **metrics.log**
```log
{"time":"2025-08-25 22:04:30","level":"INFO","msg":"CPU","total":"34.70%","core1":"31.99%","core2":"29.35%","core3":"29.25%","core4":"29.93%"}
{"time":"2025-08-25 22:04:30","level":"INFO","msg":"Memory","total":"7.54 GB","free":"0.56 GB","used":"4.22 GB","percent":"55.95%"}
{"time":"2025-08-25 22:04:30","level":"INFO","msg":"Disk","total":"915.32 GB","free":"370.19 GB","used":"498.57 GB","percent":"57.39%"}
{"time":"2025-08-25 22:04:41","level":"INFO","msg":"CPU","total":"19.59%","core1":"35.00%","core2":"37.07%","core3":"34.01%","core4":"37.29%"}
{"time":"2025-08-25 22:04:41","level":"INFO","msg":"Memory","total":"7.54 GB","free":"0.42 GB","used":"4.20 GB","percent":"55.69%"}
{"time":"2025-08-25 22:04:41","level":"INFO","msg":"Disk","total":"915.32 GB","free":"370.19 GB","used":"498.57 GB","percent":"57.39%"}
```