#! /usr/bin/env python3
import os
import hashlib
import argparse
import functools
import re
import logging
import textwrap
from collections import defaultdict, namedtuple

logger = logging.getLogger('')

Filename = namedtuple('Filename', ['name', 'base', 'ext', 'path'])


def create_filenames(filenames, root):
    '''
    Makes a generator that yields Filename objects

    Filename objects are a helper to allow multiple representations
    of the same file to be transferred cleanly.
    '''
    logger.info("Creating Filename objects")
    for filename in filenames:
        yield Filename(filename, *os.path.splitext(filename),
                       path=os.path.join(root, filename))


def generate_checksum(filename):
    '''
    A helper function that will generate the
    check sum of a file.
    '''
    logger.info("Generating checksum for {0}".format(filename))
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
            md5.update(chunk)
    return md5.digest()


def is_substring(string1, string2):
    '''
    Returns a match if one string is a substring of the other

    For example::

        is_substring('this', 'this1') -> True
        is_substring('that1', 'that') -> True

    But::

        is_substring('that', 'this')  -> False

    '''
    return string1 in string2 or string2 in string1


def pick_shorter_name(file1, file2):
    ''' 
    This convenience function will help to find the shorter (often better)
    filename.  If the file names are the same length it returns the file
    that is less, hoping for numerically.

    It picks "file.txt" over "file (1).txt", but beware it also picks
    "f.txt" over "file.txt".
    
    It also picks "file (1).txt" over "file (2).txt"
    '''
    logger.debug("Finding the shortest of {0} and {1}".format(file1.name,
                                                              file2.name))
    if len(file1.name) > len(file2.name):
        return file2
    elif len(file1.name) < len(file2.name) or file1.name < file2.name:
        return file1
    else:
        return file2


def ask_for_best(default, rest):
    hashes = [default] + list(rest)
    for num, hash in enumerate(hashes):
        if hash == default:
            print("{0}. {1} (default)".format(num, hash.name))
        else:
            print("{0}. {1}".format(num, hash.name))

    try:
        while True:
            result = input('Pick which file to keep (^C to skip): ')
            if result == '':
                best = default
                break
            elif result.isdigit() and int(result) in range(len(hashes)):
                best = hashes[int(result)]
                break
            elif result in [file.name for file in hashes]:
                best = [file for file in hashes if file.name == result][0]
                break
        rest = set(hashes) - {best}
        logger.warning('User picked {0} over {1}'.format(best, default))

    except KeyboardInterrupt:
        print('\nSkipped')
        logger.warning('User skipped in interactive mode')
        best = default
        rest = {}

    finally:
        return best, rest


def generate_checksum_dict(filenames):
    '''
    This function will create a dictionary of checksums mapped to
    a list of filenames.
    '''
    logger.info("Generating dictionary based on checksum")
    checksum_dict = defaultdict(set)

    for filename in filenames:
        checksum_dict[generate_checksum(filename.path)].add(filename)

    return checksum_dict


def generate_filename_dict(filenames, regex=r'(^.+?)(?: \(\d\))*(\..+)$'):
    '''
    This function will create a dictionary of filename parts mapped to a list
    of the real filenames.
    '''
    logger.info("Generating dictionary based on regular expression")
    filename_dict = defaultdict(set)

    regex = re.compile(regex)

    for filename in filenames:
        match = regex.match(filename.name)
        if match:
            logger.debug('Regex groups for {0}: {1}'.format(
                filename.name, str(match.groups())))
            filename_dict[match.groups()].add(filename)

    return filename_dict


def remove_by_checksum(list_of_names, no_action, interactive):
    '''
    This function first groups the files by checksum, and then removes all
    but one copy of the file.
    '''
    hashes = generate_checksum_dict(list_of_names)
    for hash in hashes:
        if len(hashes[hash]) > 1:
            logger.info("Investigating duplicate checksum {0}".format(hash))
            logger.debug("Keys for {0} are {1}".format(hash, ', '.join([
                item.name for item in hashes[hash]
            ])))
            best = functools.reduce(pick_shorter_name, hashes[hash])
            rest = hashes[hash] - {best}

            if interactive:
                best, rest = ask_for_best(best, rest)

            for bad in rest:
                if no_action:
                    print('{0} would have been deleted'.format(bad.path))
                    logger.info('{0} would have been deleted'.format(bad.path))
                else:
                    logger.info('{0} was deleted'.format(bad.path))
                    os.remove(bad.path)
            logger.info('{0} was kept as only copy'.format(best.path))

        else:
            logger.debug(
                'Skipping non duplicate checksum {0} for key {1}'.format(
                    hash, ', '.join([item.name for item in hashes[hash]])))


def walk_path(path, no_action, recursive, skip_regex, regex_pattern,
              interactive):
    '''
    This function steps through the directory structure and identifies
    groups for more in depth investigation.
    '''
    for root, dirs, filenames in os.walk(path):
        if not recursive and root != path:
            logger.debug("Skipping child directory {0}".format(root))
            continue

        if not skip_regex:
            names = generate_filename_dict(create_filenames(filenames, root),
                                           regex_pattern)

            for name in names:
                if len(names[name]) > 1:
                    logger.info("Investigating duplicate name {0}".format(name))
                    logger.debug("Keys for {0} are {1}".format(
                        name, ', '.join([item.name for item in names[name]])))
                    remove_by_checksum(names[name], no_action, interactive)
                else:
                    logger.debug(
                        'Skipping non duplicate name {0} for key {1}'.format(
                            name, ', '.join([item.name
                                             for item in names[name]])))
        else:
            remove_by_checksum(create_filenames(filenames, root), no_action,
                               interactive)


def main():
    '''
        The main function handles all the parsing of arguments.
    '''
    epilog = '''
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
                        default=0,
                        help='set print debug level')
    parser.add_argument('--log-file', help='write to log file.')
    parser.add_argument('--log-level',
                        type=int,
                        default=3,
                        help='set log file debug level')
    parser.add_argument('-p', '--pattern',
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

    args = parser.parse_args()

    if args.log_level != 3 and not args.log_file:
        parser.error('Log level set without log file')

    if args.pattern != r'(^.+?)(?: \(\d\))*(\..+)$' and args.skip_regex:
        parser.error('Pattern set while skipping regex checking')

    stream = logging.StreamHandler()
    stream.setLevel((5 - args.verbosity) * 10)
    formatter_simple = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')
    stream.setFormatter(formatter_simple)
    logger.addHandler(stream)
    logger.setLevel(logging.DEBUG)

    if args.log_file:
        log_file = logging.FileHandler(args.log_file)
        log_file.setFormatter(formatter_simple)
        log_file.setLevel((5 - args.log_level) * 10)
        logger.addHandler(log_file)

    logger.debug("Args: {0}".format(args))

    walk_path(args.path, args.no_action, args.recursive, args.skip_regex,
              args.pattern, args.interactive)


if __name__ == '__main__':
    main()
