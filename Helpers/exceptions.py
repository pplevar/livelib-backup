"""Custom exception hierarchy for livelib-backup"""


class LivelibError(Exception):
    """Base exception for livelib-backup"""
    pass


class NetworkError(LivelibError):
    """Network/connection related errors"""
    pass


class ParsingError(LivelibError):
    """HTML parsing errors"""
    pass


class UserNotFoundError(LivelibError):
    """User profile not found"""
    pass
