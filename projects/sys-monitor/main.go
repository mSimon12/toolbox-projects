package main

import "fmt"

func main() {

	myLogger := GetLogger("main")

	// cpuInfo()

	cpuReport, _ := getCpuUsage(3)
	myLogger.Info(fmt.Sprintf("CPU: %v", cpuReport))

	memReport, _ := getMemoryUsage()
	myLogger.Info(fmt.Sprintf("Memory: %v", memReport))

	diskReport, _ := getDiskUsage()
	myLogger.Info(fmt.Sprintf("Disk: %v", diskReport))
}
