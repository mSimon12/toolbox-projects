package main

import (
	"errors"
	"flag"
	"fmt"
	"log/slog"
	"os"
	"strings"
	"time"
)

const size1GB float64 = 1073741824

func getSystemMetrics(outputFile string) {
	var metricsLogger *slog.Logger
	if outputFile == "" {
		metricsLogger = GetLogger(false, outputFile)
	} else {
		if !strings.HasSuffix(outputFile, ".log") {
			outputFile = outputFile + ".log"
		}
		metricsLogger = GetLogger(true, outputFile)
	}

	// CPU
	cpuReport, _ := getCpuUsage(3)
	fields := []interface{}{
		"total", fmt.Sprintf("%.2f%%", cpuReport.total),
	}

	for idx, core := range cpuReport.cores {
		key := fmt.Sprintf("core%d", idx+1)
		value := fmt.Sprintf("%.2f%%", core)
		fields = append(fields, key, value)
	}
	metricsLogger.Info("CPU", fields...)

	// Memory
	memReport, _ := getMemoryUsage()
	metricsLogger.Info("Memory",
		"total", fmt.Sprintf("%.2f GB", float64(memReport.total)/size1GB),
		"free", fmt.Sprintf("%.2f GB", float64(memReport.free)/size1GB),
		"used", fmt.Sprintf("%.2f GB", float64(memReport.used)/size1GB),
		"percent", fmt.Sprintf("%.2f%%", memReport.percent),
	)

	// Disk
	diskReport, _ := getDiskUsage()
	metricsLogger.Info("Disk",
		"total", fmt.Sprintf("%.2f GB", float64(diskReport.total)/size1GB),
		"free", fmt.Sprintf("%.2f GB", float64(diskReport.free)/size1GB),
		"used", fmt.Sprintf("%.2f GB", float64(diskReport.used)/size1GB),
		"percent", fmt.Sprintf("%.2f%%", diskReport.percent),
	)
}

func metricsCycle(interval int, outputFile string) {
	count := 0
	for count < 2 {
		getSystemMetrics(outputFile)
		time.Sleep(time.Duration(interval))
		count++
	}

}

func run() error {
	var interval int
	var outputFile string

	flag.IntVar(&interval, "interval", 5, "Interval (s) between metrics measurements.")
	flag.StringVar(&outputFile, "outputFile", "", "Name of the file to save the output [Empty = cmd output].")
	flag.Parse()

	if interval < 1 {
		return errors.New("invalid interval: must be > 0")
	}
	metricsCycle(interval, outputFile)
	return nil
}

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "Error:", err)
		os.Exit(1)
	}
}
