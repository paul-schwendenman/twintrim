'''
Tests for the twintrimmer module
'''
# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
from io import StringIO
import unittest
import os
import sys
from unittest.mock import patch
from pyfakefs import fake_filesystem_unittest
import twintrimmer


class TestClumper(unittest.TestCase):
    def setUp(self):
        self.clumper = twintrimmer.twintrimmer.Clumper()

    def test_make_clump_is_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.clumper.make_clump('test')

    def test_dump_clumps_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.clumper.dump_clumps({('this'): {'one', 'two'}})

    def test_dump_clumps_raises_CClumpError(self):
        out = self.clumper.dump_clumps({(): {}})
        self.assertEqual(out, {})


class TestPicker(unittest.TestCase):
    def setUp(self):
        self.picker = twintrimmer.twintrimmer.Picker()

    def test_sift_is_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.picker.sift(None)


class TestPathClumper(unittest.TestCase):
    def setUp(self):
        self.clumper = twintrimmer.twintrimmer.PathClumper('/')

    def test_one_file(self):
        filenames = ['test_file.txt']
        root = '/'
        list_output = list(
            twintrimmer.twintrimmer.PathClumper.create_filenames_from_list(
                filenames, root))
        self.assertEqual(len(list_output), 1)
        self.assertIs(type(list_output[0]), twintrimmer.Filename)
        self.assertEqual(list_output[0].name, 'test_file.txt')
        self.assertEqual(list_output[0].base, 'test_file')
        self.assertEqual(list_output[0].ext, '.txt')
        self.assertEqual(list_output[0].path, '/test_file.txt')

    def test_dump_clumps_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.clumper.dump_clumps({('this'): {'one', 'two'}})

    def test_no_files(self):
        filenames = []
        root = '/'
        list_output = list(
            twintrimmer.twintrimmer.PathClumper.create_filenames_from_list(
                filenames, root))
        self.assertEqual(len(list_output), 0)


