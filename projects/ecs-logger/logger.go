package main

import (
	"log/slog"
	"os"
	"path/filepath"
	"time"
)

var logHandler *slog.JSONHandler = nil

func loggerECSFormat(groups []string, att slog.Attr) slog.Attr {
	switch att.Key {
	case slog.TimeKey:
		att.Key = "@timestamp"
		// Format time to ISO8601 with millis
		if t, ok := att.Value.Any().(time.Time); ok {
			att.Value = slog.StringValue(t.UTC().Format("2006-01-02T15:04:05.000Z07:00"))
		}
	case slog.LevelKey:
		att.Key = "log.level"
	case slog.MessageKey:
		att.Key = "message"
	case slog.SourceKey:
		// Expand source into ECS fields
		if src, ok := att.Value.Any().(*slog.Source); ok {
			return slog.Group("",
				slog.String("log.origin.file.name", filepath.Base(src.File)),
				slog.Int("log.origin.file.line", src.Line),
				slog.String("log.origin.function", src.Function),
			)
		}
	}
	return att
}

func createLogger() {
	logOptions := &slog.HandlerOptions{
		AddSource:   false,
		Level:       slog.LevelDebug,
		ReplaceAttr: loggerECSFormat,
	}

	logHandler = slog.NewJSONHandler(os.Stderr, logOptions)

}

func GetLogger(loggerName string) *slog.Logger {
	if logHandler == nil {
		createLogger()
	}

	newLogger := slog.New(logHandler)

	if loggerName != "" {
		newLogger = newLogger.With("log.logger", loggerName)
	}

	return newLogger
}
