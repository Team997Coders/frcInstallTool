# Cross platform python script to download all the CSA tools to a specified
# directory

# Portions of this code were derived from the original work under the MIT license:
# CSA-USB-Tool https://github.com/JamieSinn/CSA-USB-Tool/blob/main/pyusbtool.py
# Copyright (c) 2018 James Sinn
# The MIT license can be found at https://mit-license.org/

#!/usr/bin/env python3

import argparse
import contextlib
import csv
import hashlib
import pathlib
import os
import urllib.request
import sys
import subprocess
from typing import List
import zipfile

USER_AGENT = "frcInstallTool-997"
CHUNK_SIZE = 2**20


def download(url: str, dst_fname: pathlib.Path):
    def _reporthook(count, blocksize, totalsize):
        percent = int(count * blocksize * 100 / totalsize)
        if percent < 0 or percent > 100:
            sys.stdout.write("\r--%")
        else:
            sys.stdout.write("\r%02d%%" % percent)
        sys.stdout.flush()

    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    with contextlib.closing(urllib.request.urlopen(request)) as fp:
        headers = fp.info()

        with open(dst_fname, "wb") as tfp:
            # copied from urlretrieve source code, Python license
            bs = 1024 * 8
            size = -1
            blocknum = 0
            read = 0
            if "content-length" in headers:
                size = int(headers["Content-Length"])

            while True:
                block = fp.read(bs)
                if not block:
                    break
                read += len(block)
                tfp.write(block)
                blocknum += 1
                _reporthook(blocknum, bs, size)

    sys.stdout.write("\n")
    sys.stdout.flush()


def md5_file(fname: pathlib.Path) -> str:
    with open(fname, "rb") as fp:
        h = hashlib.md5()
        chunk = fp.read(CHUNK_SIZE)
        while chunk:
            h.update(chunk)
            chunk = fp.read(CHUNK_SIZE)

    return h.hexdigest()


def main():
    # TODO: implement size checking at startup
    parser = argparse.ArgumentParser()
    parser.add_argument("sourceCSV", type=pathlib.Path)
    parser.add_argument("destination", type=pathlib.Path)
    parser.add_argument(
        "-v",
        "--verbose_print",
        action="store_true",
        default=False,
        help="Print the source ID of each download",
    )
    parser.add_argument(
        "-o",
        "--hash_out",
        action="store_true",
        default=False,
        help="Prints the MD5 hash of each downloaded file (where applicable).",
    )

    args = parser.parse_args()

    present = 0
    invalid = 0

    installers: List[str] = []

    with open(args.sourceCSV) as sourceFilePath:
        for friendlyName, filename, id, md5, type, subfolder in csv.reader(
            sourceFilePath
        ):
            filepath: pathlib.Path

            if subfolder != "." and subfolder != "":
                filepath = args.destination / subfolder
            else:
                filepath = args.destination

            if friendlyName.startswith("#"):
                pass

            elif (
                type == "unzipped"
                or type == "zipped"
                or type == "unzipped-installer"
                or type == "zipped-installer"
            ):
                expectedHash = md5.lower()
                valid_checksum = expectedHash != "0"

                filepath.mkdir(exist_ok=True)

                filename = filepath / filename

                if args.verbose_print:
                    print("Downloading file {} from {}...".format(friendlyName, id))
                else:
                    print("Downloading file {}...".format(friendlyName))

                download(id, filename)

                hash = md5_file(filename)

                if (args.hash_out):
                    print("\nMD5 Hash for {}:".format(friendlyName))
                    print(hash)
                    print("Expected:")
                    print(expectedHash + "\n")

                if valid_checksum and md5_file(filename) != expectedHash:
                    print("{} does not match checksum!".format(friendlyName))
                    invalid += 1
                else:
                    present += 1

                if type == "zipped" or type == "zipped-installer":
                    with zipfile.ZipFile(filename, "r") as zipSource:
                        zipSource.extractall(os.path.splitext(filename)[0])

                if type == "unzipped-installer" or type == "zipped-installer":
                    installers.append(friendlyName)

            elif type == "git":
                if args.verbose_print:
                    print(
                        "Downloading git repository {} from {}...".format(
                            friendlyName, id
                        )
                    )
                else:
                    print("Downloading git repository {}...".format(friendlyName))
                try:
                    if subfolder != "." and subfolder != "":
                        subprocess.check_call(
                            ["git", "clone", "-q", "--mirror", id, filepath / friendlyName]
                        )
                    else:
                        subprocess.check_call(["git", "clone", "--mirror", "-q", id])
                except subprocess.CalledProcessError:
                    try:
                        if os.name == "nt":
                            subprocess.check_call(["git", "--version", ">NUL"])
                        elif os.name == "posix":
                            subprocess.check_call(["git", "--version", ">/dev/null"])
                    except subprocess.CalledProcessError:
                        print("Could not find git! Is it on your PATH?")
                    print("Could not clone git repository {}!".format(friendlyName))

            elif type == "pip":
                print("Downloading pip package {}...".format(friendlyName))
                try:
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", "-q", id]
                    )
                except subprocess.CalledProcessError:
                    try:
                        if os.name == "nt":
                            subprocess.check_call(
                                [sys.executable, "-m", "pip", "--version", ">NUL"]
                            )
                        elif os.name == "posix":
                            subprocess.check_call(
                                [sys.executable, "-m", "pip", "--version", ">/dev/null"]
                            )
                    except subprocess.CalledProcessError:
                        print("Could not find pip! Is it on your PATH?")
                    print("Could not download pip package {}!".format(friendlyName))

    print("\nFinished!\n-", present, "OK\n-", invalid, "invalid")

    if len(installers) != 0:
        print("\nModules needing further setup:")

        for module in installers:
            print(module)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(
            "\nProgram interrupted by user! \
            \nFiles that were in the process of downloading are very likely corrupt."
        )