class TestHashClumper(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        path = '/test/lots/of/nonexistent/directories/full.txt'
        self.fs.CreateFile(path, contents='First line\nSecond Line\n')
        self.full = twintrimmer.Filename('full.txt', 'full', '.txt', path)
        self.fs.CreateFile('/test.txt', contents='First line\nSecond Line\n')
        self.fs.CreateFile('/test2.txt', contents='First line\nSecond Line\n')
        self.test = twintrimmer.Filename(None, None, None, '/test.txt')
        self.test2 = twintrimmer.Filename(None, None, None, '/test2.txt')
        self.nonexistent = twintrimmer.Filename(None, None, None, '/none.txt')

    def test_generate_sha1_checksum_for_file(self):
        clumper = twintrimmer.twintrimmer.HashClumper('sha1')

        checksum = clumper.make_clump(self.full)
        self.assertEqual(checksum,
                         ('5a0cd97a76759aafa9fd5e4c5aa2ffe0e6f1720d', ))

    def test_generate_md5_checksum_for_file(self):
        clumper = twintrimmer.twintrimmer.HashClumper('md5')

        checksum = clumper.make_clump(self.full)
        self.assertEqual(checksum, ('af55da6adb51f8dc6b4d3758b5bcf8cc', ))

    def test_generate_checksum_raises_OSError_for_missing_file(self):
        clumper = twintrimmer.twintrimmer.HashClumper('sha1')
        with self.assertRaises(twintrimmer.twintrimmer.ClumperError):
            clumper.make_clump(self.nonexistent)

    def test_generate_checksum_dict_from_list_of_one_file(self):
        clumper = twintrimmer.twintrimmer.HashClumper('sha1')
        checksum_dict = clumper.dump_clumps({(None, ): [self.test]})
        print(checksum_dict)
        filenames = checksum_dict[(None,
                                   '5a0cd97a76759aafa9fd5e4c5aa2ffe0e6f1720d')]
        self.assertEqual(len(filenames), 1)
        self.assertTrue(self.test in filenames)

    def test_generate_checksum_dict_from_list_of_two_matching_files(self):
        clumper = twintrimmer.twintrimmer.HashClumper('sha1')
        checksum_dict = clumper.dump_clumps(
            {(None, ): [self.test, self.test2]})
        filenames = checksum_dict[(None,
                                   '5a0cd97a76759aafa9fd5e4c5aa2ffe0e6f1720d')]
        self.assertEqual(len(filenames), 2)
        self.assertTrue(self.test in filenames)
        self.assertTrue(self.test2 in filenames)

    def test_generate_checksum_dict_handles_OSError(self):
        clumper = twintrimmer.twintrimmer.HashClumper('sha1')
        checksum_dict = clumper.dump_clumps({(None, ): [self.nonexistent]})
        filenames = checksum_dict[(None,
                                   '5a0cd97a76759aafa9fd5e4c5aa2ffe0e6f1720d')]
        self.assertEqual(len(filenames), 0)


class TestShortestPicker(unittest.TestCase):
    def setUp(self):
        filenames = ['file.txt', 'file1.txt', 'file2.txt']
        root = '/'
        self.file, self.file1, self.file2 = list(
            twintrimmer.twintrimmer.PathClumper.create_filenames_from_list(
                filenames, root))
        self.filenames = {self.file, self.file1, self.file2}
        self.picker = twintrimmer.twintrimmer.ShortestPicker()

    def test_file_txt_shorter_than_file_1_txt(self):
        self.assertEqual(self.picker.pick_shorter_name(self.file, self.file1),
                         self.file)

    def test_file_1_txt_shorter_than_file_2_txt(self):
        self.assertEqual(self.picker.pick_shorter_name(self.file1, self.file2),
                         self.file1)

    def test_file_1_txt_not_shorter_than_file_txt(self):
        self.assertEqual(self.picker.pick_shorter_name(self.file1, self.file),
                         self.file)

    def test_file_2_txt_not_shorter_than_file_1_txt(self):
        self.assertEqual(self.picker.pick_shorter_name(self.file2, self.file1),
                         self.file1)

    def test_sift_finds_shortest_name(self):
        best, rest = self.picker.sift(self.filenames)
        self.assertEqual(best, self.file)
        self.assertEqual(rest, {self.file1, self.file2})

class TestModificationPicker(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.fs.CreateFile('examples/file2.txt', contents='foobar\n')
        self.fs.CreateFile('examples/file1.txt', contents='foobar\n')
        self.fs.CreateFile('examples/file.txt', contents='foobar\n')
        filenames = ['file.txt', 'file1.txt', 'file2.txt']
        root = 'examples/'
        self.file, self.file1, self.file2 = list(
            twintrimmer.twintrimmer.PathClumper.create_filenames_from_list(
                filenames, root))
        self.change_modification_time(self.file2.path, 2)
        self.change_modification_time(self.file1.path, 1)
        self.filenames = {self.file, self.file1, self.file2}
        self.picker = twintrimmer.twintrimmer.ModificationPicker()

    @staticmethod
    def change_modification_time(filepath, mtime_delta):
        statinfo = os.stat(filepath)
        mtime = statinfo.st_mtime - mtime_delta
        atime = statinfo.st_atime
        os.utime(filepath, (atime, mtime))

    def test_file_1_txt_older_than_file_txt(self):
        print(os.stat(self.file.path))
        print(os.stat(self.file1.path))
        print(os.stat(self.file2.path))
        self.assertEqual(self.picker.pick_older_file(self.file, self.file1),
                         self.file1)

    def test_file_txt_not_older_than_file_1_txt(self):
        self.assertEqual(self.picker.pick_older_file(self.file1, self.file),
                         self.file1)

    def test_sift_finds_shortest_name(self):
        best, rest = self.picker.sift(self.filenames)
        self.assertEqual(best, self.file2)
        self.assertEqual(rest, {self.file, self.file1})


class TestRegexClumper(unittest.TestCase):
    def setUp(self):
        filenames = ['file.txt', 'file (1).txt', 'file (2).txt']
        root = '/'
        bad = ['file']
        self.filenames = list(
            twintrimmer.twintrimmer.PathClumper.create_filenames_from_list(
                filenames, root))
        self.bad = list(
            twintrimmer.twintrimmer.PathClumper.create_filenames_from_list(
                bad, root))[0]

    def test_custom_regex(self):
        clumper = twintrimmer.twintrimmer.RegexClumper(r'(^.+?)(?:\..+)')
        filename_dict = clumper.dump_clumps({(None, ): self.filenames})
        self.assertEqual(len(filename_dict.keys()), 3)

    def test_no_matches_found_raises_error(self):
        clumper = twintrimmer.twintrimmer.RegexClumper(r'(^.+?)(?:\..+)')
        with self.assertRaises(twintrimmer.twintrimmer.ClumperError):
            clumper.make_clump(self.bad)


class TestCaseWithFileSystem(fake_filesystem_unittest.TestCase):
    def setUp(self):
        '''
        Add a fake filesystem matching the following structure:

        examples/
        ├── baz (1).txt		8843d7f
        ├── baz.text		8843d7f
        ├── baz.txt		8843d7f
        ├── diff (1).txt	bbe960a
        ├── diff.txt		0beec7b
        ├── foo (1).txt		f1d2d2f
        ├── foo (2).txt		f1d2d2f
        ├── foo (3).txt		21eb653
        ├── foo.txt		f1d2d2f
        ├── recur
        │   ├── file (2).txt	f4d1f01
        │   └── file.txt	f4d1f01
        └── underscore
            ├── file__1.txt	da39a3e
            └── file.txt	da39a3e

        '''
        self.setUpPyfakefs()
        self.fs.CreateFile('examples/baz.txt', contents='foobar\n')
        self.fs.CreateFile('examples/baz (1).txt', contents='foobar\n')
        self.fs.CreateFile('examples/baz.text', contents='foobar\n')
        self.fs.CreateFile('examples/diff.txt', contents='foo')
        self.fs.CreateFile('examples/diff (1).txt', contents='baz')
        self.fs.CreateFile('examples/foo.txt', contents='foo\n')
        self.fs.CreateFile('examples/foo (1).txt', contents='foo\n')
        self.fs.CreateFile('examples/foo (2).txt', contents='foo\n')
        self.fs.CreateFile('examples/foo (3).txt', contents='foobaz\n')
        self.fs.CreateFile('examples/recur/file.txt', contents='touch\n')
        self.fs.CreateFile('examples/recur/file (2).txt', contents='touch\n')
        self.fs.CreateFile('examples/underscore/file.txt', contents='\n')
        self.fs.CreateFile('examples/underscore/file__1.txt', contents='\n')
        self.file_names_list = [
            twintrimmer.Filename('foo.txt', None, None, 'examples/foo.txt'),
            twintrimmer.Filename('foo (1).txt', None, None,
                                 'examples/foo (1).txt'),
            twintrimmer.Filename('foo (2).txt', None, None,
                                 'examples/foo (2).txt'),
            twintrimmer.Filename('foo (3).txt', None, None,
                                 'examples/foo (3).txt'),
        ]
        self.picker = twintrimmer.twintrimmer.ShortestPicker()


class TestInteractivePicker(unittest.TestCase):
    def setUp(self):
        filenames = ['file.txt', 'file1.txt', 'file2.txt']
        root = '/'
        self.picker = twintrimmer.twintrimmer.InteractivePicker()
        self.file, self.file1, self.file2 = list(
            twintrimmer.twintrimmer.PathClumper.create_filenames_from_list(
                filenames, root))
        self.filenames = {self.file, self.file1, self.file2}

    @patch('builtins.input')
    def test_pick_user_by_index(self, mock_input):
        mock_input.return_value = '0'
        best, rest = self.picker.sift(self.filenames)
        self.assertEqual(self.file, best)
        self.assertEqual(len(rest), 2)
        self.assertEqual(mock_input.call_count, 1)

    @patch('builtins.input')
    def test_pick_user_follows_users_choice(self, mock_input):
        mock_input.return_value = 'file1.txt'
        best, rest = self.picker.sift(self.filenames)
        self.assertEqual(self.file1, best)
        self.assertEqual(len(rest), 2)
        self.assertEqual(mock_input.call_count, 1)

    @patch('builtins.input')
    def test_uses_default_for_no_input(self, mock_input):
        mock_input.return_value = ''
        best, rest = self.picker.sift(self.filenames)
        self.assertEqual(self.file, best)
        self.assertEqual(len(rest), 2)
        self.assertEqual(mock_input.call_count, 1)

    @patch('builtins.input')
    def test_user_supplies_full_filename(self, mock_input):
        mock_input.return_value = 'file1.txt'
        best, rest = self.picker.sift(self.filenames)
        self.assertEqual(self.file1, best)
        self.assertEqual(len(rest), 2)
        self.assertEqual(mock_input.call_count, 1)

    @patch('builtins.input')
    def test_user_typos_filename_on_input(self, mock_input):
        mock_input.side_effect = ['file3.txt', '5', 'file1.txt']
        best, rest = self.picker.sift(self.filenames)
        self.assertEqual(self.file1, best)
        self.assertEqual(len(rest), 2)
        self.assertEqual(mock_input.call_count, 3)

    @patch('builtins.input')
    def test_user_presses_keyboard_interrupt(self, mock_input):
        mock_input.side_effect = KeyboardInterrupt
        best, rest = self.picker.sift(self.filenames)
        self.assertEqual(self.file, best)
        self.assertEqual(len(rest), 0)
        self.assertEqual(mock_input.call_count, 1)


class TestRemoveFilesForDeletion(unittest.TestCase):
    @patch('os.remove')
    def test_no_action_does_no_action(self, mock_remove):
        bad = twintrimmer.Filename(None, None, None, 'examples/foo (1).txt')
        best = twintrimmer.Filename(None, None, None, 'examples/foo.txt')
        twintrimmer.remove_file(bad, best, remove_links=True, no_action=True)
        self.assertEqual(mock_remove.call_count, 0)

    @patch('os.remove')
    def test_skips_removal_of_hardlinks(self, mock_remove):
        bad = twintrimmer.Filename(None, None, None, 'examples/foo (1).txt')
        best = twintrimmer.Filename(None, None, None, 'examples/foo.txt')
        with patch('os.path.samefile') as mock_samefile:
            twintrimmer.remove_file(
                bad,
                best,
                remove_links=False,
                no_action=False)
        self.assertEqual(mock_remove.call_count, 0)
        mock_samefile.assert_called_with('examples/foo.txt',
                                         'examples/foo (1).txt')

    @patch('os.remove')
    def test_removes_duplicate_file(self, mock_remove):
        bad = twintrimmer.Filename(None, None, None, 'examples/foo (1).txt')
        best = twintrimmer.Filename(None, None, None, 'examples/foo.txt')
        twintrimmer.remove_file(bad, best, remove_links=True, no_action=False)
        self.assertEqual(mock_remove.call_count, 1)
        mock_remove.assert_called_with('examples/foo (1).txt')

    @patch('os.link')
    @patch('os.remove')
    def test_makes_hardlink_after_deletion(self, mock_remove, mock_link):
        bad = twintrimmer.Filename(None, None, None, 'examples/foo (2).txt')
        best = twintrimmer.Filename(None, None, None, 'examples/foo.txt')
        twintrimmer.remove_file(
            bad,
            best,
            remove_links=True,
            make_links=True,
            no_action=False)
        self.assertEqual(mock_remove.call_count, 1)
        mock_link.assert_called_with('examples/foo.txt',
                                     'examples/foo (2).txt')


class TestWalkPath(TestCaseWithFileSystem):
    @patch('twintrimmer.twintrimmer.remove_by_clump')
    def test_walk_path_skips_child_directories_and_regex_matching(self,
                                                                  mock_remove):
        twintrimmer.walk_path('examples',
                              hash_function='md5',
                              recursive=False,
                              regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)',
                              skip_regex=True)
        self.assertEqual(mock_remove.call_count, 1)

    @patch('twintrimmer.twintrimmer.remove_by_clump')
    def test_walk_path_includes_child_directories_and_regex_matching(
            self, mock_remove):
        twintrimmer.walk_path('examples',
                              hash_function='md5',
                              recursive=True,
                              regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)',
                              skip_regex=True)
        self.assertEqual(mock_remove.call_count, 1)

    @patch('twintrimmer.twintrimmer.remove_by_clump')
    def test_walk_path_skips_child_directories_but_not_regex_matching(
            self, mock_remove):
        twintrimmer.walk_path('examples',
                              hash_function='md5',
                              recursive=False,
                              skip_regex=False,
                              regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)')
        self.assertEqual(mock_remove.call_count, 1)

    @patch('twintrimmer.twintrimmer.remove_by_clump')
    def test_walk_path_includes_child_directories_but_not_regex_matching(
            self, mock_remove):
        twintrimmer.walk_path('examples',
                              hash_function='md5',
                              recursive=True,
                              skip_regex=False,
                              regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)')
        self.assertEqual(mock_remove.call_count, 1)

    @patch('twintrimmer.twintrimmer.InteractivePicker')
    @patch('twintrimmer.twintrimmer.remove_by_clump')
    def test_walk_path_includes_child_directories_interactive(
            self, mock_interactive, mock_remove):
        twintrimmer.walk_path('examples',
                              hash_function='md5',
                              interactive=True,
                              recursive=True,
                              skip_regex=False,
                              regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)')
        self.assertEqual(mock_remove.call_count, 1)
        self.assertEqual(mock_interactive.call_count, 1)

    @patch('twintrimmer.twintrimmer.ModificationPicker')
    @patch('twintrimmer.twintrimmer.remove_by_clump')
    def test_walk_path_calls_modification_picker(
            self, mock_modification, mock_remove):
        twintrimmer.walk_path('examples',
                              hash_function='md5',
                              keep_oldest=True,
                              recursive=True,
                              skip_regex=False,
                              regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)')
        self.assertEqual(mock_remove.call_count, 1)
        self.assertEqual(mock_modification.call_count, 1)


