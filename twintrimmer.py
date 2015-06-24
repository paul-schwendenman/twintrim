#! /usr/bin/env python3
import os
import hashlib
import argparse
import functools
import re
import logging
from collections import defaultdict, namedtuple

logger = logging.getLogger('')

Filename = namedtuple('Filename', ['name', 'base', 'ext', 'path'])


def create_filenames(filenames, root):
    '''
    Makes a generator that yields Filename objects

    Filename objects are a helper to allow multiple representations
    of the same file to be transfered cleanly.
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


def generate_filename_dict(filenames):
    '''
    This function will create a dictionary of filename parts mapped to a list
    of the real filenames.
    '''
    logger.info("Generating dictionary based on regular expression")
    filename_dict = defaultdict(set)

    regex = re.compile(r'(^.+?)( \((\d)\))*(\..+)$')

    for filename in filenames:
        match = regex.match(filename.name)
        if match:
            logger.debug('Regex groups for {0}: {1}'.format(
                filename.name, str(match.groups())))
            logger.info("Found a match for {0} adding to key {1}".format(
                filename.name, ''.join(match.group(1, 4))))
            filename_dict[''.join(match.group(1, 4))].add(filename)

    return filename_dict


def remove_by_checksum(list_of_names, no_action):
    hashes = generate_checksum_dict(list_of_names)
    for hash in hashes:
        if len(hashes[hash]) > 1:
            logger.info("Investigating duplicate checksum {0}".format(hash))
            logger.debug("Keys for {0} are {1}".format(hash, ', '.join([
                item.name for item in hashes[hash]
            ])))
            best = functools.reduce(pick_shorter_name, hashes[hash])
            for bad in hashes[hash] - {best}:
                if no_action:
                    print('{0} to be deleted'.format(bad.name))
                    logger.info('{0} would have been deleted'.format(bad.name))
                else:
                    logger.info('{0} was deleted'.format(bad.name))
                    os.remove(bad.path)
            logger.info('{0} was kept as only copy'.format(best.name))

        else:
            logger.debug(
                'Skipping non duplicate checksum {0} for key {1}'.format(
                    hash, ', '.join([item.name for item in hashes[hash]])))


def main(path, no_action, recursive, skip_regex):
    '''
    This function handles all options and steps through the directory
    '''
    for root, dirs, filenames in os.walk(path):
        if not recursive and root != path:
            logger.debug("Skipping child directory {0}".format(root))
            continue

        if not skip_regex:
            names = generate_filename_dict(create_filenames(filenames, root))

            for name in names:
                if len(names[name]) > 1:
                    logger.info("Investigating duplicate name {0}".format(name))
                    logger.debug("Keys for {0} are {1}".format(
                        name, ', '.join([item.name for item in names[name]])))
                    remove_by_checksum(names[name], no_action)
                else:
                    logger.debug(
                        'Skipping non duplicate name {0} for key {1}'.format(
                            name, ', '.join([item.name
                                             for item in names[name]])))
        else:
            remove_by_checksum(create_filenames(filenames, root), no_action)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'path',
        help='This is the path you want to run the checker against')
    parser.add_argument(
        '-n', '--no-action',
        default=False,
        action='store_true',
        help='This will print the output without changing anyfiles')
    parser.add_argument(
        '-r', '--recursive',
        default=False,
        action='store_true',
        help='This option toggles whether the program should search recursively')
    parser.add_argument('--verbosity',
                        type=int,
                        default=0,
                        help='Set debug level')
    parser.add_argument('--log-file',
                        help='This option sets a log file to write.')
    parser.add_argument('--log-level',
                        type=int,
                        default=3,
                        help='Set debug level in log file')
    parser.add_argument(
        '-c', '--only-checksum',
        default=False,
        action='store_true',
        dest='skip_regex',
        help=
        'This option toggles whether the program searches only by checksum rather than name first')

    args = parser.parse_args()

    if args.log_level != 3 and not args.log_file:
        parser.error('Log level set without log file')

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

    main(args.path, args.no_action, args.recursive, args.skip_regex)
