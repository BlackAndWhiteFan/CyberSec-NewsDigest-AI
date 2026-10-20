import py_compile
import unittest
from pathlib import Path


class TestScriptsCompile(unittest.TestCase):
    """Catch syntax errors in scripts that unit tests do not import
    (main.py is run only by the workflow; error of 2026-10-20 in v20)."""

    def test_all_source_files_compile(self):
        for path in sorted(Path(__file__).parent.glob("*.py")):
            with self.subTest(file=path.name):
                py_compile.compile(str(path), doraise=True)


if __name__ == "__main__":
    unittest.main()
