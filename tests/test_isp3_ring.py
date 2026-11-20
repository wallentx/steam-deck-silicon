"""Synthetic R64-sized packets. No firmware bytes, addresses to access, or hardware."""

import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import decode_isp3_ring as ring


# Each literal has an independently fixed byte sum. The indirect fixtures use a
# zero reference: the decoder can only use a separately supplied regular file.
PATH_SLOT = bytes.fromhex("0403020101000102 0807060500000000") + bytes(40) + bytes.fromhex("0100000000000029")
CTRL_SLOT = bytes.fromhex("1700000001000502 0000000000000000 500a000000000000") + bytes(32) + bytes.fromhex("020000000000007b")
INFO_SLOT = bytes.fromhex("1600000002000502 0000000000000000 7812000000000000") + bytes(32) + bytes.fromhex("01000000000000aa")
DONE_SLOT = bytes.fromhex("0800000001000100 0403020101000102 000034125245504c") + bytes(39) + bytes([0x91])
FRAME_DONE_SLOT = bytes.fromhex("0900000002000100 8877665544332211") + bytes(47) + bytes([0x70])


class PacketTests(unittest.TestCase):
    def test_stream_path_and_command_done(self):
        command = ring.decode_slot(PATH_SLOT, "command", 2)
        self.assertEqual(command["stream_tag"], 1)
        self.assertTrue(command["matches_capture_ring"])
        self.assertEqual(len(bytes.fromhex(command["inline_hex"])), 20)
        done = ring.decode_slot(DONE_SLOT, "response")
        self.assertEqual(done["command_sequence"], command["sequence"])
        self.assertEqual(done["command_id"], command["id"])
        self.assertEqual(done["status"], 0)
        self.assertEqual(done["error_detail"], 0x1234)
        self.assertTrue(bytes.fromhex(done["reply_hex"]).startswith(b"REPL"))

    def test_indirect_frame_control_and_independent_body(self):
        record = ring.decode_slot(CTRL_SLOT, "command", 3)
        self.assertTrue(record["matches_frame_ctrl_issuer"])
        self.assertTrue(record["matches_capture_ring"])
        self.assertEqual(record["payload_reference"], "0x0000000000000000")
        ring.check_payload(record, bytes(0xa50))
        self.assertTrue(record["external_payload_verified"])
        for bad in (bytes(0xa4f), bytes(0xa4f) + b"\x01"):
            with self.subTest(length=len(bad)), self.assertRaises(ValueError):
                ring.check_payload(ring.decode_slot(CTRL_SLOT, "command"), bad)

    def test_frame_info_retains_tag_on_global_command_ring(self):
        record = ring.decode_slot(INFO_SLOT, "command", 0)
        self.assertEqual(record["inferred_requested_ring"], 2)
        self.assertTrue(record["matches_capture_ring"])
        self.assertTrue(record["passes_wrapped_stream_class_tag_check"])
        self.assertFalse(ring.decode_slot(INFO_SLOT, "command", 2)["matches_capture_ring"])
        self.assertEqual(record["matching_frame_info_sizes"], ["wrapped"])
        ram = bytearray(INFO_SLOT)
        ram[16] = 0x30
        ram[63] = 0x62
        self.assertEqual(ring.decode_slot(ram, "command")["matching_frame_info_sizes"], ["ram"])

    def test_global_physical_ring_does_not_validate_a_global_stream_tag(self):
        global_tag = bytearray(INFO_SLOT)
        global_tag[56:58] = bytes.fromhex("ffff")
        global_tag[63] = 0xa7
        record = ring.decode_slot(global_tag, "command", 0)
        self.assertTrue(record["matches_capture_ring"])
        self.assertFalse(record["passes_wrapped_stream_class_tag_check"])

    def test_frame_info_package_debug_view_uses_separate_saved_bytes(self):
        record = ring.decode_slot(INFO_SLOT, "command")
        body = bytearray(0x1278)
        body[0x784], body[0x790], body[0x79c] = 64, 128, 64
        ring.check_payload(record, body)
        self.assertEqual(record["r64_host_debug_view"]["length_operands"], [64, 128, 64])

    def test_frame_done_keeps_the_metadata_reference_opaque(self):
        record = ring.decode_slot(FRAME_DONE_SLOT, "response")
        self.assertEqual(record["metadata_reference"], "0x1122334455667788")
        self.assertNotIn("command_sequence", record)
        self.assertNotIn("status", record)

    def test_send_buffer_planes_and_ends_in_a_synthetic_allocation(self):
        slot = bytearray(64)
        struct.pack_into("<II", slot, 0, 5, ring.SEND_BUFFER)
        struct.pack_into("<QI", slot, 8 + 0x0c, 0x1000, 256)
        struct.pack_into("<QI", slot, 8 + 0x18, 0x1100, 128)
        slot[-1] = sum(slot[:-1]) & 0xff
        record = ring.decode_slot(slot, "command", 0)
        self.assertEqual([p["bytes"] for p in record["planes"]], [256, 128, 0])
        ring.check_owned_range(record, 0x1000, 384)
        for base, size in ((0x1000, 383), (0x1001, 384), (-1, 385), (2**64 - 1, 2)):
            with self.subTest(base=base, size=size), self.assertRaises(ValueError):
                ring.check_owned_range(record, base, size)

    def test_unknown_and_empty_records(self):
        unknown = bytes.fromhex("ffffffff33554371") + bytes(48) + bytes.fromhex("ffff000000000036")
        record = ring.decode_slot(unknown, "command")
        self.assertEqual(record["name"], "unclassified")
        self.assertEqual(record["form"], "unclassified")
        self.assertEqual(record["inferred_requested_ring"], 0)
        self.assertEqual(ring.decode_slot(bytes(64), "response")["state"], "zero-filled")

    def test_bad_checksum_size_or_ring(self):
        for data, index in ((PATH_SLOT[:-1], 0), (PATH_SLOT[:-1] + b"\0", 0), (PATH_SLOT, 4)):
            with self.subTest(length=len(data), index=index), self.assertRaises(ValueError):
                ring.decode_slot(data, "command", index)

    def test_normalized_cursor_bounds_and_wrap(self):
        size = ring.RING_BYTES["command"]
        self.assertEqual(ring.pending_offsets("command", size, size - 64, 64), [size - 64, 0])
        self.assertEqual(ring.pending_offsets("command", size, 128, 128), [])
        self.assertEqual(ring.pending_offsets("response", 0x3200, 0, 128), [0, 64])
        for read, write in ((None, None), (0, None), (1, 64), (0, size), (-64, 0)):
            with self.subTest(read=read, write=write), self.assertRaises(ValueError):
                ring.pending_offsets("command", size, read, write)

    def test_cli_reads_only_pending_slots(self):
        script = Path(ring.__file__)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "response-ring.bin"
            cells = bytearray(ring.RING_BYTES["response"])
            cells[-64:] = DONE_SLOT
            cells[:64] = FRAME_DONE_SLOT
            cells[64] = 99  # stale slot with an invalid checksum, outside the snapshot
            path.write_bytes(cells)
            params = [sys.executable, "-B", str(script), "response", str(path),
                      "--read-pointer", "0x31c0", "--write-pointer", "0x40"]
            result = subprocess.run(params, capture_output=True, text=True, check=True)
            decoded = json.loads(result.stdout)
            self.assertEqual([r["name"] for r in decoded], ["CMD_DONE", "FRAME_DONE"])
            self.assertEqual([r["offset"] for r in decoded], [0x31c0, 0])


if __name__ == "__main__":
    unittest.main()
