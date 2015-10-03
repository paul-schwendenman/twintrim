#! /usr/bin/env python3
'''
tool for removing duplicate files
'''
import argparse
import functools
import hashlib
import logging
import os
import re
import sys
import textwrap
from collections import defaultdict, namedtuple

LOGGER = logging.getLogger(__name__)

Filename = namedtuple('Filename', ['name', 'base', 'ext', 'path'])


def create_filenames(filenames, root):
    '''
    Makes a generator that yields Filename objects

    Filename objects are a helper to allow multiple representations
    of the same file to be transferred cleanly between functions.

    :param filenames: list of filenames
    :type filenames: iterable[str]
    :param root: the parent directory of the filenames
    :type root: str
    :returns: Filename instance representing each filename
    :rtype: Filename
    '''
    LOGGER.info("Creating Filename objects")
    for filename in filenames:
        yield Filename(filename, *os.path.splitext(filename),
                       path=os.path.join(root, filename))


def generate_checksum(filename, hash_name='md5'):
    '''
    A helper function that will generate the checksum of a file.

    :param filename: path to a file
    :type filename: str
    :param hash_name: hash algorithm to use for checksum generation
    :type hash_name: str
    :returns: the checksum in a hex form
    :rtype: str

    According to the hashlib documentation:

    - hashlib.sha1 should be prefered over hashlib.new('sha1')
    - the list of available function will change depending on the openssl
      library
    - the same function might exist with multiple spellings i.e. SHA1 and sha1

    >>> from timeit import repeat
    >>> repeat("sha1 = hashlib.sha1();"
               "sha1.update(b'this is a bunch of text');"
               "sha1.hexdigest()",
               setup="import hashlib;", number=1000000, repeat=3)
    [1.1151904039998044, 1.107502792001469, 1.1114749459993618]
    >>> repeat("sha1 = hashlib.new('sha1');"
               "sha1.update(b'this is a bunch of text');"
               "sha1.hexdigest()",
               setup="import hashlib;", number=1000000, repeat=3)
    [1.9987542880007823, 1.9930373919996782, 1.9749872180000239]
    >>> repeat("sha1.update(b'this is a bunch of text'); sha1.hexdigest()",
               setup="import hashlib; sha1 = hashlib.new('sha1')",
               number=100000, repeat=3)
    [0.09824231799939298, 0.09060508599941386, 0.08991972700096085]
    >>> repeat("sha1.update(b'this is a bunch of text'); sha1.hexdigest()",
               setup="import hashlib; sha1 = hashlib.sha1()",
               number=100000, repeat=3)
    [0.0977191860001767, 0.09078196100017522, 0.09082681499967293]
    '''
    LOGGER.info("Generating checksum with %s for %s", hash_name, filename)

    if hash_name.lower() in ('md5', 'MD5'):
        hash_func = hashlib.md5()
    elif hash_name.lower() in ('sha1', 'SHA1'):
        hash_func = hashlib.sha1()
    elif hash_name.lower() in ('sha256', 'SHA256'):
        hash_func = hashlib.sha256()
    elif hash_name.lower() in ('sha512', 'SHA512'):
        hash_func = hashlib.sha512()
    elif hash_name.lower() in ('sha224', 'SHA224'):
        hash_func = hashlib.sha224()
    elif hash_name.lower() in ('sha384', 'SHA384'):
        hash_func = hashlib.sha384()
    else:
        hash_func = hashlib.new(hash_name)

    with open(filename, 'rb') as file:
        for chunk in iter(lambda: file.read(128 * hash_func.block_size), b''):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def is_substring(string1, string2):
    '''
    Returns a match if one string is a substring of the other

    :param str string1: the first string to compare
    :param str string2: the second string to compare
    :returns: True if either string is substring of the other
    :rtype: bool

    For example:

    >>> is_substring('this', 'this1')
    True
    >>> is_substring('that1', 'that')
    True
    >>> is_substring('that', 'this')
    False
    '''
    return string1 in string2 or string2 in string1


