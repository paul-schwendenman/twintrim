import unittest

class TestSomeThings(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_this_things(self):
        assert True
        
    def tearDown(self):
        pass
    

if __name__ == '__main__':
    unittest.main()