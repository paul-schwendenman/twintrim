#! /usr/bin/env python3
'''
Twin trim

A duplicate file remover
'''
import argparse
import hashlib
import logging
import os
import re
import sys
import textwrap
from twintrimmer import walk_path

def terminal():
    '''
        The main function handles all the parsing of arguments.
    '''
    epilog = r'''
    examples:

        find matches with default regex:

            $ ./twintrimmer.py -n ~/downloads

        find matches ignoring the extension:

            $  ls examples/
            Google.html  Google.html~
            $ ./twintrimmer.py -n -p '(^.+?)(?: \(\d\))*\..+' examples/
            examples/Google.html~ would have been deleted

        find matches with "__1" added to basename:

            $ ls examples/underscore/
            file__1.txt  file.txt
            $ ./twintrimmer.py -n -p '(.+?)(?:__\d)*\..*' examples/underscore/
            examples/underscore/file__1.txt to be deleted
    '''

    parser = argparse.ArgumentParser(
        description='tool for removing duplicate files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(epilog))
    parser.add_argument('path', help='path to check')
    parser.add_argument('-n', '--no-action',
                        default=False,
                        action='store_true',
                        help='show what files would have been deleted')
    parser.add_argument('-r', '--recursive',
                        default=False,
                        action='store_true',
                        help='search directories recursively')
    parser.add_argument('--verbosity',
                        type=int,
                        default=1,
                        help='set print debug level')
    parser.add_argument('--log-file', help='write to log file.')
    parser.add_argument('--log-level',
                        type=int,
                        default=3,
                        help='set log file debug level')
    parser.add_argument('-p', '--pattern',
                        dest='regex_pattern',
                        type=str,
                        default=r'(^.+?)(?: \(\d\))*(\..+)$',
                        help='set filename matching regex')
    parser.add_argument(
        '-c', '--only-checksum',
        default=False,
        action='store_true',
        dest='skip_regex',
        help='toggle searching by checksum rather than name first')

    parser.add_argument('-i', '--interactive',
                        default=False,
                        action='store_true',
                        help='ask for file deletion interactively')

    parser.add_argument('--hash-function',
                        type=str,
                        default='md5',
                        choices=hashlib.algorithms_available,
                        help='set hash function to use for checksums')
    parser.add_argument('--make-links',
                        default=False,
                        action='store_true',
                        help='create hard link rather than remove file')
    parser.add_argument('--remove-links',
                        default=False,
                        action='store_true',
                        help='remove hardlinks rather than skipping')

    args = parser.parse_args()

    if not os.path.isdir(args.path):
        parser.error('path was not a directory: "{0}"'.format(args.path))

    if args.log_level != 3 and not args.log_file:
        parser.error('Log level set without log file')

    if args.regex_pattern != r'(^.+?)(?: \(\d\))*(\..+)$' and args.skip_regex:
        parser.error('Pattern set while skipping regex checking')

    try:
        re.compile(args.regex_pattern)
    except re.error:
        parser.error('Invalid regular expression: "{0}"'.format(args.pattern))

    stream = logging.StreamHandler()
    stream.setLevel((5 - args.verbosity) * 10)
    formatter_simple = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')
    stream.setFormatter(formatter_simple)
    root_logger = logging.getLogger('')
    root_logger.addHandler(stream)
    root_logger.setLevel(logging.DEBUG)

    if args.log_file:
        try:
            log_file = logging.FileHandler(args.log_file)
        except OSError as err:
            sys.exit("Couldn't open log file: {0}".format(err))
        log_file.setFormatter(formatter_simple)
        log_file.setLevel((5 - args.log_level) * 10)
        root_logger.addHandler(log_file)

    root_logger.debug("Args: %s", args)

    walk_path(**vars(args))

if __name__ == '__main__':
    terminal()
