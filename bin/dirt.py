#!/usr/bin/env python3
import csv
import io
import logging
import os
import sys

try:
    import click
except ImportError:
    print('Python "click" package is required for the command line '
          'interface, please install it with: \n'
          'pip install click')
    raise SystemExit

try:
    from tabulate import tabulate, _table_formats
except ImportError:
    print('Python "tabulate" package is required for the command line '
          'interface, please install it with: \n'
          'pip install tabulate')
    raise SystemExit

try:
    # That means we are in debug mode, being called within the package
    sys.path.append(os.path.abspath(os.path.join(__file__, '../..')))
    if bool(os.environ.get('DIRTOOLS3_DEBUG')):
        sys.path.append(os.path.abspath(os.path.join(__file__, '../..')))

    from dirtools import Folder, SortBy
    from dirtools.utils import bytes2human, human2bytes
    from dirtools.loggers import logger
except ImportError:
    print('dirtools3 package is not installed. Please install it with: \n'
          'pip install dirtools3')
    raise SystemExit
else:
    logger.setLevel(logging.WARNING)

TABLE_HEADERS = {
    'name': 'Name',
    'size': 'Size',
    'depth': 'Depth',
    'num_of_files': 'Files',
    'atime': 'Access Time',
    'mtime': 'Modify Time',
    'ctime': 'Change Time'
}

cli = click.Group()
SORT_BY_OPTIONS = [str(s).lower() for s in SortBy]
TABULATE_OPTIONS = ('csv', ) + tuple(_table_formats.keys())
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('path', nargs=1)
@click.option(
    '--sortby',
    '-s',
    type=click.Choice(SORT_BY_OPTIONS),
    default=str(SortBy.ATIME_DESC).lower(),
    help='Sorting parameter to display the items in desired order. '
    'Defaults to "atime_desc" that shows recently accessed items at '
    'the beginning, which is opposite of "atime_asc". To display '
    'newly modified ones use "mtime_desc" and "mtime_asc" for vice versa.')
@click.option(
    '--output',
    '-o',
    type=click.Choice(TABULATE_OPTIONS),
    default='simple',
    help='This option is passed directly to python-tabulate package '
    'as the "tablefmt" parameter, with the exception of manual '
    '"csv" output. Defaults to "simple". Check the current table '
    'formats from; https://bitbucket.org/astanin/python-tabulate.')
@click.option(
    '--precision',
    '-p',
    type=click.IntRange(0, 11),
    default=2,
    help='The floating precision of the human-readable size format. '
    'Does not have any affect if --nohuman is given. '
    'Integer value between 0 to 11 and defaults to 2.')
@click.option(
    '--depth',
    '-d',
    type=click.IntRange(0, 2),
    default=0,
    help='The depth of sub folders you want to list, trim down, etc. '
    'Maximum allowed depth is 3 sub-folders inside, limited '
    'only for the CLI. Integer value between 0 to 2 and defaults '
    'to 0 (zero).')
@click.option(
    '--nohuman',
    '-nh',
    type=click.BOOL,
    is_flag=True,
    default=False,
    help='Display only raw values such as file size in bytes, creation '
    'time in timestamp etc.')
@click.option(
    '--trim-down',
    default=None,
    help='The size to be trimmed down instead of listing, in human '
    'readable format. For example; "900mb". \n\n'
    'WARNING: --trim-down action DELETES your files and cannot be undo!')
def invoke_dirtools3(path, sortby, output, precision, depth, nohuman,
                     trim_down: str):
    """Command line interface to the dirtools package.
    """

    # Get SortBy enum val
    try:
        sortby = next(s for s in SortBy if sortby.upper() == str(s))
    except StopIteration:
        click.secho(
            'Invalid sort by option: {0}'.format(sortby), err=True, fg='red')
        return

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
        click.secho(
            '--trim-down value cannot be only numeric to prevent accident, {0} given.'.
            format(trim_down),
            err=True,
            fg='red')
        return
    # Folder trimming
    else:
        items = scan.cleanup_items(
            trim_down, humanise=not nohuman, precision=precision)

    # CSV - custom
    if output.lower() == 'csv':
        with io.StringIO() as csv_io:
            writer = csv.writer(csv_io, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(TABLE_HEADERS.values())
            writer.writerows(i.values() for i in items)
            rows = csv_io.getvalue().rstrip()
    # Display it with tabulate
    else:
        rows = tabulate(
            items, TABLE_HEADERS, tablefmt=output, stralign='right')

    click.echo(rows)

    # Give summary info regarding to its listing
    if trim_down is None:
        click.secho(
            '{len} items with total of {size} data; took {exec} second(s).'.
            format(
                exec=scan.exec_took,
                size=bytes2human(scan.total_size, precision=precision),
                len=len(scan)),
            bold=True)
    # or cleaning operation
    else:
        del_len = len(scan) - old_items_len
        del_size = bytes2human(old_size - scan.total_size, precision=precision)
        click.secho(
            '{del_len:d} items with total of {del_size} data has been deleted.'.
            format(del_len=del_len, del_size=del_size),
            bold=True)
        click.secho(
            'Currently {len} items left with {size} of data; took {exec} second(s).'.
            format(
                len=len(scan),
                size=bytes2human(scan.total_size, precision=precision),
                exec=scan.exec_took),
            bold=True)


if __name__ == '__main__':
    invoke_dirtools3()

