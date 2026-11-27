"""Tests for the HunterBTT Android 6.1.49 FF81 codec."""

import unittest

from hunter_btt.protocol.ff81 import (
    build_ff81_payload,
    decrypt_stream,
    encrypt_stream,
    parse_ff81_payload,
)

CAPTURED_CLIENT_ID = bytes.fromhex("C8 7A 76 C4 AA 52")
CAPTURED_PLAINTEXT = bytes.fromhex("00 00 00 00 C8 7A 76 C4 AA 52")
CAPTURED_CIPHERTEXT = bytes.fromhex("B7 B7 B7 B7 F1 64 04 91 E2 25")
CAPTURED_KEY = b"x47"
CAPTURED_PAYLOAD = bytes.fromhex(
    "B7 B7 B7 B7 F1 64 04 91 E2 25 00 78 34 37"
)


class FF81CodecTests(unittest.TestCase):
    def test_android_6149_capture_vector_matches_byte_for_byte(self):
        self.assertEqual(
            build_ff81_payload(
                "0000",
                CAPTURED_CLIENT_ID,
                random_key="x47",
                is_set=False,
            ),
            CAPTURED_PAYLOAD,
        )

    def test_capture_vector_decrypts_to_passcode_and_ffa5_client_id(self):
        decoded = parse_ff81_payload(CAPTURED_PAYLOAD)
        self.assertEqual(decoded.passcode, "0000")
        self.assertEqual(decoded.client_id, CAPTURED_CLIENT_ID)
        self.assertFalse(decoded.is_set)
        self.assertEqual(decoded.random_key, "x47")

    def test_configured_passcode_is_encoded_as_four_numeric_bytes(self):
        payload = build_ff81_payload(
            "1234",
            CAPTURED_CLIENT_ID,
            random_key="x47",
        )
        decoded = parse_ff81_payload(payload)
        self.assertEqual(decoded.passcode, "1234")
        self.assertEqual(
            decrypt_stream(payload[:10], b"x47")[:4],
            bytes((1, 2, 3, 4)),
        )

    def test_encrypt_and_decrypt_are_inverse_for_multiple_payloads(self):
        for payload in (
            CAPTURED_PLAINTEXT,
            bytes(range(10)),
            bytes.fromhex("09 08 07 06 01 23 45 67 89 ab"),
        ):
            with self.subTest(payload=payload.hex()):
                encrypted = encrypt_stream(payload, CAPTURED_KEY)
                self.assertEqual(decrypt_stream(encrypted, CAPTURED_KEY), payload)

    def test_rejects_non_four_digit_passcode(self):
        for passcode in ("", "123", "12345", "12a4", "１２３４"):
            with self.subTest(passcode=passcode):
                with self.assertRaises(ValueError):
                    build_ff81_payload(passcode, CAPTURED_CLIENT_ID, random_key="x47")

    def test_rejects_invalid_client_id(self):
        for client_id in (b"", b"12345", b"1234567", bytes(6)):
            with self.subTest(client_id=client_id):
                with self.assertRaises(ValueError):
                    build_ff81_payload("0000", client_id, random_key="x47")

    def test_rejects_invalid_random_key(self):
        for key in ("xy", "xyzz", "X47", "x-7", "é47"):
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    build_ff81_payload("0000", CAPTURED_CLIENT_ID, random_key=key)

    def test_rejects_invalid_payload_length_and_flag(self):
        with self.assertRaises(ValueError):
            parse_ff81_payload(CAPTURED_PAYLOAD[:-1])
        malformed = bytearray(CAPTURED_PAYLOAD)
        malformed[10] = 2
        with self.assertRaises(ValueError):
            parse_ff81_payload(malformed)


if __name__ == "__main__":
    unittest.main()
