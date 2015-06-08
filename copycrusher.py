#! /usr/bin/env python3
import os
import hashlib
import argparse
import itertools
from collections import defaultdict, namedtuple

Filename = namedtuple('Filename', ['name', 'ext'])


def generate_checksum(filename):
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
            md5.update(chunk)
    return md5.digest()


def is_substring(string1, string2):
    length = min(len(string1), len(string2))
    return string1[:length] == string2[:length]


def compare_filename(file1, file2):
    filename1 = Filename(*os.path.splitext(file1))
    filename2 = Filename(*os.path.splitext(file2))

    return is_substring(filename1.name, filename2.name) and is_substring(
        filename1.ext, filename2.ext)


def pick_basename(file1, file2):
    if len(file1) > len(file2):
        return file2, file1
    else:
        return file1, file2

def generate_checksum_dict(root, filenames):
    checksum_dict = defaultdict(list)

    for filename in filenames:
        checksum_dict[generate_checksum(
            os.path.join(root, filename))].append(filename)

    return checksum_dict


def main(path):
    from pprint import pprint

    for root, dirs, filenames in os.walk(path):
        hashes = generate_checksum_dict(root, filenames)
        #pprint(hashes)

        for hash in hashes:
            if len(hashes[hash]) > 1:
                for pair in itertools.combinations(hashes[hash], 2):
                    if compare_filename(*pair):
                        print(pick_basename(*pair))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--path', required=True,
        help='This is the path you want to run the checker against')
    args = parser.parse_args()

    main(args.path)
