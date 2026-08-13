"""First-generation Hunter protocol framing."""

from __future__ import annotations

from dataclasses import dataclass


class FirstProtocolError(ValueError):
    """Invalid First-generation protocol data."""


@dataclass(frozen=True, slots=True)
class FirstFrame:
    """Decoded FirstProtocol frame."""

    header: int
    payload: bytes


def encode_frame(header: int, payload: bytes) -> bytes:
    """Encode [header][payload length][payload]."""

    if not 0 <= header <= 0xFF:
        raise FirstProtocolError("header must be in range 0..255")

    if len(payload) > 0xFF:
        raise FirstProtocolError("payload is too long")

    return bytes((header, len(payload))) + payload


def decode_frame(data: bytes) -> FirstFrame:
    """Decode a FirstProtocol frame."""

    if len(data) < 2:
        raise FirstProtocolError("frame requires header and length")

    length = data[1]

    if len(data) < 2 + length:
        raise FirstProtocolError(
            f"truncated frame: expected {length} payload bytes"
        )

    return FirstFrame(
        header=data[0],
        payload=bytes(data[2 : 2 + length]),
    )


def encode_u16(value: int) -> bytes:
    """Encode a First-generation unsigned 16-bit value."""

    if not 0 <= value <= 0xFFFF:
        raise FirstProtocolError("u16 value out of range")

    return value.to_bytes(2, "little")


def decode_u16(payload: bytes, offset: int = 0) -> int:
    """Decode a First-generation unsigned 16-bit value."""

    if len(payload) < offset + 2:
        raise FirstProtocolError("not enough bytes for u16")

    return int.from_bytes(
        payload[offset : offset + 2],
        "little",
    )
