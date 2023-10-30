# This is a sample commands.py.  You can add your own commands here.
#
# Please refer to commands_full.py for all the default commands and a complete
# documentation.  Do NOT add them all here, or you may end up with defunct
# commands when upgrading ranger.

# A simple command for demonstration purposes follows.
# -----------------------------------------------------------------------------

from __future__ import absolute_import, division, print_function

import hashlib

# You can import any python module as needed.
import os
import pathlib
import re

from plugins.ranger_udisk_menu.mounter import mount

# You always need to import ranger.api.commands here to get the Command class:
from ranger.api.commands import Command


class get_strings(Command):
    ASCII_BYTE = b" !\"#\$%&'\(\)\*\+,-\./0123456789:;<=>\?@ABCDEFGHIJKLMNOPQRSTUVWXYZ\[\]\^_`abcdefghijklmnopqrstuvwxyz\{\|\}\\\~\t"

    def execute(self):
        cwd = self.fm.thisdir
        filepaths = map(lambda x: x.path, cwd.get_selection())
        for filepath in filepaths:
            self.process(filepath)

    def process(self, path: str) -> None:
        p = pathlib.Path(path)
        if p.is_file():
            self.process_file(p)
        elif p.is_dir():
            for pd in p.rglob("*"):
                if pd.is_file():
                    self.process_file(pd)

    def process_file(self, filepath: pathlib.Path) -> None:
        data = b""
        re_narrow = re.compile(b"([%s]{%d,})" % (self.ASCII_BYTE, 4))
        re_wide = re.compile(b"((?:[%s]\x00){%d,})" % (self.ASCII_BYTE, 4))
        with open(filepath, "rb") as f:
            data = f.read()

        strings_file = f"{filepath}.strings"
        with open(strings_file, "w") as out:
            for match in re_narrow.finditer(data):
                out.write(match.group().decode("ascii") + "\n")

            for match in re_wide.finditer(data):
                try:
                    out.write(match.group().decode("utf-16") + "\n")
                except UnicodeDecodeError:
                    pass


class md5(Command):  # pylint: disable=invalid-name
    filename_fmt = "{new_filename}"

    def execute(self):
        cwd = self.fm.thisdir
        filepaths = map(lambda x: x.path, cwd.get_selection())
        for filepath in filepaths:
            self.process(filepath)

    def process(self, path: str) -> None:
        p = pathlib.Path(path)
        if p.is_file():
            self.process_file(p)
        elif p.is_dir():
            for pd in p.rglob("*"):
                if pd.is_file():
                    self.process_file(pd)

    def process_file(self, filepath: str) -> None:
        path = pathlib.Path(filepath)
        new_filename = self.hash_uppercase(str(path))
        extension = path.suffix
        new_path = pathlib.Path(
            path.parent,
            self.filename_fmt.format(new_filename=new_filename, extension=extension),
        )
        if new_path == filepath:
            return

        # while new_path.is_file():
        #     new_path = pathlib.Path(str(new_path) + "_")

        path.rename(new_path)

    @staticmethod
    def hash_uppercase(filepath: str) -> str:
        hash_value = hashlib.md5()

        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(5 * 1024 * 1024), b""):
                hash_value.update(chunk)

        return hash_value.hexdigest().upper()


class md5e(md5):
    filename_fmt = "{new_filename}{extension}"
