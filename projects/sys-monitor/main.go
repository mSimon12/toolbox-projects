package main

import (
	"errors"
	"flag"
	"fmt"
	"os"
	"time"
)

const size1GB float64 = 1073741824

func getSystemMetrics(outputType string, outputFile string) {
	metricsLogger := GetLogger(outputFile)

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

func metricsCycle(interval int, outputType string, outputFile string) {
	count := 0
	for count < 2 {
		getSystemMetrics(outputType, outputFile)
		time.Sleep(time.Duration(interval))
		count++
	}

}

func run() error {
	var interval int
	var outputFile string
	var outputType string

	flag.IntVar(&interval, "interval", 5, "Interval (s) between metrics measurements.")
	flag.StringVar(&outputType, "outputType", "file", "Select output mode [file, cmd].")
	flag.StringVar(&outputFile, "outputFile", "metrics", "Name of the file to save the output.")
	flag.Parse()

	if interval < 1 {
		return errors.New("invalid interval: must be > 0")
	}

	if !((outputType == "file") || (outputType == "cmd")) {
		return errors.New("invalid outputType: must be 'file' or 'cmd'")
	}

	metricsCycle(interval, outputType, outputFile)
	return nil
}

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "Error:", err)
		os.Exit(1)
	}
}
