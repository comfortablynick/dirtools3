#!/usr/bin/env python3
"""Command-line interface to the dirtools3 package."""
import csv
import io
import logging
import os
import sys

from dirtools import argument_parser

try:
    from tabulate import tabulate, _table_formats
except ImportError:
    print(
        'Python "tabulate" package is required for the command line '
        "interface, please install it with: \n"
        "pip install tabulate"
    )
    raise SystemExit

try:
    # That means we are in debug mode, being called within the package
    # sys.path.append(os.path.abspath(os.path.join(__file__, "../..")))
    if bool(os.environ.get("DIRTOOLS3_DEBUG")):
        sys.path.append(os.path.abspath(os.path.join(__file__, "../..")))

    from dirtools.scanner import Folder, SortBy

    from dirtools.utils import bytes2human, human2bytes
    from dirtools.loggers import logger
except ImportError:
    print(
        "dirtools3 package is not installed. Please install it with: \n"
        "pip install dirtools3"
    )
    raise SystemExit
else:
    logger.setLevel(logging.INFO)

TABLE_HEADERS = {
    "name": "Name",
    "size": "Size",
    "depth": "Depth",
    "num_of_files": "Files",
    "atime": "Access Time",
    "mtime": "Modify Time",
    "ctime": "Change Time",
}

# cli = click.Group()
SORT_BY_OPTIONS = [str(s).lower() for s in SortBy]
TABULATE_OPTIONS = ("csv",) + tuple(_table_formats.keys())
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


def invoke_dirtools3(args):
    """Command line interface to the dirtools package."""
    # Get SortBy enum val
    try:
        sortby = next(s for s in SortBy if args.sortby.upper() == str(s))
    except StopIteration:
        sys.stderr.write("Invalid sort by option: {0}".format(sortby))
        return
    path = args.path
    precision = args.precision
    depth = args.depth
    nohuman = args.nohuman
    trim_down = args.trim_down
    output = args.output
    # Create folder object and start its scanning process
    scan = Folder(path, sortby, level=depth)
    old_size = scan.total_size
    old_items_len = len(scan)

    # Only folder scanning and listing etc
    if trim_down is None:
        items = scan.items(humanise=not nohuman, precision=precision)
    # Do not allow to pass only digit value because it will be interpreted as
    # byte value and probably this was an accident.
    elif trim_down.isdigit():
        sys.stderr.write(
            "--trim-down value cannot be only numeric to prevent accident, {0} given.".format(
                trim_down
            )
        )
        return
    # Folder trimming
    else:
        items = scan.cleanup_items(trim_down, humanise=not nohuman, precision=precision)

    # CSV - custom
    if output.lower() == "csv":
        with io.StringIO() as csv_io:
            writer = csv.writer(csv_io, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(TABLE_HEADERS.values())
            writer.writerows(i.values() for i in items)
            rows = csv_io.getvalue().rstrip()
    # Display it with tabulate
    else:
        rows = tabulate(items, TABLE_HEADERS, tablefmt=output, stralign="right")

    sys.stdout.write(rows)

    # Give summary info regarding to its listing
    lit = lambda n, sing, plur: str(n) + (f" {sing}" if n == 1 else f" {plur}")
    if trim_down is None:
        sys.stdout.write(
            "\n{ct} with total of {size} data; took {exec}.".format(
                exec=lit(scan.exec_took, "second", "seconds"),
                size=bytes2human(scan.total_size, precision=precision),
                ct=lit(len(scan), "item", "items"),
            )
        )
    # or cleaning operation
    else:
        del_len = len(scan) - old_items_len
        del_size = bytes2human(old_size - scan.total_size, precision=precision)
        sys.stderr.write(
            "{del_len:d} items with total of {del_size} data has been deleted.".format(
                del_len=del_len, del_size=del_size
            )
        )
        sys.stderr.write(
            "Currently {len} items left with {size} of data; took {exec} second(s).".format(
                len=len(scan),
                size=bytes2human(scan.total_size, precision=precision),
                exec=scan.exec_took,
            )
        )


if __name__ == "__main__":
    try:
        sys.argv[1]
        cli_args = sys.argv[1:]
    except IndexError:
        cli_args = []
    args = argument_parser.get_args(cli_args)
    logger.debug(args)
    invoke_dirtools3(args)
