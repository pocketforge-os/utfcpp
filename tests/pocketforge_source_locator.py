#!/usr/bin/env python3

import configparser
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SECTION = 'submodule "extern/ftest"'
FORK_URL = "https://github.com/pocketforge-os/ftest.git"
PIN = "c4ad4af0946b73ce1a40cbc72205d15d196c7e06"


def validate_gitmodules(path):
	parser = configparser.ConfigParser(interpolation=None)
	with path.open(encoding="utf-8") as stream:
		parser.read_file(stream)
	if parser.sections() != [SECTION]:
		raise ValueError("expected only the extern/ftest submodule")
	if parser.get(SECTION, "path", fallback="") != "extern/ftest":
		raise ValueError("ftest submodule path changed")
	if parser.get(SECTION, "url", fallback="") != FORK_URL:
		raise ValueError("ftest submodule does not use the PocketForge fork")


class SourceLocatorTests(unittest.TestCase):
	def test_repository_locator_and_gitlink_are_pinned(self):
		validate_gitmodules(ROOT / ".gitmodules")
		entry = subprocess.run(
			["git", "-C", str(ROOT), "ls-files", "--stage", "extern/ftest"],
			check=True,
			text=True,
			stdout=subprocess.PIPE,
		).stdout.split()
		self.assertEqual(entry[0], "160000")
		self.assertEqual(entry[1], PIN)

	def test_exact_locator_is_accepted(self):
		with tempfile.TemporaryDirectory() as temp_dir:
			path = Path(temp_dir) / ".gitmodules"
			path.write_text(
				f'[{SECTION}]\n\tpath = extern/ftest\n\turl = {FORK_URL}\n',
				encoding="utf-8",
			)
			validate_gitmodules(path)

	def test_upstream_url_is_rejected(self):
		with tempfile.TemporaryDirectory() as temp_dir:
			path = Path(temp_dir) / ".gitmodules"
			path.write_text(
				f'[{SECTION}]\n\tpath = extern/ftest\n\turl = https://github.com/nemtrif/ftest\n',
				encoding="utf-8",
			)
			with self.assertRaises(ValueError):
				validate_gitmodules(path)


if __name__ == "__main__":
	unittest.main(verbosity=2)
