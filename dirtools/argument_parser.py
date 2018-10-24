#!/usr/bin/env python3
"""Parse command line arguments."""
import os
import argparse
import logging
import sys
from dirt import TABULATE_OPTIONS

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

    from dirtools import Folder, SortBy

    from dirtools.utils import bytes2human, human2bytes
    from dirtools.loggers import logger
except ImportError:
    print("Cannot find dirtools3 package.")
    raise SystemExit
else:
    logger.setLevel(logging.WARNING)

SORT_BY_OPTIONS = [str(s).lower() for s in SortBy]


def get_args(args: list):
    """Parse arguments with argparse."""
    cli = argparse.ArgumentParser(
        prog="dirt",
        usage="%(prog)s [OPTION]... [PATH]",
        description="""Scans file system folders to collect statistical information about their contents (size, file count, creation time, modification time, etc.""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
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
        choices=TABULATE_OPTIONS,
        default="simple",
        help="passed directly to tabulate package as the 'tablefmt' param, with the exception of 'csv'",
    )
    cli.add_argument(
        "--p",
        "--precision",
        type=int,
        choices=range(0, 11),
        default=2,
        help="floating precision of the human-readable size fmt. Does not have any effect if --nohuman is given",
    )
    cli._positionals.title = "MANDATORY ARGUMENTS"
    cli._optionals.title = cli._optionals.title.upper()
    return cli.parse_args(args)


if __name__ == "__main__":
    test_args = ["-h"]
    get_args(test_args)
