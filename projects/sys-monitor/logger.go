package main

import (
	"log/slog"
	"os"
	"time"
)

var logHandler *slog.JSONHandler = nil

func loggerECSFormat(groups []string, att slog.Attr) slog.Attr {
	switch att.Key {
	case slog.TimeKey:
		// Format time to ISO8601 with millis
		if t, ok := att.Value.Any().(time.Time); ok {
			att.Value = slog.StringValue(t.Format("2006-01-02 15:04:05"))
		}
	}
	return att
}

func GetLogger(logToFile bool, loggerFilename string) *slog.Logger {
	if logHandler == nil { // open only once

		logOptions := &slog.HandlerOptions{
			AddSource:   false,
			Level:       slog.LevelDebug,
			ReplaceAttr: loggerECSFormat,
		}

		if logToFile {
			logFile, err := os.OpenFile(loggerFilename, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
			if err != nil {
				panic("failed to open log file: " + err.Error())
			}
			logHandler = slog.NewJSONHandler(logFile, logOptions)
		} else {
			logHandler = slog.NewJSONHandler(os.Stdout, logOptions)
		}
	}

	newLogger := slog.New(logHandler)

	return newLogger
}
