package main

import (
	"errors"
	"flag"
	"fmt"
	"os"
	"time"
)

func getSystemMetrics(outputType string, outputFile string) {
	metricsLogger := GetLogger("metrics")

	// cpuInfo()

	cpuReport, _ := getCpuUsage(3)
	metricsLogger.Info(fmt.Sprintf("CPU: %v", cpuReport))

	memReport, _ := getMemoryUsage()
	metricsLogger.Info(fmt.Sprintf("Memory: %v", memReport))

	diskReport, _ := getDiskUsage()
	metricsLogger.Info(fmt.Sprintf("Disk: %v", diskReport))
}

func metricsCycle(interval int, outputType string, outputFile string) {
	count := 0
	for count < 10 {
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
