import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from makefile_source import read_makefile


class MakefileSourceTests(unittest.TestCase):
    def test_legacy_source_is_unchanged(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'Makefile'
            text = '# Original\ninclude windows.mk\nall:\n\techo hello\n'
            path.write_text(text)
            self.assertEqual(read_makefile(path, encoding='utf-8'), text)

    def test_sections_preserve_order_and_recipe_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            sections = root / 'make/sections'
            sections.mkdir(parents=True)
            first = 'VALUE := before\nfirst:\n\t@echo $(VALUE)\n'
            second = 'VALUE := after\ninclude accuracy_next.mk\n'
            (sections / 'rules-02.mk').write_text(first)
            (sections / 'rules-01.mk').write_text(second)
            path = root / 'Makefile'
            path.write_text('# Ordered Makefile sections\ninclude make/sections/rules-02.mk\ninclude make/sections/rules-01.mk\n')
            self.assertEqual(read_makefile(path), first + second)


if __name__ == '__main__':
    unittest.main()
