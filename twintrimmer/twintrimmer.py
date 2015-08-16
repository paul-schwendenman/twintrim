'''
duplicate file remover
'''
import os
import hashlib
import functools
import re
import logging
from collections import defaultdict, namedtuple

LOGGER = logging.getLogger(__name__)

Filename = namedtuple('Filename', ['name', 'base', 'ext', 'path'])


def create_filenames(filenames, root):
    '''
    Makes a generator that yields Filename objects

    Filename objects are a helper to allow multiple representations
    of the same file to be transferred cleanly between functions.

    Args:
        filenames (iterable[str]): list of filenames
        root (str): the parent directory of the filenames
    Yields:
        Filename instance representing each filename
    '''
    LOGGER.info("Creating Filename objects")
    for filename in filenames:
        yield Filename(filename, *os.path.splitext(filename),
                       path=os.path.join(root, filename))


def generate_checksum(filename, hash_name='md5'):
    '''
    A helper function that will generate the checksum of a file.

    Args:
        filename (str): path to a file
    Kwargs:
        hash_name (str): hash algorithm to use for checksum generation
    Returns:
        str: the checksum in a hex form

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

    Args:
        string1 (str): the first string to compare
        string2 (str): the second string to compare

    Returns:
        bool: True if either string is substring of the other

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

    Args:
        file1 (Filename): first filename to compare
        file2 (Filename): second filename to compare

    Returns:
        Filename: the shortest name

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

    Args:
        default (Filename): Filename object that would normally be kept
        rest (set): Other matching filenames to offer as options to be kept,
                    they are all going to be deleted

    Returns:
        (best, rest):
            best:
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

    Args:
        filenames (iterable[Filename]): list of filenames to clump by checksum
        hash_name (str): name of hash function used to generate checksum

    Return value:
        dictionary of sets of Filename objects with their checksum as the key
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

    Args:
        filenames (iterable[Filename]): list of filenames to clump by filename
                                        parts
        expr (str): regex pattern to break and group the filename string

    Return value:
        dictionary of sets of Filename objects with their regex matches as the
        key
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

    Args:
        bad (Filename): the file to be deleted
        best (Filename): the file that was kept instead of 'bad'
    Kwargs:
        remove_links (bool): causes function to check if best and bad
                             are hardlinks before deletion
        no_action (bool): show what files would have been deleted.
        make_links (bool): create a hard link to best from path bad,
                           after bad is deleted
    Raises:
        OSError
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

    Args:
        list_of_names (iterable[Filename]): list of objects to remove
    Kwargs:
        interactive (bool): allow the user to pick which file to keep
        hash_name (str): the name of the hash function used to compute the
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

    Args:
        path (str): the path to search for files and begin processing
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
