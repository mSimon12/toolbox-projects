class TimeTrackerError(Exception):
    """Base class for domain errors raised by core."""


class AlreadyClockedIn(TimeTrackerError):
    pass


class NotClockedIn(TimeTrackerError):
    pass


class EntryExistsForDay(TimeTrackerError):
    pass


class EntryNotFound(TimeTrackerError):
    pass


class InvalidTimeRange(TimeTrackerError):
    pass
