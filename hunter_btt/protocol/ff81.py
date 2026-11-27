"""HunterBTT Android 6.1.49 FF81 initialization codec.

The captured FF81 value is:
    B7 B7 B7 B7 F1 64 04 91 E2 25 00 78 34 37

It consists of ten encrypted bytes, a one-byte isSet flag, and a
three-character random key. The encrypted plaintext is four numeric
passcode bytes followed by the six-byte client ID read from FFA5.
"""

from __future__ import annotations

import secrets
import string
from dataclasses import dataclass

FF81_PLAINTEXT_LENGTH = 10
FF81_PAYLOAD_LENGTH = 14
FF81_RANDOM_KEY_LENGTH = 3
_RANDOM_ALPHABET = string.ascii_lowercase + string.digits


@dataclass(frozen=True, slots=True)
class FF81Decoded:
    """Decoded FF81 payload fields."""

    passcode: str
    client_id: bytes
    is_set: bool
    random_key: str


def _validate_key(key: bytes) -> bytes:
    """Validate the three-byte ASCII key used by the Android formatter."""
    value = bytes(key)
    if len(value) != FF81_RANDOM_KEY_LENGTH:
        raise ValueError("FF81 random key must contain exactly three bytes.")
    try:
        text = value.decode("ascii")
    except UnicodeDecodeError as err:
        raise ValueError("FF81 random key must be ASCII.") from err
    if any(character not in _RANDOM_ALPHABET for character in text):
        raise ValueError("FF81 random key must use lowercase ASCII letters or digits.")
    return value


def _rotate_left(value: int, amount: int) -> int:
    amount %= 8
    if amount == 0:
        return value & 0xFF
    return ((value << amount) | (value >> (8 - amount))) & 0xFF


def _rotate_right(value: int, amount: int) -> int:
    amount %= 8
    if amount == 0:
        return value & 0xFF
    return ((value >> amount) | (value << (8 - amount))) & 0xFF


def encrypt_stream(data: bytes, key: bytes) -> bytes:
    """Apply the Android 6.1.49 three-round XOR/bit-rotation transform."""
    source = bytes(data)
    key_bytes = _validate_key(key)
    result = bytearray(len(source))

    for round_index, key_byte in enumerate(key_bytes):
        shift = key_bytes[len(key_bytes) - round_index - 1] % 8
        for offset in range(len(source)):
            value = source[offset] if round_index == 0 else result[offset]
            value ^= key_byte
            if round_index % 2 == 0:
                value = _rotate_left(value, shift)
            else:
                value = _rotate_right(value, shift)
            result[offset] = value

    return bytes(result)


def decrypt_stream(data: bytes, key: bytes) -> bytes:
    """Reverse the Android 6.1.49 three-round XOR/bit-rotation transform."""
    source = bytes(data)
    key_bytes = _validate_key(key)
    result = bytearray(len(source))

    for round_index in range(len(key_bytes) - 1, -1, -1):
        shift = key_bytes[len(key_bytes) - round_index - 1] % 8
        for offset in range(len(source)):
            value = (
                source[offset]
                if round_index == len(key_bytes) - 1
                else result[offset]
            )
            if round_index % 2 == 0:
                value = _rotate_right(value, shift)
            else:
                value = _rotate_left(value, shift)
            result[offset] = value ^ key_bytes[round_index]

    return bytes(result)


def _passcode_bytes(passcode: str) -> bytes:
    """Convert the configured four decimal passcode digits to numeric bytes."""
    if (
        not isinstance(passcode, str)
        or len(passcode) != 4
        or not passcode.isascii()
        or not passcode.isdigit()
    ):
        raise ValueError("Hunter BTT passcode must be exactly four ASCII digits.")
    return bytes(int(character) for character in passcode)


def _random_key() -> bytes:
    return "".join(
        secrets.choice(_RANDOM_ALPHABET)
        for _ in range(FF81_RANDOM_KEY_LENGTH)
    ).encode("ascii")


def build_ff81_payload(
    passcode: str,
    client_id: bytes,
    *,
    random_key: str | bytes | None = None,
    is_set: bool = False,
) -> bytes:
    """Build the 14-byte FF81 value used by HunterBTT Android 6.1.49."""
    client_id_bytes = bytes(client_id)
    if len(client_id_bytes) != 6:
        raise ValueError(
            f"FFA5 client ID must be exactly six bytes; received {len(client_id_bytes)}."
        )
    if not any(client_id_bytes):
        raise ValueError("FFA5 client ID is all zeroes; refusing an uninitialized ID.")
    if not isinstance(is_set, bool):
        raise ValueError("FF81 is_set must be a boolean.")

    key = (
        _random_key()
        if random_key is None
        else random_key.encode("ascii") if isinstance(random_key, str)
        else bytes(random_key)
    )
    key = _validate_key(key)
    plaintext = _passcode_bytes(passcode) + client_id_bytes
    encrypted = encrypt_stream(plaintext, key)
    return encrypted + bytes((int(is_set),)) + key


def parse_ff81_payload(payload: bytes) -> FF81Decoded:
    """Decode an Android 6.1.49 FF81 value for diagnostics and regression tests."""
    value = bytes(payload)
    if len(value) != FF81_PAYLOAD_LENGTH:
        raise ValueError(
            f"FF81 payload must be exactly {FF81_PAYLOAD_LENGTH} bytes; received {len(value)}."
        )

    encrypted = value[:FF81_PLAINTEXT_LENGTH]
    is_set_byte = value[FF81_PLAINTEXT_LENGTH]
    if is_set_byte not in (0, 1):
        raise ValueError(f"FF81 isSet byte must be 0 or 1; received {is_set_byte}.")

    key = _validate_key(value[FF81_PLAINTEXT_LENGTH + 1 :])
    plaintext = decrypt_stream(encrypted, key)
    digits = plaintext[:4]
    if any(digit > 9 for digit in digits):
        raise ValueError("Decrypted FF81 passcode bytes are not decimal digits.")

    return FF81Decoded(
        passcode="".join(str(digit) for digit in digits),
        client_id=plaintext[4:],
        is_set=bool(is_set_byte),
        random_key=key.decode("ascii"),
    )
