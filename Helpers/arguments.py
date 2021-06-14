import argparse
import math
import re


def csv_file_type(arg_value, pat=re.compile(r'^.+\.csv$')):
    if not pat.match(arg_value):
        raise argparse.ArgumentTypeError('Not a csv file')
    return arg_value


def get_arguments():
    arg_parser = argparse.ArgumentParser(description='backup livelib library')

    arg_parser.add_argument('user',
                            type=str,
                            help='livelib username used in the link to the personal page')

    arg_parser.add_argument('--min_delay',
                            type=int,
                            default=60,
                            help='minimum waiting time between two page loads (default: 30 seconds)')

    arg_parser.add_argument('--max_delay',
                            type=int,
                            default=30,
                            help='maximum waiting time between two page loads (default: 30 seconds)')

    arg_parser.add_argument('-b', '--books_backup',
                            type=csv_file_type,
                            default=None,
                            help='path to file stores books backup')

    arg_parser.add_argument('-q', '--quotes_backup',
                            type=csv_file_type,
                            default=None,
                            help='path to file stores quotes backup')

    arg_parser.add_argument('--read_count',
                            type=int,
                            default=math.inf,
                            help='the number of pages of read books that the script will process')

    arg_parser.add_argument('--quote_count',
                            type=int,
                            default=math.inf,
                            help='the number of pages of quotes that the script will process')

    arg_parser.add_argument('-R', '--rewrite_all',
                            action='store_true')

    return arg_parser.parse_args()