def pick_shorter_name(file1, file2):
    '''
    This convenience function will help to find the shorter (often better)
    filename.  If the file names are the same length it returns the file
    that is less, hoping for numerically.

    :param file1: first filename to compare
    :type file1: Filename
    :param file2: second filename to compare
    :type file2: Filename
    :returns: the shortest name
    :rtype: Filename

    It picks "file.txt" over "file (1).txt", but beware it also picks
    "f.txt" over "file.txt".

    It also picks "file (1).txt" over "file (2).txt"

    >>> file1 = Filename('file.txt', 'file', '.txt', '/file.txt')
    >>> file2 = Filename('file (1).txt', 'file (1)', '.txt', '/file (1).txt')
    >>> file3 = Filename('file (2).txt', 'file (2)', '.txt', '/file (2).txt')
    >>> pick_shorter_name(file1, file2)
    Filename(name='file.txt', base='file', ext='.txt', path='/file.txt')
    >>> pick_shorter_name(file2, file1)
    Filename(name='file.txt', base='file', ext='.txt', path='/file.txt')
    >>> pick_shorter_name(file2, file3)
    Filename(name='file (1).txt', base='file (1)', ext='.txt', path='/file (1).txt')
    '''
    LOGGER.debug("Finding the shortest of %s and %s", file1.name, file2.name)
    if len(file1.name) > len(file2.name):
        return file2
    elif len(file1.name) < len(file2.name) or file1.name < file2.name:
        return file1
    else:
        return file2


def ask_for_best(default, rest):
    '''
    This function allows the user to interactively select which file is
    selected to be preserved.

    :param default: Filename object that would normally be kept
    :type default: Filename
    :param rest: Other matching filenames to offer as options to be kept,
                    they are all going to be deleted
    :type rest: set(Filename)

    :returns: (best, rest):
    :rtype: (Filename, set(Filename))
    '''
    files = [default] + list(rest)
    for num, file in enumerate(files):
        if file == default:
            print("{0}. {1} (default)".format(num, file.name))
        else:
            print("{0}. {1}".format(num, file.name))

    try:
        while True:
            result = input('Pick which file to keep (^C to skip): ')
            if result == '':
                best = default
                break
            elif result.isdigit() and int(result) in range(len(files)):
                best = files[int(result)]
                break
            elif result in [file.name for file in files]:
                best = [file for file in files if file.name == result][0]
                break
        rest = set(files) - {best}
        LOGGER.warning('User picked %s over %s', best, default)

    except KeyboardInterrupt:
        print('\nSkipped')
        LOGGER.warning('User skipped in interactive mode')
        best = default
        rest = {}

    return best, rest


def generate_checksum_dict(filenames, hash_name):
    '''
    This function will create a dictionary of checksums mapped to
    a list of filenames.

    :param filenames: list of filenames to clump by checksum
    :type filenames: iterable[Filename]
    :param str hash_name: name of hash function used to generate checksum

    :returns: dictionary of sets of Filename objects with their checksum as
              the key
    '''
    LOGGER.info("Generating dictionary based on checksum")
    checksum_dict = defaultdict(set)

    for filename in filenames:
        try:
            checksum_dict[generate_checksum(filename.path,
                                            hash_name)].add(filename)
        except OSError as err:
            LOGGER.error('Checksum generation error: %s', err)

    return checksum_dict


def generate_filename_dict(filenames, expr=None):
    '''
    This function will create a dictionary of filename parts mapped to a list
    of the real filenames.

    :param filenames: list of filenames to clump by filename
                      parts
    :type filenames: iterable[Filename]
    :param str expr: regex pattern to break and group the filename string

    :returns: dictionary of sets of Filename objects with their regex matches
              as the key
    '''
    LOGGER.info("Generating dictionary based on regular expression")
    filename_dict = defaultdict(set)

    if expr is None:
        expr = r'(^.+?)(?: \(\d\))*(\..+)$'
    regex = re.compile(expr)

    for filename in filenames:
        match = regex.match(filename.name)
        if match:
            LOGGER.debug('Regex groups for %s: %s', filename.name,
                         str(match.groups()))
            filename_dict[match.groups()].add(filename)

    return filename_dict


