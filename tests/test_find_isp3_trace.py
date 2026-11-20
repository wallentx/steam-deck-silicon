"""Synthetic controls for finding complete slots across arbitrary stream boundaries."""

import io
import struct
import unittest

from scripts.find_isp3_trace import scan


class TraceSearchTests(unittest.TestCase):
    def test_unaligned_command_and_ack_across_chunks(self):
        command = bytearray(64)
        struct.pack_into("<II", command, 0, 93, 0x02050002)
        struct.pack_into("<I", command, 16, 4728)
        command[56] = 1
        command[63] = sum(command[:63]) & 0xff
        ack = bytearray(64)
        struct.pack_into("<IIII", ack, 0, 2, 0x10001, 93, 0x02050002)
        ack[63] = sum(ack[:63]) & 0xff
        data = b"12345" + command + b"xyz" + ack
        for block in (1, 31, 63, 64, 65, 101, 65536):
            with self.subTest(block=block):
                result = scan(io.BytesIO(data), block)
                self.assertEqual(result["first_hits"], [("frame_info", 5), ("done_frame_info", 72)])
                self.assertEqual(result["counts"]["frame_info_size"], 1)
                self.assertEqual(result["counts"]["done_frame_info_checksum"], 1)

    def test_bad_checksum_and_wrong_size(self):
        data = bytearray(64)
        struct.pack_into("<I", data, 4, 0x02050002)
        struct.pack_into("<I", data, 16, 4656)
        result = scan(io.BytesIO(data))
        self.assertEqual(result["counts"], {"frame_info_id": 1, "frame_info_size": 1})
        data[16] = 0
        self.assertEqual(scan(io.BytesIO(data))["counts"], {"frame_info_id": 1})
        self.assertFalse(scan(io.BytesIO(data[:63]))["counts"])

    def test_ack_does_not_imply_command(self):
        data = bytearray(64)
        struct.pack_into("<I", data, 4, 0x10001)
        struct.pack_into("<I", data, 12, 0x02050002)
        data[-1] = sum(data[:-1]) & 0xff
        result = scan(io.BytesIO(data))
        self.assertEqual(result["counts"], {"done_frame_info_id": 1, "done_frame_info_checksum": 1})
        self.assertEqual(result["first_hits"], [("done_frame_info", 0)])


if __name__ == "__main__":
    unittest.main()
