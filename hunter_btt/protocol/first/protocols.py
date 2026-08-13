"""First-generation protocol objects used for manual watering."""

from __future__ import annotations

from dataclasses import dataclass

from .base import decode_u16, encode_frame, encode_u16


@dataclass(slots=True)
class FirstC3:
    """First_C3_Protocol."""

    select_mode: int = 0
    HEADER = 0x53

    @classmethod
    def from_payload(cls, payload: bytes) -> "FirstC3":
        if not payload:
            raise ValueError("First_C3 payload is empty")
        return cls(payload[0])

    def to_frame(self) -> bytes:
        return encode_frame(
            self.HEADER,
            bytes((self.select_mode & 0xFF,)),
        )


@dataclass(slots=True)
class FirstD9:
    """First_D9_Protocol."""

    control: int = 0
    minute: int = 0
    HEADER = 0x69

    @classmethod
    def from_payload(cls, payload: bytes) -> "FirstD9":
        if not payload:
            raise ValueError("First_D9 payload is empty")
        return cls(
            control=payload[0],
            minute=decode_u16(payload, 1) if len(payload) >= 3 else 0,
        )

    def to_frame(self) -> bytes:
        return encode_frame(
            self.HEADER,
            bytes((self.control & 0xFF,)) + encode_u16(self.minute),
        )


@dataclass(slots=True)
class FirstEB:
    """First_EB_Protocol."""

    control: int = 0
    minute: int = 0
    HEADER = 0x7B

    @classmethod
    def from_payload(cls, payload: bytes) -> "FirstEB":
        if not payload:
            raise ValueError("First_EB payload is empty")
        return cls(
            control=payload[0],
            minute=decode_u16(payload, 1) if len(payload) >= 3 else 0,
        )

    def to_frame(self) -> bytes:
        return encode_frame(
            self.HEADER,
            bytes((self.control & 0xFF,)) + encode_u16(self.minute),
        )
