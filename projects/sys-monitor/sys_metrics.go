package main

import (
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/shirou/gopsutil/cpu"
	"github.com/shirou/gopsutil/disk"
	"github.com/shirou/gopsutil/v4/mem"
)

type cpuUsage struct {
	total float64
	cores []float64
}

type Usage struct {
	total   uint64
	used    uint64
	free    uint64
	percent float64
}

func cpuInfo() {
	infos, _ := cpu.Info()
	for _, info := range infos {
		data, _ := json.MarshalIndent(info, "", " ")
		fmt.Print(string(data))
	}

	physicalCnt, _ := cpu.Counts(false)
	logicalCnt, _ := cpu.Counts(true)
	fmt.Printf("physical count:%d logical count:%d\n", physicalCnt, logicalCnt)
}

func getCpuUsage(duration uint16) (cpuUsage, error) {

	cpuUse := cpuUsage{}

	totalPercent, err := cpu.Percent(time.Duration(duration)*time.Second, false)
	if err != nil {
		return cpuUse, err
	}
	cpuUse.total = totalPercent[0]

	perPercents, err := cpu.Percent(time.Duration(duration)*time.Second, true)
	if err != nil {
		return cpuUse, err
	}

	cpuUse.cores = append(cpuUse.cores, perPercents...)

	return cpuUse, nil
}

func getMemoryUsage() (Usage, error) {
	memUse := Usage{}

	usageStat, err := mem.VirtualMemory()
	if err != nil {
		return memUse, err
	}

	memUse.total = usageStat.Total
	memUse.used = usageStat.Used
	memUse.free = usageStat.Free
	memUse.percent = usageStat.UsedPercent

	return memUse, nil
}

func getDiskUsage() (Usage, error) {
	diskUse := Usage{}

	usageStat, err := disk.Usage("/")
	if err != nil {
		log.Fatalf("Error getting disk usage: %v", err)
	}

	diskUse.total = usageStat.Total
	diskUse.used = usageStat.Used
	diskUse.free = usageStat.Free
	diskUse.percent = usageStat.UsedPercent

	return diskUse, nil
}
