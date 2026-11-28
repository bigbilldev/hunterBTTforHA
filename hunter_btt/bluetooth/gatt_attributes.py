"""Recover characteristics hidden in malformed Bleak descriptor groupings.

Some ESPHome/Bleak GATT inventories place subsequent 0x2803 declaration
attributes and their value attributes in the preceding characteristic's
descriptor list. This module only identifies candidates; it never guesses
characteristic properties or authorizes a protocol write.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID


CHARACTERISTIC_DECLARATION_UUID = "00002803-0000-1000-8000-00805f9b34fb"
CLIENT_CONFIGURATION_UUID = "00002902-0000-1000-8000-00805f9b34fb"

_PROPERTY_BITS = (
    (0x01, "broadcast"),
    (0x02, "read"),
    (0x04, "write-without-response"),
    (0x08, "write"),
    (0x10, "notify"),
    (0x20, "indicate"),
    (0x40, "authenticated-signed-writes"),
    (0x80, "extended-properties"),
)


@dataclass(frozen=True)
class MisclassifiedCharacteristic:
    """A declaration/value pair represented as descriptors by Bleak."""

    service: Any
    declaration: Any
    value_attribute: Any
    cccd: Any | None


@dataclass(frozen=True)
class ParsedCharacteristicDeclaration:
    """The characteristic properties and value handle from a 0x2803 value."""

    properties: tuple[str, ...]
    value_handle: int
    uuid: str


def find_misclassified_characteristic(
    services: Any,
    target_uuid: str,
) -> MisclassifiedCharacteristic | None:
    """Find 0x2803 followed by the requested characteristic value attribute."""
    target = str(target_uuid).strip().lower()
    for service in services:
        attributes = []
        for characteristic in service.characteristics:
            attributes.extend(
                (descriptor, characteristic)
                for descriptor in (getattr(characteristic, "descriptors", ()) or ())
                if isinstance(getattr(descriptor, "handle", None), int)
            )
        attributes.sort(key=lambda item: item[0].handle)

        for index, (attribute, _parent) in enumerate(attributes):
            if str(attribute.uuid).strip().lower() != CHARACTERISTIC_DECLARATION_UUID:
                continue
            if index + 1 >= len(attributes):
                continue
            value_attribute, _value_parent = attributes[index + 1]
            if (
                value_attribute.handle != attribute.handle + 1
                or str(value_attribute.uuid).strip().lower() != target
            ):
                continue

            cccd = None
            if index + 2 < len(attributes):
                possible_cccd, _cccd_parent = attributes[index + 2]
                if (
                    possible_cccd.handle == value_attribute.handle + 1
                    and str(possible_cccd.uuid).strip().lower()
                    == CLIENT_CONFIGURATION_UUID
                ):
                    cccd = possible_cccd

            return MisclassifiedCharacteristic(
                service=service,
                declaration=attribute,
                value_attribute=value_attribute,
                cccd=cccd,
            )
    return None


def parse_characteristic_declaration(
    payload: bytes,
    expected_uuid: str,
) -> ParsedCharacteristicDeclaration:
    """Decode a 128-bit UUID GATT characteristic declaration value.

    The ATT declaration value is: properties (1), value handle (2 LE), UUID
    (16 bytes in Bluetooth little-endian UUID order).
    """
    raw = bytes(payload)
    if len(raw) != 19:
        raise ValueError(
            f"128-bit characteristic declaration must be 19 bytes; got {len(raw)}"
        )

    properties_byte = raw[0]
    value_handle = int.from_bytes(raw[1:3], "little")
    characteristic_uuid = str(UUID(bytes_le=raw[3:19]))
    expected = str(expected_uuid).strip().lower()

    if characteristic_uuid.lower() != expected:
        raise ValueError(
            f"declaration UUID {characteristic_uuid} does not match {expected}"
        )
    if value_handle <= 0:
        raise ValueError(f"invalid characteristic value handle {value_handle}")

    properties = tuple(
        name for bit, name in _PROPERTY_BITS if properties_byte & bit
    )
    return ParsedCharacteristicDeclaration(
        properties=properties,
        value_handle=value_handle,
        uuid=characteristic_uuid,
    )
