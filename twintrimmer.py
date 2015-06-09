#! /usr/bin/env python3
import os
import hashlib
import argparse
import itertools
import re
import logging
from collections import defaultdict, namedtuple

logger = logging.getLogger('')

Filename = namedtuple('Filename', ['name', 'base', 'ext', 'path'])


def create_filenames(filenames, root):
    '''
    Makes a genrator that yields Filename objects

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
    length = min(len(string1), len(string2))
    logger.debug("Testing {0}[{1}] and {2}[{3}] -> {4}".format(
        string1[:length], string1[length:], string2[:length], string2[length:],
        string1[:length] == string2[:length]))
    return string1[:length] == string2[:length]


def compare_filename_name(file1, file2):
    '''
    Uses is_substring to determine if both base and extension match.
    '''
    logger.info("Comparing {0} and {1} by substring".format(file1.path,
                                                            file2.path))
    return is_substring(file1.base, file2.base) and is_substring(file1.ext,
                                                                 file2.ext)


def compare_filename_checksum(file1, file2):
    '''
    Uses the generate_checksum function to compare two files
    '''
    logger.info("Comparing {0} and {1} by checksum".format(file1.path,
                                                           file2.path))
    return generate_checksum(file1.path) == generate_checksum(file2.path)


def pick_basename(file1, file2):
    '''
    This convience will help to find the shorter (often better) filename

    It picks "file.txt" over "file (1).txt", but beware it also picks
    "f.txt" over "file.txt".
    '''
    logger.debug("Finding the shortest of {0} and {1}".format(file1.name,
                                                              file2.name))
    if len(file1.name) > len(file2.name):
        return file2, file1
    else:
        return file1, file2


def generate_checksum_dict(filenames):
    '''
    This function will create a dictionary of checksums mapped to
    a list of filenames.
    '''
    logger.info("Generating dictionary based on checksum")
    checksum_dict = defaultdict(list)

    for filename in filenames:
        checksum_dict[generate_checksum(filename.path)].append(filename)

    return checksum_dict


def generate_filename_dict(filenames):
    '''
    This function will create a dictionary of filename parts mapped to a list
    of the real filenames.
    '''
    logger.info("Generating dictionary based on regular expression")
    filename_dict = defaultdict(list)

    regex = re.compile(r'(^.+?)( \((\d)\))*(\..+)$')

    for filename in filenames:
        match = regex.match(filename.name)
        if match:
            logger.debug('Regex groups for {0}: {1}'.format(
                filename.name, str(match.groups())))
            logger.info("Found a match for {0} adding to key {1}".format(
                filename.name, ''.join(match.group(1, 4))))
            filename_dict[''.join(match.group(1, 4))].append(filename)

    return filename_dict


def main(path, no_action, recursive, generate_dict, compare_filename):
    '''
    This function handles all options and steps through the directory
    '''
    for root, dirs, filenames in os.walk(path):
        if not recursive and root != path:
            logger.debug("Skipping child directory {0}".format(root))
            continue
        hashes = generate_dict(create_filenames(filenames, root))

        for hash in hashes:
            if len(hashes[hash]) > 1:
                logger.info("Investigating duplicate hash {0}".format(hash))
                logger.debug("Keys for {0} are {1}".format(
                    hash, ', '.join([item.name for item in hashes[hash]])))
                for pair in itertools.combinations(hashes[hash], 2):
                    if compare_filename(*pair):
                        orig, dup = pick_basename(*pair)
                        if no_action:
                            print('{1} to be deleted'.format(orig.name,
                                                             dup.name))
                            logger.info('{1} would have been deleted'.format(
                                orig.name, dup.name))
                        else:
                            logger.info('{1} was deleted'.format(orig.name,
                                                                 dup.name))
                            os.remove(dup.path)
                    else:
                        logger.info('Files {0} and {1} did not match'.format(
                            pair[0].name, pair[1].name))
            else:
                logger.debug(
                    'Skipping non duplicate hash {0} for key {1}'.format(
                        hash, ', '.join([item.name for item in hashes[hash]])))


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
    parser.add_argument(
        '-c', '--checksum',
        default=False,
        action='store_true',
        help=
        'This option toggles whether the program searchs first by checksum rather than name')
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

    if args.checksum:
        main(args.path, args.no_action, args.recursive, generate_checksum_dict,
             compare_filename_name)
    else:
        main(args.path, args.no_action, args.recursive, generate_filename_dict,
             compare_filename_checksum)
