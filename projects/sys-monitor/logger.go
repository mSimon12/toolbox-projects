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

func GetLogger(loggerFilename string) *slog.Logger {
	logOptions := &slog.HandlerOptions{
		AddSource:   false,
		Level:       slog.LevelDebug,
		ReplaceAttr: loggerECSFormat,
	}

	logHandler = slog.NewJSONHandler(os.Stderr, logOptions)

	newLogger := slog.New(logHandler)

	return newLogger
}
