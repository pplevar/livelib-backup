import argparse
import math
import re
from .validators import validate_username, validate_delay, validate_driver_type
from .constants import SUPPORTED_DRIVERS, DEFAULT_MIN_DELAY, DEFAULT_MAX_DELAY


def table_file_type(arg_value, pat=re.compile(r'^.+\.(?:xlsx|csv)$')):
    """Validate file extension for backup files."""
    if not pat.match(arg_value):
        raise argparse.ArgumentTypeError('File must have .csv or .xlsx extension')
    return arg_value


def get_arguments():
    """
    Parse and validate command-line arguments.

    Returns:
        Namespace object with validated arguments

    Raises:
        ValueError: If validation fails for any argument
    """
    arg_parser = argparse.ArgumentParser(description='Backup Livelib library data')

    arg_parser.add_argument('user',
                            type=str,
                            help='Livelib username used in the link to the personal page')

    arg_parser.add_argument('--min_delay',
                            type=int,
                            default=DEFAULT_MIN_DELAY,
                            help=f'Minimum waiting time between two page loads (default: {DEFAULT_MIN_DELAY} seconds)')

    arg_parser.add_argument('--max_delay',
                            type=int,
                            default=DEFAULT_MAX_DELAY,
                            help=f'Maximum waiting time between two page loads (default: {DEFAULT_MAX_DELAY} seconds)')

    arg_parser.add_argument('-b', '--books_backup',
                            type=table_file_type,
                            default=None,
                            help='Path to file that stores books backup')

    arg_parser.add_argument('-q', '--quotes_backup',
                            type=table_file_type,
                            default=None,
                            help='Path to file that stores quotes backup')

    arg_parser.add_argument('--read_count',
                            type=int,
                            default=math.inf,
                            help='The number of pages of read books that the script will process')

    arg_parser.add_argument('--quote_count',
                            type=int,
                            default=math.inf,
                            help='The number of pages of quotes that the script will process')

    arg_parser.add_argument('-R', '--rewrite_all',
                            action='store_true',
                            help='Rewrite all backup files (not update)')

    arg_parser.add_argument('-s', '--skip',
                            type=str,
                            choices=['books', 'quotes'],
                            help='Skip the action (books/quotes)')

    arg_parser.add_argument('-d', '--driver',
                            type=str,
                            default='requests',
                            choices=SUPPORTED_DRIVERS,
                            help='The name of the page download driver (requests/selenium)')

    arg_parser.add_argument('-v', '--verbose',
                            action='count',
                            default=0,
                            help='Increase verbosity (-v for INFO, -vv for DEBUG)')

    arg_parser.add_argument('-q', '--quiet',
                            action='store_true',
                            help='Suppress all output except errors')

    args = arg_parser.parse_args()

    # Validate inputs
    args.user = validate_username(args.user)
    args.min_delay, args.max_delay = validate_delay(args.min_delay, args.max_delay)
    args.driver = validate_driver_type(args.driver, SUPPORTED_DRIVERS)

    return args
