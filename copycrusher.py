#! /usr/bin/env python3
import os
import hashlib
import argparse
import itertools
import re
from collections import defaultdict, namedtuple

Filename = namedtuple('Filename', ['name', 'base', 'ext', 'path'])

def create_filenames(filenames, root):
    for filename in filenames:
        yield Filename(filename, *os.path.splitext(filename), path=os.path.join(root, filename))


def generate_checksum(filename):
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
            md5.update(chunk)
    return md5.digest()


def is_substring(string1, string2):
    length = min(len(string1), len(string2))
    return string1[:length] == string2[:length]


def compare_filename_name(file1, file2):
    return is_substring(file1.base, file2.base) and is_substring(
        file1.ext, file2.ext)


def compare_filename_checksum(file1, file2):
    return generate_checksum(file1.path) == generate_checksum(file2.path)


def pick_basename(file1, file2):
    if len(file1.name) > len(file2.name):
        return file2, file1
    else:
        return file1, file2

def generate_checksum_dict(filenames):
    checksum_dict = defaultdict(list)

    for filename in filenames:
        checksum_dict[generate_checksum(filename.path)].append(filename)

    return checksum_dict


def generate_filename_dict(filenames):
    filename_dict = defaultdict(list)

    regex = re.compile(r'(^.+?)( \((\d)\))*(\..+)$')

    for filename in filenames:
        match = regex.match(filename.name)
        if match:
            filename_dict[''.join(match.group(1, 4))].append(filename)

    return filename_dict


def main(path, no_action, recursive, generate_dict, compare_filename):
    from pprint import pprint

    for root, dirs, filenames in os.walk(path):
        if not recursive and root != path:
            continue
        hashes = generate_dict(create_filenames(filenames, root))

        for hash in hashes:
            if len(hashes[hash]) > 1:
                for pair in itertools.combinations(hashes[hash], 2):
                    if compare_filename(*pair):
                        orig, dup = pick_basename(*pair)
                        if no_action:
                            print('{1} deleted'.format(orig.name, dup.name))
                            #print('{1} deleted. {0} kept'.format(orig.name, dup.name))
                        else:
                            os.remove(dup.path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--path', required=True,
        help='This is the path you want to run the checker against')
    parser.add_argument(
        '-n', '--no-action', default=False, action='store_true',
        help='This will print the output without changing anyfiles')
    parser.add_argument(
        '-r', '--recursive', default=False, action='store_true',
        help='This option toggles whether the program should search recursively')
    parser.add_argument(
        '-c', '--checksum', default=False, action='store_true',
        help='This option toggles whether the program searchs first by checksum rather than name')
    args = parser.parse_args()

    if args.checksum:
        main(args.path, args.no_action, args.recursive, generate_checksum_dict, compare_filename_name)
    else:
        main(args.path, args.no_action, args.recursive, generate_filename_dict, compare_filename_checksum)