class TestRemoveByClump(TestCaseWithFileSystem):
    def setUp(self):
        super(TestRemoveByClump, self).setUp()
        self.filename_set_two = {
            twintrimmer.Filename(name='baz (1).txt',
                                 base='baz (1)',
                                 ext='.txt',
                                 path='examples/baz (1).txt'),
            twintrimmer.Filename(name='baz.txt',
                                 base='baz',
                                 ext='.txt',
                                 path='examples/baz.txt')
        }
        self.filename_set_one = {
            twintrimmer.Filename(name='baz (3).txt',
                                 base='baz (3)',
                                 ext='.txt',
                                 path='examples/baz (3).txt'),
        }

    @patch('twintrimmer.twintrimmer.remove_file')
    def test_remove_by_checksum_picks_best_of_two_files(self, mock_remove):
        twintrimmer.twintrimmer.remove_by_clump(
            {'baz': self.filename_set_two}, self.picker)
        self.assertEqual(mock_remove.call_count, 1)

    @patch('twintrimmer.twintrimmer.remove_file')
    def test_remove_by_checksum_catches_OSError(self, mock_remove):
        mock_remove.side_effect = PermissionError
        twintrimmer.twintrimmer.remove_by_clump(
            {'baz': self.filename_set_two}, self.picker)
        self.assertEqual(mock_remove.call_count, 1)

    @patch('twintrimmer.twintrimmer.remove_file')
    def test_remove_by_checksum_skips_single_file(self, mock_remove):
        twintrimmer.twintrimmer.remove_by_clump(
            {'baz3': self.filename_set_one}, self.picker)
        self.assertEqual(mock_remove.call_count, 0)


