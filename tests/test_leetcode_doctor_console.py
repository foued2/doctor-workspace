from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_ROOT / "leetcode-tools" / "leetcode_doctor.py"


def load_leetcode_doctor_module():
    spec = importlib.util.spec_from_file_location("leetcode_doctor_module", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Cp1252Sink:
    encoding = "cp1252"

    def __init__(self) -> None:
        self.buffer = ""

    def write(self, text: str) -> int:
        encoded = text.encode(self.encoding)
        decoded = encoded.decode(self.encoding)
        self.buffer += decoded
        return len(text)

    def flush(self) -> None:
        return None


class LeetCodeDoctorConsoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_leetcode_doctor_module()

    def test_print_safe_falls_back_for_cp1252_console(self) -> None:
        sink = Cp1252Sink()

        self.module._print_safe("👨‍⚕️ LeetCode Doctor", file=sink)

        self.assertIn("LeetCode Doctor", sink.buffer)
        self.assertTrue(sink.buffer.endswith("\n"))

    def test_coerce_console_text_replaces_unencodable_characters(self) -> None:
        sink = Cp1252Sink()

        result = self.module._coerce_console_text("✅ ready", sink)

        self.assertEqual(result, "? ready")


if __name__ == "__main__":
    unittest.main()
