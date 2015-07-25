import unittest
import twintrimmer
from unittest.mock import patch, mock_open
import builtins

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

class TestGenerateChecksum(unittest.TestCase):
  def setUp(self):
      pass

  @unittest.skip('Skip: bug in python issue23004')
  def test_generate_checksum(self):
      m = mock_open(read_data='bibble'.encode('utf-8'))
      with patch('builtins.open', m, create=True):
          checksum = twintrimmer.generate_checksum('foo')

      m.assert_called_once_with('foo')
      self.assertEqual(checksum, 'cb1eda4e6df6ff361f9ed94f91ce5386')


if __name__ == '__main__':
    unittest.main()