class TestWalkPathIntegration(TestCaseWithFileSystem):
    def test_no_action_does_no_action(self):
        twintrimmer.walk_path('examples',
                              hash_function='md5',
                              remove_links=True,
                              skip_regex=False,
                              regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)',
                              recursive=False,
                              no_action=True)
        self.assertTrue(os.path.exists('examples/foo (1).txt'))

    def test_no_action_does_nothing_warns_removes_links(self):
        twintrimmer.walk_path('examples',
                              hash_function='md5',
                              no_action=True,
                              skip_regex=False,
                              regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)',
                              recursive=False,
                              remove_links=True)
        self.assertTrue(os.path.exists('examples/foo (1).txt'))

    def test_no_action_does_no_action_skips_hardlinks(self):
        twintrimmer.walk_path('examples',
                              hash_function='md5',
                              no_action=True,
                              skip_regex=False,
                              regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)',
                              recursive=False,
                              remove_links=False)
        self.assertTrue(os.path.exists('examples/foo (1).txt'))

    def test_skip_links_does_no_action_skips_hardlinks(self):
        twintrimmer.walk_path('examples',
                              hash_function='md5',
                              skip_regex=False,
                              regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)',
                              recursive=False,
                              no_action=True,
                              remove_links=False)
        self.assertTrue(os.path.exists('examples/foo (1).txt'))

    def test_makes_links_when_expected(self):
        twintrimmer.walk_path('examples/',
                              hash_function='md5',
                              skip_regex=False,
                              regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)',
                              recursive=False,
                              make_links=True)
        self.assertTrue(os.path.exists('examples/foo (1).txt'))
        self.assertTrue(os.path.samefile('examples/foo.txt',
                                         'examples/foo (1).txt'))

    def test_removes_duplicate_file_foo_1(self):
        self.assertTrue(os.path.exists('examples/foo.txt'))
        self.assertTrue(os.path.exists('examples/foo (1).txt'))
        self.assertTrue(os.path.exists('examples/foo (2).txt'))
        self.assertTrue(os.path.exists('examples/foo (3).txt'))
        twintrimmer.walk_path('examples',
                              hash_function='md5',
                              regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)',
                              skip_regex=False,
                              recursive=False,
                              no_action=False,
                              remove_links=True)
        self.assertTrue(os.path.exists('examples/foo.txt'))
        self.assertFalse(os.path.exists('examples/foo (1).txt'))
        self.assertFalse(os.path.exists('examples/foo (2).txt'))
        self.assertTrue(os.path.exists('examples/foo (3).txt'))

    @unittest.skip
    def test_removes_duplicate_file_foo_1_with_trailing_backslash(self):
        self.assertTrue(os.path.exists('examples/foo.txt'))
        self.assertTrue(os.path.exists('examples/foo (1).txt'))
        self.assertTrue(os.path.exists('examples/foo (2).txt'))
        self.assertTrue(os.path.exists('examples/foo (3).txt'))
        twintrimmer.walk_path('examples/',
                              hash_function='md5',
                              no_action=False,
                              skip_regex=False,
                              recursive=False,
                              regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)',
                              remove_links=True)
        self.assertTrue(os.path.exists('examples/foo.txt'))
        self.assertFalse(os.path.exists('examples/foo (1).txt'))
        self.assertFalse(os.path.exists('examples/foo (2).txt'))
        self.assertTrue(os.path.exists('examples/foo (3).txt'))

    def test_removes_duplicate_file_with_custom_regex_double_underscore(self):
        self.assertTrue(os.path.exists('examples/underscore/file.txt'))
        self.assertTrue(os.path.exists('examples/underscore/file__1.txt'))
        twintrimmer.walk_path('examples/underscore',
                              hash_function='md5',
                              regex_pattern=r'(.+?)(?:__\d)*\..*',
                              recursive=False,
                              skip_regex=False,
                              no_action=False,
                              remove_links=True)
        self.assertTrue(os.path.exists('examples/underscore/file.txt'))
        self.assertFalse(os.path.exists('examples/underscore/file__1.txt'))

    def test_removes_duplicate_file_with_custom_regex_trailing_tilde(self):
        self.fs.CreateFile('examples/foo.txt~', contents='foo\n')
        self.assertTrue(os.path.exists('examples/foo.txt'))
        twintrimmer.walk_path('examples',
                              hash_function='md5',
                              no_action=False,
                              regex_pattern=r'(^.+?)(?: \(\d\))*\..+',
                              skip_regex=False,
                              recursive=False,
                              remove_links=True)
        self.assertTrue(os.path.exists('examples/foo.txt'))
        self.assertFalse(os.path.exists('examples/foo.txt~'))

    def test_removes_files_skipping_name_match(self):
        self.fs.CreateFile('examples/fizz', contents='foo\n')
        self.assertTrue(os.path.exists('examples/foo.txt'))
        twintrimmer.walk_path('examples',
                              hash_function='md5',
                              no_action=False,
                              recursive=False,
                              regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)',
                              skip_regex=True,
                              remove_links=True)
        self.assertTrue(os.path.exists('examples/fizz'))
        self.assertFalse(os.path.exists('examples/foo.txt'))

    def test_traverses_directories_recursively(self):
        self.assertTrue(os.path.exists('examples/recur/file (2).txt'))
        twintrimmer.walk_path('examples',
                              hash_function='md5',
                              no_action=False,
                              skip_regex=False,
                              recursive=True,
                              regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)',
                              remove_links=True)
        self.assertTrue(os.path.exists('examples/foo.txt'))
        self.assertFalse(os.path.exists('examples/foo (1).txt'))
        self.assertFalse(os.path.exists('examples/recur/file (2).txt'))

    def test_can_not_sum_hash_due_to_OSError(self):
        os.chmod('examples/recur/file.txt', 0o000)
        twintrimmer.walk_path('examples/recur',
                              hash_function='md5',
                              no_action=False,
                              skip_regex=False,
                              recursive=False,
                              regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)',
                              remove_links=True)
        self.assertTrue(os.path.exists('examples/recur/file (2).txt'))

    @unittest.skip
    def test_can_not_delete_file_due_to_OSError(self):
        os.chmod('examples/recur/file (2).txt', 0o700)
        os.chown('examples/recur/file (2).txt', 0, 0)
        print(os.stat('examples/recur/file (2).txt'))

        #with self.assertRaises(OSError):
        twintrimmer.walk_path('examples/recur',
                              hash_function='md5',
                              no_action=False,
                              recursive=False,
                              skip_regex=False,
                              remove_links=True)
        self.assertTrue(os.path.exists('examples/recur/file (2).txt'))


