#!/usr/bin/env python3
"""Parse command line arguments."""
import os
import argparse
import logging
import sys

try:
    from tabulate import tabulate, _table_formats
except ImportError:
    print("Python tabulate package is required!")
    raise SystemExit

try:
    # That means we are in debug mode, being called within the package
    sys.path.append(os.path.abspath(os.path.join(__file__, "../..")))
    if bool(os.environ.get("DIRTOOLS3_DEBUG")):
        sys.path.append(os.path.abspath(os.path.join(__file__, "../..")))

    from scanner import Folder, SortBy

    from utils import bytes2human, human2bytes
    from loggers import logger
except ImportError:
    print("Cannot find dirtools3 package.")
    raise SystemExit
else:
    logger.setLevel(logging.WARNING)

SORT_BY_OPTIONS = [str(s).lower() for s in SortBy]
TABULATE_OPTIONS = ("csv",) + tuple(_table_formats.keys())


def get_args(args: list):
    """Parse arguments with argparse."""
    cli = argparse.ArgumentParser(
        prog="dirt",
        usage="%(prog)s [OPTION]... [PATH]",
        description="Scans file system folders to collect statistical information about their contents (size, file count, creation time, modification time, etc.)",
        # formatter_class=argparse.RawTextHelpFormatter,
        epilog=None,
        add_help=True,
    )
    cli.add_argument(
        "path",
        action="store",
        default=os.getcwd(),
        nargs="?",
        help="file or directory to search",
    )
    cli.add_argument(
        "-s",
        "--sortby",
        choices=SORT_BY_OPTIONS,
        default=str(SortBy.ATIME_DESC).lower(),
        help=f"Sorting parameter for output. Allowed values are: [{'|'.join(SORT_BY_OPTIONS)}]",
        metavar="",
    )
    cli.add_argument(
        "-o",
        "--output",
        choices=TABULATE_OPTIONS,
        default="simple",
        help=f"passed directly to tabulate package as the 'tablefmt' param, with the exception of 'csv'. Allowed values are: [{'|'.join(TABULATE_OPTIONS)}]",
        metavar="",
    )
    cli.add_argument(
        "-p",
        "--precision",
        type=int,
        choices=range(0, 12),
        default=2,
        help="floating precision of the human-readable size fmt. Does not have any effect if --nohuman is given. Integer value between 0 to 11 and defaults to 2.",
        metavar="",
    )
    cli.add_argument(
        "-d",
        "--depth",
        type=int,
        choices=range(0, 3),
        default=0,
        help="the depth of subfolders you want to list, trim down, etc. Maximum allowed depth is 3 subfolders inside, limited only for the CLI. Integer value between 0 to 2 and defaults to 0",
        metavar="",
    )
    cli.add_argument(
        "-nh",
        "--nohuman",
        action="store_true",
        default=False,
        help="display only raw values such as file size in bytes, creation time in timestamp, etc.",
    )
    cli.add_argument(
        # Not going to implement this option going forward
        "--trim-down",
        action="store",
        default=None,
        help=argparse.SUPPRESS,
    )
    cli._positionals.title = "MANDATORY ARGUMENTS"
    cli._optionals.title = cli._optionals.title.upper()
    return cli.parse_args(args)


if __name__ == "__main__":
    test_args = ["-h"]
    get_args(test_args)