def remove_files_for_deletion(bad, best, **options):
    '''
    Preform the deletion of file that has been identified as a duplicate

    :param Filename bad: the file to be deleted
    :param Filename best: the file that was kept instead of 'bad'
    :param bool remove_links: causes function to check if best and bad
                             are hardlinks before deletion
    :param bool no_action: show what files would have been deleted.
    :param bool make_links: create a hard link to best from path bad,
                           after bad is deleted
    :raises OSError: when error occurs modifing the file
    '''
    if not options['remove_links'] and os.path.samefile(best.path, bad.path):
        LOGGER.info('hard link skipped %s', bad.path)
    elif options['no_action']:
        print('{0} would have been deleted'.format(bad.path))
        LOGGER.info('%s would have been deleted', bad.path)
    else:
        os.remove(bad.path)
        LOGGER.info('%s was deleted', bad.path)
        if options.get('make_links', False):
            LOGGER.info('hard link created: %s', bad.path)
            os.link(best.path, bad.path)


def remove_by_checksum(list_of_names,
                       interactive=False,
                       hash_name='sha1', **options):
    '''
    This function first groups the files by checksum, and then removes all
    but one copy of the file.

    :param list_of_names: list of objects to remove
    :type list_of_names:  iterable[Filename]
    :param bool interactive: allow the user to pick which file to keep
    :param str hash_name: the name of the hash function used to compute the
                         checksum

    '''
    files = generate_checksum_dict(list_of_names, hash_name)
    for file in files:
        if len(files[file]) > 1:
            LOGGER.info("Investigating duplicate checksum %s", file)
            LOGGER.debug("Keys for %s are %s", file,
                         ', '.join([item.name for item in files[file]]))
            best = functools.reduce(pick_shorter_name, files[file])
            rest = files[file] - {best}

            if interactive:
                best, rest = ask_for_best(best, rest)

            for bad in rest:
                try:
                    remove_files_for_deletion(bad, best, **options)
                except OSError as err:
                    LOGGER.error('File deletion error: %s', err)
            LOGGER.info('%s was kept as only copy', best.path)

        else:
            LOGGER.debug('Skipping non duplicate checksum %s for key %s', file,
                         ', '.join([item.name for item in files[file]]))


def walk_path(path, **options):
    '''
    This function steps through the directory structure and identifies
    groups for more in depth investigation.

    :param str path: the path to search for files and begin processing
    '''
    for root, _, filenames in os.walk(path):
        if not options['recursive'] and root != path:
            LOGGER.debug("Skipping child directory %s of %s", root, path)
            continue

        if not options['skip_regex']:
            names = generate_filename_dict(create_filenames(filenames, root),
                                           options['regex_pattern'])

            for name in names:
                if len(names[name]) > 1:
                    LOGGER.info("Investigating duplicate name %s", name)
                    LOGGER.debug("Keys for %s are %s", name,
                                 ', '.join([item.name
                                            for item in names[name]]))
                    remove_by_checksum(names[name], **options)
                else:
                    LOGGER.debug('Skipping non duplicate name %s for key %s',
                                 name, ', '.join([item.name
                                                  for item in names[name]]))
        else:
            remove_by_checksum(create_filenames(filenames, root), **options)

def main(args_param=None):
    '''
    The main function handles the parsing of arguments as well as the
    initiation of the logging handlers.

    positional arguments:
      path                  path to check

    optional arguments:
      -h, --help            show this help message and exit
      -n, --no-action       show what files would have been deleted
      -r, --recursive       search directories recursively
      --verbosity VERBOSITY
                            set print debug level
      --log-file LOG_FILE   write to log file.
      --log-level LOG_LEVEL
                            set log file debug level
      -p PATTERN, --pattern PATTERN
                            set filename matching regex
      -c, --only-checksum   toggle searching by checksum rather than name first
      -i, --interactive     ask for file deletion interactively
      --hash-function
                            {'sha224', 'sha384', 'sha1', 'md5', 'sha512', 'sha256'}
                            set hash function to use for checksums
      --make-link           create hard link rather than remove file
      --remove-links        remove hardlinks rather than skipping
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

    args = parser.parse_args(args_param)

    if not os.path.isdir(args.path):
        print(args.path)
        parser.error('path was not a directory: "{0}"'.format(args.path))

    if args.log_level != 3 and not args.log_file:
        parser.error('Log level set without log file')

    if args.regex_pattern != r'(^.+?)(?: \(\d\))*(\..+)$' and args.skip_regex:
        parser.error('Pattern set while skipping regex checking')

    try:
        re.compile(args.regex_pattern)
    except re.error:
        parser.error('Invalid regular expression: "{0}"'.format(args.regex_pattern))

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
    main()
