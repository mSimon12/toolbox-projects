package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"log/slog"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"
)

const size1GB float64 = 1073741824

func formatOutputFile(filename string) string {
	if !strings.HasSuffix(filename, ".log") {
		filename = filename + ".log"
	}
	return filename
}

func logCpuUsage(logger *slog.Logger, usageReport cpuUsage) {
	fields := []interface{}{
		"total", fmt.Sprintf("%.2f%%", usageReport.total),
	}

	for idx, core := range usageReport.cores {
		key := fmt.Sprintf("core%d", idx+1)
		value := fmt.Sprintf("%.2f%%", core)
		fields = append(fields, key, value)
	}
	logger.Info("CPU", fields...)
}

func logCommonUsage(logger *slog.Logger, message string, usageReport Usage) {
	logger.Info(message,
		"total", fmt.Sprintf("%.2f GB", float64(usageReport.total)/size1GB),
		"free", fmt.Sprintf("%.2f GB", float64(usageReport.free)/size1GB),
		"used", fmt.Sprintf("%.2f GB", float64(usageReport.used)/size1GB),
		"percent", fmt.Sprintf("%.2f%%", usageReport.percent),
	)
}

func getSystemMetrics() (cpuUsage, Usage, Usage) {
	cpuReport, _ := getCpuUsage(3)
	memReport, _ := getMemoryUsage()
	diskReport, _ := getDiskUsage()

	return cpuReport, memReport, diskReport
}

func metricsCycle(ctx context.Context, logger *slog.Logger, interval int) {
	count := 0
	ticker := time.NewTicker(time.Duration(interval) * time.Second)
	for {

		select {
		case <-ticker.C:
			cpu, memory, disk := getSystemMetrics()
			logCpuUsage(logger, cpu)
			logCommonUsage(logger, "Memory", memory)
			logCommonUsage(logger, "Disk", disk)
		case <-ctx.Done():
			fmt.Println("stopping PeriodicTask")
			ticker.Stop()
			return
		}

		time.Sleep(time.Duration(interval) * time.Second)
		count++
	}
}

func run() error {
	var interval int
	var outputFile string
	ctx := context.Background()

	flag.IntVar(&interval, "interval", 5, "Interval (s) between metrics measurements.")
	flag.StringVar(&outputFile, "outputFile", "", "Name of the file to save the output [Empty = cmd output].")
	flag.Parse()

	if interval < 1 {
		return errors.New("invalid interval: must be > 0")
	}

	metricsLogger := GetLogger(outputFile != "", formatOutputFile(outputFile))
	go metricsCycle(ctx, metricsLogger, interval)

	// Create a channel to receive signals from the operating system.
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGTERM)

	// The code blocks until a signal is received (e.g. Ctrl+C).
	<-sigCh

	return nil
}

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "Error:", err)
		os.Exit(1)
	}
}