class TestMain(TestCaseWithFileSystem):
    def setUp(self):
        super(TestMain, self).setUp()
        self.new_out, self.new_err = StringIO(), StringIO()
        self.old_out, self.old_err = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = self.new_out, self.new_err

    def tearDown(self):
        super(TestMain, self).tearDown()
        sys.stdout, sys.stderr = self.old_out, self.old_err

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_default_args_pass_correctly(self, mock_walk_path):
        twintrimmer.twintrimmer.main(['.'])
        mock_walk_path.assert_called_with(
            log_file=None,
            log_level=3,
            interactive=False,
            hash_function='md5',
            remove_links=False,
            verbosity=1,
            recursive=False,
            path='.',
            make_links=False,
            regex_pattern='(^.+?)(?: \\(\\d\\))*(\\..+)$',
            skip_regex=False,
            keep_oldest=False,
            no_action=False)
        self.assertEqual(self.new_out.getvalue(), '')
        self.assertEqual(self.new_err.getvalue(), '')

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_no_action_argument_passes_correctly(self, mock_walk_path):
        twintrimmer.twintrimmer.main(['--no-action', '.'])
        mock_walk_path.assert_called_with(
            log_file=None,
            log_level=3,
            interactive=False,
            hash_function='md5',
            remove_links=False,
            verbosity=1,
            recursive=False,
            path='.',
            make_links=False,
            regex_pattern='(^.+?)(?: \\(\\d\\))*(\\..+)$',
            skip_regex=False,
            keep_oldest=False,
            no_action=True)
        self.assertEqual(self.new_out.getvalue(), '')
        self.assertEqual(self.new_err.getvalue(), '')

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_no_action_single_argument_passes_correctly(self, mock_walk_path):
        twintrimmer.twintrimmer.main(['--n', '.'])
        mock_walk_path.assert_called_with(
            log_file=None,
            log_level=3,
            interactive=False,
            hash_function='md5',
            remove_links=False,
            verbosity=1,
            recursive=False,
            path='.',
            make_links=False,
            regex_pattern='(^.+?)(?: \\(\\d\\))*(\\..+)$',
            skip_regex=False,
            keep_oldest=False,
            no_action=True)
        self.assertEqual(self.new_out.getvalue(), '')
        self.assertEqual(self.new_err.getvalue(), '')

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_log_file_argument_passes_correctly(self, mock_walk_path):
        twintrimmer.twintrimmer.main(['.', '--log-file', 'file.log',
                                      '--log-level', '5'])
        mock_walk_path.assert_called_with(
            log_file='file.log',
            log_level=5,
            interactive=False,
            hash_function='md5',
            remove_links=False,
            verbosity=1,
            recursive=False,
            path='.',
            make_links=False,
            regex_pattern='(^.+?)(?: \\(\\d\\))*(\\..+)$',
            skip_regex=False,
            keep_oldest=False,
            no_action=False)
        self.assertEqual(self.new_out.getvalue(), '')
        self.assertEqual(self.new_err.getvalue(), '')

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_hash_fuction_argument_passes_correctly(self, mock_walk_path):
        twintrimmer.twintrimmer.main(['.', '--hash-function', 'sha1'])
        mock_walk_path.assert_called_with(
            log_file=None,
            log_level=3,
            interactive=False,
            hash_function='sha1',
            remove_links=False,
            verbosity=1,
            recursive=False,
            path='.',
            make_links=False,
            regex_pattern='(^.+?)(?: \\(\\d\\))*(\\..+)$',
            skip_regex=False,
            keep_oldest=False,
            no_action=False)
        self.assertEqual(self.new_out.getvalue(), '')
        self.assertEqual(self.new_err.getvalue(), '')

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_short_recursive_argument_passes_correctly(self, mock_walk_path):
        twintrimmer.twintrimmer.main(['.', '-r'])
        mock_walk_path.assert_called_with(
            log_file=None,
            log_level=3,
            interactive=False,
            hash_function='md5',
            remove_links=False,
            verbosity=1,
            recursive=True,
            path='.',
            make_links=False,
            regex_pattern='(^.+?)(?: \\(\\d\\))*(\\..+)$',
            skip_regex=False,
            keep_oldest=False,
            no_action=False)
        self.assertEqual(self.new_out.getvalue(), '')
        self.assertEqual(self.new_err.getvalue(), '')

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_long_recursive_argument_passes_correctly(self, mock_walk_path):
        twintrimmer.twintrimmer.main(['.', '--recursive'])
        mock_walk_path.assert_called_with(
            log_file=None,
            log_level=3,
            interactive=False,
            hash_function='md5',
            remove_links=False,
            verbosity=1,
            recursive=True,
            path='.',
            make_links=False,
            regex_pattern='(^.+?)(?: \\(\\d\\))*(\\..+)$',
            skip_regex=False,
            keep_oldest=False,
            no_action=False)
        self.assertEqual(self.new_out.getvalue(), '')
        self.assertEqual(self.new_err.getvalue(), '')

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_make_links_argument_passes_correctly(self, mock_walk_path):
        twintrimmer.twintrimmer.main(['.', '--make-links'])
        mock_walk_path.assert_called_with(
            log_file=None,
            log_level=3,
            interactive=False,
            hash_function='md5',
            remove_links=False,
            verbosity=1,
            recursive=False,
            path='.',
            make_links=True,
            regex_pattern='(^.+?)(?: \\(\\d\\))*(\\..+)$',
            skip_regex=False,
            keep_oldest=False,
            no_action=False)
        self.assertEqual(self.new_out.getvalue(), '')
        self.assertEqual(self.new_err.getvalue(), '')

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_remove_link_arg_pass_correctly(self, mock_walk_path):
        twintrimmer.twintrimmer.main(['.', '--remove-links'])
        mock_walk_path.assert_called_with(
            log_file=None,
            log_level=3,
            interactive=False,
            hash_function='md5',
            remove_links=True,
            verbosity=1,
            recursive=False,
            path='.',
            make_links=False,
            regex_pattern='(^.+?)(?: \\(\\d\\))*(\\..+)$',
            skip_regex=False,
            keep_oldest=False,
            no_action=False)
        self.assertEqual(self.new_out.getvalue(), '')
        self.assertEqual(self.new_err.getvalue(), '')

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_interactive_mode_passed_correctly(self, mock_walk_path):
        twintrimmer.twintrimmer.main(['.', '--interactive'])
        mock_walk_path.assert_called_with(
            log_file=None,
            log_level=3,
            interactive=True,
            hash_function='md5',
            remove_links=False,
            verbosity=1,
            recursive=False,
            path='.',
            make_links=False,
            regex_pattern='(^.+?)(?: \\(\\d\\))*(\\..+)$',
            skip_regex=False,
            keep_oldest=False,
            no_action=False)
        self.assertEqual(self.new_out.getvalue(), '')
        self.assertEqual(self.new_err.getvalue(), '')

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_short_arg_interactive_passed_correctly(self, mock_walk_path):
        twintrimmer.twintrimmer.main(['.', '-i'])
        mock_walk_path.assert_called_with(
            log_file=None,
            log_level=3,
            interactive=True,
            hash_function='md5',
            remove_links=False,
            verbosity=1,
            recursive=False,
            path='.',
            make_links=False,
            regex_pattern='(^.+?)(?: \\(\\d\\))*(\\..+)$',
            skip_regex=False,
            keep_oldest=False,
            no_action=False)
        self.assertEqual(self.new_out.getvalue(), '')
        self.assertEqual(self.new_err.getvalue(), '')

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_keep_oldest_mode_passed_correctly(self, mock_walk_path):
        twintrimmer.twintrimmer.main(['.', '--keep-oldest'])
        mock_walk_path.assert_called_with(
            log_file=None,
            log_level=3,
            interactive=False,
            hash_function='md5',
            remove_links=False,
            verbosity=1,
            recursive=False,
            path='.',
            make_links=False,
            regex_pattern='(^.+?)(?: \\(\\d\\))*(\\..+)$',
            skip_regex=False,
            keep_oldest=True,
            no_action=False)
        self.assertEqual(self.new_out.getvalue(), '')
        self.assertEqual(self.new_err.getvalue(), '')

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_short_checksum_only_mode_passed_correctly(self, mock_walk_path):
        twintrimmer.twintrimmer.main(['.', '-c'])
        mock_walk_path.assert_called_with(
            log_file=None,
            log_level=3,
            interactive=False,
            hash_function='md5',
            remove_links=False,
            verbosity=1,
            recursive=False,
            path='.',
            make_links=False,
            regex_pattern='(^.+?)(?: \\(\\d\\))*(\\..+)$',
            skip_regex=True,
            keep_oldest=False,
            no_action=False)
        self.assertEqual(self.new_out.getvalue(), '')
        self.assertEqual(self.new_err.getvalue(), '')

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_long_checksum_only_mode_passed_correctly(self, mock_walk_path):
        twintrimmer.twintrimmer.main(['.', '--only-checksum'])
        mock_walk_path.assert_called_with(
            log_file=None,
            log_level=3,
            interactive=False,
            hash_function='md5',
            remove_links=False,
            verbosity=1,
            recursive=False,
            path='.',
            make_links=False,
            regex_pattern='(^.+?)(?: \\(\\d\\))*(\\..+)$',
            skip_regex=True,
            keep_oldest=False,
            no_action=False)
        self.assertEqual(self.new_out.getvalue(), '')
        self.assertEqual(self.new_err.getvalue(), '')

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_custom_regex_passed_correctly(self, mock_walk_path):
        twintrimmer.twintrimmer.main(['.', '--pattern', r'(^.+?)(?:\..+)$'])
        mock_walk_path.assert_called_with(
            log_file=None,
            log_level=3,
            interactive=False,
            hash_function='md5',
            remove_links=False,
            verbosity=1,
            recursive=False,
            path='.',
            make_links=False,
            regex_pattern=r'(^.+?)(?:\..+)$',
            skip_regex=False,
            keep_oldest=False,
            no_action=False)
        self.assertEqual(self.new_out.getvalue(), '')
        self.assertEqual(self.new_err.getvalue(), '')

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_no_args_fails(self, mock_walk_path):
        with self.assertRaises(SystemExit):
            twintrimmer.twintrimmer.main([])
        self.assertEqual(mock_walk_path.call_count, 0)
        self.assertEqual(self.new_out.getvalue(), '')
        self.assertIn('error: the following arguments are required: path',
                      self.new_err.getvalue())

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_pattern_with_skip_regex_fails(self, mock_walk_path):
        with self.assertRaises(SystemExit):
            twintrimmer.twintrimmer.main(['.', '-c', '-p', '(.*)'])
        self.assertEqual(mock_walk_path.call_count, 0)
        self.assertEqual(self.new_out.getvalue(), '')
        self.assertIn('Pattern set while skipping regex checking',
                      self.new_err.getvalue())

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_invalid_arg_fails(self, mock_walk_path):
        with self.assertRaises(SystemExit):
            twintrimmer.twintrimmer.main(['.', '--invalid'])
        self.assertEqual(mock_walk_path.call_count, 0)
        self.assertEqual(self.new_out.getvalue(), '')
        self.assertIn('unrecognized arguments: --invalid',
                      self.new_err.getvalue())

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_log_level_without_file_fails(self, mock_walk_path):
        with self.assertRaises(SystemExit):
            twintrimmer.twintrimmer.main(['.', '--log-level', '4'])
        self.assertEqual(mock_walk_path.call_count, 0)
        self.assertEqual(self.new_out.getvalue(), '')
        self.assertIn('Log level set without log file',
                      self.new_err.getvalue())

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_bad_path_fails(self, mock_walk_path):
        with self.assertRaises(SystemExit):
            twintrimmer.twintrimmer.main(['/does/not/exist/'])
        self.assertEqual(mock_walk_path.call_count, 0)
        self.assertEqual(self.new_out.getvalue(), '/does/not/exist/\n')
        self.assertIn('path was not a directory', self.new_err.getvalue())

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_invalid_regex_fails(self, mock_walk_path):
        with self.assertRaises(SystemExit):
            twintrimmer.twintrimmer.main(['.', '-p', '(((r)'])
        self.assertEqual(mock_walk_path.call_count, 0)
        self.assertEqual(self.new_out.getvalue(), '')
        self.assertIn('Invalid regular expression: "(((r)"',
                      self.new_err.getvalue())

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_unwritable_log_file_fails(self, mock_walk_path):
        os.chmod('examples/baz.txt', 0o000)
        with self.assertRaises(SystemExit):
            twintrimmer.twintrimmer.main(['.', '--log-file', 'examples/baz.txt'
                                         ])
        self.assertEqual(mock_walk_path.call_count, 0)
        self.assertEqual(self.new_out.getvalue(), '')
        self.assertEqual(self.new_err.getvalue(), '')

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_help_arg_show_helpful_message(self, mock_walk_path):
        with self.assertRaises(SystemExit):
            twintrimmer.twintrimmer.main(['--help'])
        self.assertEqual(mock_walk_path.call_count, 0)
        self.assertIn('usage', self.new_out.getvalue())
        self.assertEqual(self.new_err.getvalue(), '')

    @patch('twintrimmer.twintrimmer.walk_path')
    def test_version_arg_show_version_message(self, mock_walk_path):
        with self.assertRaises(SystemExit):
            twintrimmer.twintrimmer.main(['--version'])
        self.assertEqual(mock_walk_path.call_count, 0)
        self.assertIn(twintrimmer.__version__, self.new_out.getvalue())
        self.assertEqual(self.new_err.getvalue(), '')


if __name__ == '__main__':
    unittest.main()
