import unittest
import twintrimmer

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

    def test_no_files(self):
        filenames = []
        root = '/'
        list_output = list(twintrimmer.create_filenames(filenames, root))
        self.assertEqual(len(list_output), 0)



if __name__ == '__main__':
    unittest.main()
