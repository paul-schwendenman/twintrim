'''
Tests for the twintrimmer module
'''
#pylint: disable=missing-docstring, invalid-name
import unittest
import twintrimmer
from unittest.mock import patch
import fake_filesystem_unittest
import os


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
            twintrimmer.twintrimmer.PathClumper.create_filenames(filenames,
                                                                 root))
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
            twintrimmer.twintrimmer.PathClumper.create_filenames(filenames,
                                                                 root))
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
            twintrimmer.twintrimmer.PathClumper.create_filenames(filenames,
                                                                 root))
        self.filenames = {self.file, self.file1, self.file2}
        self.picker = twintrimmer.twintrimmer.ShortestPicker()

    def test_filter_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.picker.filter({('this'): {'one', 'two'}})

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


class TestRegexClumper(unittest.TestCase):
    def setUp(self):
        filenames = ['file.txt', 'file (1).txt', 'file (2).txt']
        root = '/'
        bad = ['file']
        self.filenames = list(
            twintrimmer.twintrimmer.PathClumper.create_filenames(filenames,
                                                                 root))
        self.bad = list(twintrimmer.twintrimmer.PathClumper.create_filenames(
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
            twintrimmer.twintrimmer.PathClumper.create_filenames(filenames,
                                                                 root))
        self.filenames = {self.file, self.file1, self.file2}

    def test_filter_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.picker.filter({('this'): {'one', 'two'}})

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
                bad, best,
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
            bad, best,
            remove_links=True,
            make_links=True,
            no_action=False)
        self.assertEqual(mock_remove.call_count, 1)
        mock_link.assert_called_with('examples/foo.txt',
                                     'examples/foo (2).txt')


class TestMain(TestCaseWithFileSystem):
    @patch('twintrimmer.twintrimmer.remove_by_clump')
    def test_walk_path_skips_child_directories_and_regex_matching(self, mock_remove):
        twintrimmer.main('examples',
                         hash_function='md5',
                         recursive=False,
                         regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)',
                         skip_regex=True)
        self.assertEqual(mock_remove.call_count, 1)

    @patch('twintrimmer.twintrimmer.remove_by_clump')
    def test_walk_path_includes_child_directories_and_regex_matching(self, mock_remove):
        twintrimmer.main('examples',
                         hash_function='md5',
                         recursive=True,
                         regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)',
                         skip_regex=True)
        self.assertEqual(mock_remove.call_count, 1)

    @patch('twintrimmer.twintrimmer.remove_by_clump')
    def test_walk_path_skips_child_directories_but_not_regex_matching(self, mock_remove):
        twintrimmer.main('examples',
                         hash_function='md5',
                         recursive=False,
                         skip_regex=False,
                         regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)')
        self.assertEqual(mock_remove.call_count, 1)

    @patch('twintrimmer.twintrimmer.remove_by_clump')
    def test_walk_path_includes_child_directories_but_not_regex_matching(self, mock_remove):
        twintrimmer.main('examples',
                         hash_function='md5',
                         recursive=True,
                         skip_regex=False,
                         regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)')
        self.assertEqual(mock_remove.call_count, 1)

    @patch('twintrimmer.twintrimmer.InteractivePicker')
    @patch('twintrimmer.twintrimmer.remove_by_clump')
    def test_walk_path_includes_child_directories_interactive(self, mock_interactive, mock_remove):
        twintrimmer.main('examples',
                         hash_function='md5',
                         interactive=True,
                         recursive=True,
                         skip_regex=False,
                         regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)')
        self.assertEqual(mock_remove.call_count, 1)
        self.assertEqual(mock_interactive.call_count, 1)


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


class TestMainIntegration(TestCaseWithFileSystem):
    def test_no_action_does_no_action(self):
        twintrimmer.main('examples',
                         hash_function='md5',
                         remove_links=True,
                         skip_regex=False,
                         regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)',
                         recursive=False,
                         no_action=True)
        self.assertTrue(os.path.exists('examples/foo (1).txt'))

    def test_no_action_does_nothing_warns_removes_links(self):
        twintrimmer.main('examples',
                         hash_function='md5',
                         no_action=True,
                         skip_regex=False,
                         regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)',
                         recursive=False,
                         remove_links=True)
        self.assertTrue(os.path.exists('examples/foo (1).txt'))

    def test_no_action_does_no_action_skips_hardlinks(self):
        twintrimmer.main('examples',
                         hash_function='md5',
                         no_action=True,
                         skip_regex=False,
                         regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)',
                         recursive=False,
                         remove_links=False)
        self.assertTrue(os.path.exists('examples/foo (1).txt'))

    def test_skip_links_does_no_action_skips_hardlinks(self):
        twintrimmer.main('examples',
                         hash_function='md5',
                         skip_regex=False,
                         regex_pattern=r'(^.+?)(?: \(\d\))*(\..+)',
                         recursive=False,
                         remove_links=False)
        self.assertTrue(os.path.exists('examples/foo (1).txt'))

    def test_makes_links_when_expected(self):
        twintrimmer.main('examples/',
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
        twintrimmer.main('examples',
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
        twintrimmer.main('examples/',
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
        twintrimmer.main('examples/underscore',
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
        twintrimmer.main('examples',
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
        twintrimmer.main('examples',
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
        twintrimmer.main('examples',
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
        twintrimmer.main('examples/recur',
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
        twintrimmer.main('examples/recur',
                         hash_function='md5',
                         no_action=False,
                         recursive=False,
                         skip_regex=False,
                         remove_links=True)
        self.assertTrue(os.path.exists('examples/recur/file (2).txt'))


if __name__ == '__main__':
    unittest.main()
