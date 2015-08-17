def is_substring(string1, string2):
    '''
    Returns a match if one string is a substring of the other

    :param str string1: the first string to compare
    :param str string2: the second string to compare
    :returns: True if either string is substring of the other
    :rtype: bool

    For example:

    >>> is_substring('this', 'this1')
    True
    >>> is_substring('that1', 'that')
    True
    >>> is_substring('that', 'this')
    False
    '''
    return string1 in string2 or string2 in string1

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
