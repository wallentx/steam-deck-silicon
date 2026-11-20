"""Small non-vendor fixtures for section boundaries and the SMU directory reader."""

import struct
import unittest

from scripts.compare_isp3_smu import smu_parts
from scripts.scan_isp3_frame_info import sections


class ArtifactTests(unittest.TestCase):
    def test_unnamed_executable_section_still_counts(self):
        data = bytearray(0x110)
        data[:6] = b"\x7fELF\x02\x01"
        struct.pack_into("<Q", data, 40, 64)
        struct.pack_into("<3H", data, 58, 64, 2, 0)
        # The image has no section-name table. Its four code bytes are still allocated.
        struct.pack_into("<II4QII2Q", data, 128, 0, 1, 6, 0, 256, 4, 0, 0, 1, 0)
        self.assertEqual(list(sections(data)), [("<unnamed>", True, 256, 4)])
        struct.pack_into("<Q", data, 128 + 32, 128)
        with self.assertRaises(ValueError):
            list(sections(data))

    def test_smu_directory_uses_relative_offsets_and_both_types(self):
        directory = 0x20
        size = 0x40200
        first = 64
        second = first + size
        image = bytearray(directory + second + size)
        image[directory:directory + 4] = b"$PL2"
        struct.pack_into("<I", image, directory + 8, 2)
        for row, (kind, start) in enumerate([(8, first), (0x12, second)]):
            struct.pack_into("<IIQ", image, directory + 16 + row * 16,
                             kind, size, (2 << 62) | start)
            image[directory + start + 16:directory + start + 20] = b"$PS1"
        self.assertEqual(set(smu_parts(image, directory)), {8, 0x12})
        struct.pack_into("<I", image, directory + 32, 8)
        with self.assertRaises(ValueError):
            smu_parts(image, directory)


if __name__ == "__main__":
    unittest.main()
