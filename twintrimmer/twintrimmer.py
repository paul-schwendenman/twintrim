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

class ClumperError(Exception):
    '''
    Base Exception for Clumper errors
    '''
    pass

class Clumper():
    '''
    general purpose class for grouping
    '''
    def __init__(self, *args, **kwargs):
        pass

    def make_clump(self, item):
        '''
        make a clump of the item
        '''
        raise NotImplementedError

    def dump_clumps(self, list_of_items):
        '''
        group list into clumps
        '''
        clumps = defaultdict(set)

        for item in list_of_items:
            try:
                clumps[self.make_clump(item)].add(item)
            except ClumperError as err:
                LOGGER.error(str(err))

        return clumps

class Sifter():
    '''
    general purpose class for dividing groups
    '''
    def __init__(self, *args, **kwargs):
        pass

    def sift(self, clump, best=None):
        '''
        divide the clumps returning the best and the rest
        '''
        raise NotImplementedError

    def filter(self, dictionary_of_groups):
        '''
        helper function for filtering clumps
        '''
        raise NotImplementedError


class HashClumper(Clumper):
    '''
    Subclass of Clumper using hash algorithms
    '''
    def __init__(self, hash_name):
        super(HashClumper, self).__init__()
        self.hash_func = hashlib.new(hash_name)


    def make_clump(self, filename):
        hash_func = self.hash_func.copy()

        try:
            with open(filename, 'rb') as file:
                for chunk in iter(lambda: file.read(128 * hash_func.block_size), b''):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except OSError as err:
            raise ClumperError('Checksum generation error: %s', err)

class RegexClumper(Clumper):
    '''
    Subclass of Clumper using regular expressions
    '''
    def __init__(self, expr):
        super(RegexClumper, self).__init__()
        self.regex = re.compile(expr)

    def make_clump(self, filename):
        match = regex.match(filename.name)
        if not match:
            raise ClumperError('No regex match found for %s' % (filename.path))

        return match.groups()


class ShortestSifter(Sifter):
    def __init__(self, *args, **kwargs):
        super(ShortestSifter, self).__init__(*args, **kwargs)

    def sift(self, clump):
        best = functools.reduce(self.pick_shorter_name, clump)
        rest = clump - {best}
        return best, rest

    @staticmethod
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

class InteractiveSifter(ShortestSifter):
    '''
    This class allows the user to interactively select which file is
    selected to be preserved.
    '''
    def __init__(self, *args, **kwargs):
        super(InteractiveSifter, self).__init__(*args, **kwargs)

    def sift(self, clump):
        '''
        Asks user for best after giving recommendation
        '''
        default, rest = super(InteractiveSifter, self).sift(clump)
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


def remove_by_checksum(list_of_names, sifter,
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
            best, rest = sifter.sift(files[file])

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
    if options.get('interactive', False):
        sifter = InteractiveSifter()
    else:
        sifter = ShortestSifter()

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
                    remove_by_checksum(names[name], sifter, **options)
                else:
                    LOGGER.debug('Skipping non duplicate name %s for key %s',
                                 name, ', '.join([item.name
                                                  for item in names[name]]))
        else:
            remove_by_checksum(create_filenames(filenames, root), sifter, **options)
