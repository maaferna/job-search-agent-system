"""Tests of the sanitization gate's image layer and line scanner (no local denylist needed)."""
import hashlib
import pathlib
import struct
import sys
import tempfile
import unittest
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sanitize_check as s  # noqa: E402


def png(*extra_chunks):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 0, 0, 0, 0))
            + b"".join(chunk(k, d) for k, d in extra_chunks)
            + chunk(b"IDAT", zlib.compress(b"\x00\x00")) + chunk(b"IEND", b""))


class Images(unittest.TestCase):
    def check(self, files):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            for name, data in files.items():
                (root / name).write_bytes(data if isinstance(data, bytes) else data.encode())
            return s.check_images(sorted(root.iterdir()), lambda p: p.name)

    def manifest(self, name, data):
        return f"{s.MANIFEST_HEAD}\n# image: {name} sha256={hashlib.sha256(data).hexdigest()}\n\nvisible text\n"

    def test_image_with_matching_manifest_passes(self):
        img = png()
        self.assertEqual(self.check({"a.png": img, "a.txt": self.manifest("a.png", img)}), [])

    def test_image_without_manifest_fails(self):
        self.assertIn("no manifest", self.check({"a.png": png()})[0])

    def test_image_changed_after_its_manifest_fails(self):
        hits = self.check({"a.png": png(), "a.txt": self.manifest("a.png", b"other bytes")})
        self.assertIn("changed since", hits[0])

    def test_png_text_chunks_are_rejected(self):
        img = png((b"tEXt", b"Author\x00someone"))
        hits = self.check({"a.png": img, "a.txt": self.manifest("a.png", img)})
        self.assertIn("metadata chunks tEXt", hits[0])


class Lines(unittest.TestCase):
    def scan(self, line):
        return s.scan_lines([line], dict(s.STATIC), None, "f")

    def test_static_patterns(self):
        # Built from parts so this file does not trip the gate it tests.
        self.assertTrue(self.scan("asked for " + "$" + "1.500.000 per month"))
        self.assertTrue(self.scan("write to someone" + "@" + "gmail.com"))

    def test_phone_pattern_does_not_fire_inside_a_hash(self):
        self.assertEqual(self.scan("# image: a.png sha256=ab56912345678cd"), [])
        self.assertTrue(self.scan("call +5" + "6 9 1234 5678"))   # built from parts, like the others

    def test_reserved_example_domains_are_allowed(self):
        self.assertEqual(self.scan("example.candidate@example.com"), [])


if __name__ == "__main__":
    unittest.main()
