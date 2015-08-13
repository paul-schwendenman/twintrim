import unittest
import twintrimmer
from unittest.mock import patch, mock_open
import builtins
import fake_filesystem_unittest
import os

class TestCreateFilenames(unittest.TestCase):
    def test_one_file(self):
        filenames = ['test_file.txt']
        root = '/'
        list_output = list(twintrimmer.create_filenames(filenames, root))
        self.assertEqual(len(list_output), 1)
        self.assertIs(type(list_output[0]), twintrimmer.Filename)
        self.assertEqual(list_output[0].name, 'test_file.txt')
        self.assertEqual(list_output[0].base, 'test_file')
        self.assertEqual(list_output[0].ext, '.txt')
        self.assertEqual(list_output[0].path, '/test_file.txt')

    def test_no_files(self):
        filenames = []
        root = '/'
        list_output = list(twintrimmer.create_filenames(filenames, root))
        self.assertEqual(len(list_output), 0)

class TestGenerateChecksum(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.fs.CreateFile('/test/lots/of/nonexistent/directories/full.txt',
                           contents='First line\nSecond Line\n')

    def test_generate_sha1_checksum_for_file(self):
        checksum = twintrimmer.generate_checksum('/test/lots/of/nonexistent/directories/full.txt', 'sha1')
        self.assertEqual(checksum, '5a0cd97a76759aafa9fd5e4c5aa2ffe0e6f1720d')

    def test_generate_md5_checksum_for_file(self):
        checksum = twintrimmer.generate_checksum('/test/lots/of/nonexistent/directories/full.txt')
        self.assertEqual(checksum, 'af55da6adb51f8dc6b4d3758b5bcf8cc')

    def test_generate_sha256_checksum_for_file(self):
        checksum = twintrimmer.generate_checksum('/test/lots/of/nonexistent/directories/full.txt', 'sha256')
        self.assertEqual(checksum, '2300530cd0164f39302afed1b8dfa54781ad804f1caac7a76ed8c5dd129e7087')

    def test_generate_sha512_checksum_for_file(self):
        checksum = twintrimmer.generate_checksum('/test/lots/of/nonexistent/directories/full.txt', 'sha512')
        self.assertEqual(checksum, '2671d9257c1b6c84e8b23bdca07d38cf4ced034b62de1834283bc7bf33968f9361fa01b652c6e363dcdf0361746c40da245a5d9a1d1a78f8de04d93d4d179c59')

    def test_generate_sha224_checksum_for_file(self):
        checksum = twintrimmer.generate_checksum('/test/lots/of/nonexistent/directories/full.txt', 'sha224')
        self.assertEqual(checksum, 'd0b3c8046b81a798aa7f7302cf7482ee36f1e14b7139ec0bb7122b99')

    def test_generate_sha384_checksum_for_file(self):
        checksum = twintrimmer.generate_checksum('/test/lots/of/nonexistent/directories/full.txt', 'sha384')
        self.assertEqual(checksum, '49dd8afce21b0e0bd363796f754434e4075a22daf110c908380cbfbf0aceb62c08c04e7bbcac84d80628d71e99174ce1')

    def test_generate_whirlpool_checksum_for_file(self):
        checksum = twintrimmer.generate_checksum('/test/lots/of/nonexistent/directories/full.txt', 'whirlpool')
        self.assertEqual(checksum, 'b9d619b1860cd603a47a4a367558e0f9e5a4cfde96403c944ddcf9c4e01f9f20207869b34d48d672018efdf394cbac6410e45df044a16fa621dfcec43a67b4bc')

    def test_generate_checksum_raises_OSError_for_missing_file(self):
        with self.assertRaises(OSError):
            checksum = twintrimmer.generate_checksum('/nonexistentfile.txt')


class TestIsSubstring(unittest.TestCase):
    def test_this_is_substring_of_this1(self):
        self.assertTrue(twintrimmer.is_substring('this', 'this1'))

    def test_that1_is_substring_of_that(self):
        self.assertTrue(twintrimmer.is_substring('that1', 'that'))

    def test_this_is_not_substring_of_that(self):
        self.assertFalse(twintrimmer.is_substring('this', 'that'))

class TestPickShorterName(unittest.TestCase):
    def setUp(self):
        filenames = ['file.txt', 'file1.txt', 'file2.txt']
        root = '/'
        self.file, self.file1, self.file2 = list(twintrimmer.create_filenames(filenames, root))

    def test_file_txt_shorter_than_file_1_txt(self):
        self.assertEqual(twintrimmer.pick_shorter_name(self.file, self.file1), self.file)

    def test_file_1_txt_shorter_than_file_2_txt(self):
        self.assertEqual(twintrimmer.pick_shorter_name(self.file1, self.file2), self.file1)

    def test_file_1_txt_not_shorter_than_file_txt(self):
        self.assertEqual(twintrimmer.pick_shorter_name(self.file1, self.file), self.file)

class TestGenerateFilenameDict(unittest.TestCase):
    def setUp(self):
        filenames = ['file.txt', 'file (1).txt', 'file (2).txt']
        root = '/'
        self.filenames = list(twintrimmer.create_filenames(filenames, root))

    def test_dictionary_has_one_key(self):
        filename_dict = twintrimmer.generate_filename_dict(self.filenames)
        self.assertEqual(len(filename_dict.keys()), 1)
        self.assertEqual(list(filename_dict.keys())[0], ('file', '.txt'))

    def test_custom_regex(self):
        filename_dict = twintrimmer.generate_filename_dict(self.filenames, r'(^.+?)(?:\..+)')
        self.assertEqual(len(filename_dict.keys()), 3)

class TestWalkPath(fake_filesystem_unittest.TestCase):
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
        self.fs.CreateFile('examples/baz.txt',
                           contents='foobar\n')
        self.fs.CreateFile('examples/baz (1).txt',
                           contents='foobar\n')
        self.fs.CreateFile('examples/baz.text',
                           contents='foobar\n')
        self.fs.CreateFile('examples/diff.txt',
                           contents='foo')
        self.fs.CreateFile('examples/diff (1).txt',
                           contents='baz')
        self.fs.CreateFile('examples/foo.txt',
                           contents='foo\n')
        self.fs.CreateFile('examples/foo (1).txt',
                           contents='foo\n')
        self.fs.CreateFile('examples/foo (2).txt',
                           contents='foo\n')
        self.fs.CreateFile('examples/foo (3).txt',
                           contents='foobaz\n')
        self.fs.CreateFile('examples/recur/file.txt',
                           contents='touch\n')
        self.fs.CreateFile('examples/recur/file (2).txt',
                           contents='touch\n')
        self.fs.CreateFile('examples/underscore/file.txt',
                           contents='\n')
        self.fs.CreateFile('examples/underscore/file__1.txt',
                           contents='\n')

    def test_no_action_does_no_action(self):
        twintrimmer.walk_path('examples',
                              no_action=True)
        self.assertTrue(os.path.exists('examples/foo (1).txt'))

    def test_no_action_does_nothing_warns_removes_links(self):
        twintrimmer.walk_path('examples',
                              no_action=True,
                              remove_links=True)
        self.assertTrue(os.path.exists('examples/foo (1).txt'))

    def test_no_action_does_no_action_skips_hardlinks(self):
        twintrimmer.walk_path('examples',
                              no_action=True,
                              remove_links=False)
        self.assertTrue(os.path.exists('examples/foo (1).txt'))

    def test_skip_links_does_no_action_skips_hardlinks(self):
        twintrimmer.walk_path('examples',
                              remove_links=False)
        self.assertTrue(os.path.exists('examples/foo (1).txt'))

    def test_makes_links_when_expected(self):
        twintrimmer.walk_path('examples/',
                              make_links=True)
        self.assertTrue(os.path.exists('examples/foo (1).txt'))
        self.assertTrue(os.path.samefile('examples/foo.txt', 'examples/foo (1).txt'))

    def test_removes_duplicate_file_foo_1(self):
        self.assertTrue(os.path.exists('examples/foo.txt'))
        self.assertTrue(os.path.exists('examples/foo (1).txt'))
        self.assertTrue(os.path.exists('examples/foo (2).txt'))
        self.assertTrue(os.path.exists('examples/foo (3).txt'))
        twintrimmer.walk_path('examples',
                              no_action=False,
                              remove_links=True)
        self.assertTrue(os.path.exists('examples/foo.txt'))
        self.assertFalse(os.path.exists('examples/foo (1).txt'))
        self.assertFalse(os.path.exists('examples/foo (2).txt'))
        self.assertTrue(os.path.exists('examples/foo (3).txt'))

    @unittest.expectedFailure
    def test_removes_duplicate_file_foo_1_with_trailing_backslash(self):
        self.assertTrue(os.path.exists('examples/foo.txt'))
        self.assertTrue(os.path.exists('examples/foo (1).txt'))
        self.assertTrue(os.path.exists('examples/foo (2).txt'))
        self.assertTrue(os.path.exists('examples/foo (3).txt'))
        twintrimmer.walk_path('examples/',
                              no_action=False,
                              remove_links=True)
        self.assertTrue(os.path.exists('examples/foo.txt'))
        self.assertFalse(os.path.exists('examples/foo (1).txt'))
        self.assertFalse(os.path.exists('examples/foo (2).txt'))
        self.assertTrue(os.path.exists('examples/foo (3).txt'))

    def test_removes_duplicate_file_with_custom_regex_double_underscore(self):
        self.assertTrue(os.path.exists('examples/underscore/file.txt'))
        self.assertTrue(os.path.exists('examples/underscore/file__1.txt'))
        twintrimmer.walk_path('examples/underscore',
                              regex_pattern='(.+?)(?:__\d)*\..*',
                              no_action=False,
                              remove_links=True)
        self.assertTrue(os.path.exists('examples/underscore/file.txt'))
        self.assertFalse(os.path.exists('examples/underscore/file__1.txt'))

    def test_removes_duplicate_file_with_custom_regex_trailing_tilde(self):
        self.fs.CreateFile('examples/foo.txt~',
                           contents='foo\n')
        self.assertTrue(os.path.exists('examples/foo.txt'))
        twintrimmer.walk_path('examples',
                              regex_pattern='(^.+?)(?: \(\d\))*\..+',
                              no_action=False,
                              remove_links=True)
        self.assertTrue(os.path.exists('examples/foo.txt'))
        self.assertFalse(os.path.exists('examples/foo.txt~'))

    def test_removes_files_skipping_name_match(self):
        self.fs.CreateFile('examples/fizz',
                           contents='foo\n')
        self.assertTrue(os.path.exists('examples/foo.txt'))
        twintrimmer.walk_path('examples',
                              skip_regex=True,
                              no_action=False,
                              remove_links=True)
        self.assertTrue(os.path.exists('examples/fizz'))
        self.assertFalse(os.path.exists('examples/foo.txt'))

    def test_traverses_directories_recursively(self):
        self.assertTrue(os.path.exists('examples/recur/file (2).txt'))
        twintrimmer.walk_path('examples',
                              no_action=False,
                              recursive=True,
                              remove_links=True)
        self.assertTrue(os.path.exists('examples/foo.txt'))
        self.assertFalse(os.path.exists('examples/foo (1).txt'))
        self.assertFalse(os.path.exists('examples/recur/file (2).txt'))

    def test_can_not_sum_hash_due_to_OSError(self):
        os.chmod('examples/recur/file.txt', 0o000)
        #with self.assertRaises(OSError):
        twintrimmer.walk_path('examples/recur',
                              no_action=False,
                              remove_links=True)
        self.assertTrue(os.path.exists('examples/recur/file (2).txt'))

    @unittest.expectedFailure
    def test_can_not_delete_file_due_to_OSError(self):
        os.chmod('examples/recur/file (2).txt', 0o700)
        os.chown('examples/recur/file (2).txt', 0, 0)
        print(os.stat('examples/recur/file (2).txt'))

        #with self.assertRaises(OSError):
        twintrimmer.walk_path('examples/recur',
                              no_action=False,
                              remove_links=True)
        self.assertTrue(os.path.exists('examples/recur/file (2).txt'))

if __name__ == '__main__':
    unittest.main()