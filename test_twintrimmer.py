import unittest
import twintrimmer
from unittest.mock import patch, mock_open
import builtins
import fake_filesystem_unittest

class TestSomeThings(unittest.TestCase):
    def setUp(self):
        pass

    def test_this_things(self):
        assert True

    def tearDown(self):
        pass

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

if __name__ == '__main__':
    unittest.main()
