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

    def dump_clumps(self, clumper):
        '''
        group list into clumps
        '''
        clumps = defaultdict(set)

        for key, value in clumper.items():
            for item in value:
                try:
                    clumps[key + self.make_clump(item)].add(item)
                except ClumperError as err:
                    LOGGER.error(str(err))

        return clumps

class Sifter():
    '''
    general purpose class for dividing groups
    '''
    def __init__(self, *args, **kwargs):
        pass

    def sift(self, clump):
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
            with open(filename.path, 'rb') as file:
                for chunk in iter(lambda: file.read(128 * hash_func.block_size), b''):
                    hash_func.update(chunk)
            return (hash_func.hexdigest(),)
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
        match = self.regex.match(filename.name)
        if not match:
            raise ClumperError('No regex match found for %s' % (filename.path))
        else:
            LOGGER.debug('Regex groups for %s: %s', filename.name,
                         str(match.groups()))

        return match.groups()

class PathClumper(Clumper):
    def __init__(self, root_path, recursive=False):
        super(PathClumper, self).__init__()
        self.root_path = root_path
        self.recursive = recursive

    def make_clump(self, path):
        return (path,)

    def dump_clumps(self, clumper=None):
        if clumper is not None:
            raise NotImplementedError
        clumps = {}

        for path, _, filenames in os.walk(self.root_path):
            if not self.recursive and path != self.root_path:
                LOGGER.debug("Skipping child directory %s of %s", path, self.root_path)
                continue
            clumps[self.make_clump(path)] = self.create_filenames(filenames, path)
        return clumps

    @staticmethod
    def create_filename(filename, root):
        return Filename(filename, *os.path.splitext(filename),
                       path=os.path.join(root, filename))

    @classmethod
    def create_filenames(cls, filenames, root):
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
            yield cls.create_filename(filename, root)



class ShortestSifter(Sifter):
    '''
    Used to separate the shortest name from the rest
    '''
    def __init__(self, *args, **kwargs):
        super(ShortestSifter, self).__init__(*args, **kwargs)

    def sift(self, clump):
        best = functools.reduce(self.pick_shorter_name, clump)
        rest = clump - {best}
        return best, rest

    def filter(self, dictionary_of_groups):
        '''
        helper function for filtering clumps
        '''
        raise NotImplementedError

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

    def filter(self, dictionary_of_groups):
        '''
        helper function for filtering clumps
        '''
        raise NotImplementedError

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


def remove_file(bad, best, **options):
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


def remove_by_clump(dict_of_names, sifter, **options):
    '''
    This function first groups the files by checksum, and then removes all
    but one copy of the file.

    :param list_of_names: list of objects to remove
    :type list_of_names:  iterable[Filename]
    :param bool interactive: allow the user to pick which file to keep
    :param str hash_name: the name of the hash function used to compute the
                         checksum

    '''
    for file in dict_of_names:
        if len(dict_of_names[file]) > 1:
            LOGGER.info("Investigating duplicate key %s", file)
            LOGGER.debug("Values for key %s are %s", file,
                         ', '.join([item.name for item in dict_of_names[file]]))
            best, rest = sifter.sift(dict_of_names[file])

            for bad in rest:
                try:
                    remove_file(bad, best, **options)
                except OSError as err:
                    LOGGER.error('File deletion error: %s', err)
            LOGGER.info('%s was kept as only copy', best.path)

        else:
            LOGGER.debug('Skipping non duplicate checksum %s for key %s', file,
                         ', '.join([item.name for item in dict_of_names[file]]))


def main(path, **options):
    '''
    This function steps through the directory structure and identifies
    groups for more in depth investigation.

    :param str path: the path to search for files and begin processing
    '''
    if options.get('interactive', False):
        sifter = InteractiveSifter()
    else:
        sifter = ShortestSifter()

    checksum_clumper = HashClumper(options['hash_function'])
    filepath_clumper = PathClumper(path, options['recursive'])

    clumps = filepath_clumper.dump_clumps()

    if not options['skip_regex']:
        regex_clumper = RegexClumper(options['regex_pattern'])
        clumps = regex_clumper.dump_clumps(clumps)

    clumps = checksum_clumper.dump_clumps(clumps)
    remove_by_clump(clumps, sifter, **options)
