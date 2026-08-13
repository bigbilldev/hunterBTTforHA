"""First-generation Hunter BTT protocol."""

from .base import (
    FirstFrame,
    FirstProtocolError,
    decode_frame,
    decode_u16,
    encode_frame,
    encode_u16,
)
from .commands import (
    FirstWrite,
    build_manual_start,
    build_manual_stop,
)
from .protocols import FirstC3, FirstD9, FirstEB

__all__ = (
    "FirstC3",
    "FirstD9",
    "FirstEB",
    "FirstFrame",
    "FirstProtocolError",
    "FirstWrite",
    "build_manual_start",
    "build_manual_stop",
    "decode_frame",
    "decode_u16",
    "encode_frame",
    "encode_u16",
)
