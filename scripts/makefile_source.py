"""Read ordered Makefile sections for source-inspection tools (not evaluation)."""
from pathlib import Path
import re


def read_makefile(path, *args, **kwargs):
    path = Path(path)
    text = path.read_text(*args, **kwargs)
    if path.name != 'Makefile' or '# Ordered Makefile sections' not in text:
        return text
    sections = re.findall(r'^include (make/sections/[^\s]+)$', text, re.M)
    return ''.join((path.parent / section).read_text(*args, **kwargs) for section in sections)
