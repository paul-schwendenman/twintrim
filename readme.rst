--------------
Twintrimmer
--------------

Introduction
-------------

Twintrimmer is a project designed to automatically remove duplicate files
specially those created by downloading in a browser.


Modivation
-----------

Relatively often I find that I download a file multiple times using Chrome
or Firefox and they rather than over writing the file "``<filename>.<ext>``"
will name the newest copy "``<filename> (#).<ext>``" I built this tool to
automatically remove duplicate versions by comparing the names and then
validating the content with a checksum.


Usage
-------

usage: twintrim [-h] [-n] [-r] [--verbosity VERBOSITY]
                      [--log-file LOG_FILE] [--log-level LOG_LEVEL]
                      [-p PATTERN] [-c] [-i]
                      [--hash-function {'sha224', 'sha384', 'sha1', 'md5', 'sha512', 'sha256'}
                      [--make-links] [--remove-links]
                      path

tool for removing duplicate files

positional arguments:
  path                  path to check

optional arguments:
  -h, --help            show this help message and exit
  -n, --no-action       show what files would have been deleted
  -r, --recursive       search directories recursively
  --verbosity VERBOSITY
                        set print debug level
  --log-file LOG_FILE   write to log file.
  --log-level LOG_LEVEL
                        set log file debug level
  -p PATTERN, --pattern PATTERN
                        set filename matching regex
  -c, --only-checksum   toggle searching by checksum rather than name first
  -i, --interactive     ask for file deletion interactively
  --hash-function {'sha224', 'sha384', 'sha1', 'md5', 'sha512', 'sha256'}
                        set hash function to use for checksums
  --make-link           create hard link rather than remove file
  --remove-links        remove hardlinks rather than skipping


examples:

    find matches with default regex::

        $ twintrim -n ~/downloads

    find matches ignoring the extension::

        $  ls examples/
        Google.html  Google.html~
        $ twintrim -n -p '(^.+?)(?: \(\d\))*\..+' examples/
        examples/Google.html~ would have been deleted

    find matches with "__1" added to basename::

        $ ls examples/underscore/
        file__1.txt  file.txt
        $ twintrim -n -p '(.+?)(?:__\d)*\..*' examples/underscore/
        examples/underscore/file__1.txt to be deleted



Try it out
-----------

If you would like to try it out I have included an example directory. After
cloning the repository, try running::

	python -m twintrimmer.tool examples/


Running the Tests
------------------

To run tests::

    python -m unittest discover -p '*_test.py'

or using nose::

    python3 -m nose --with-json-extended

:note: the requirements-test.txt file is required to run tests. one of the
       dependencies includes a personally patched version of pyfakefs
       which doesn't seem to work on python3.


Hash algorithm options
-----------------------

Depending on your installed OpenSSL library your available algorithms might change.

The following are the hash algorithms guaranteed to be supported by this
module on all platforms.

- sha224
- sha384
- sha1
- md5
- sha512
- sha256

Additionally, these algorithms might be available (potentially more)

- ecdsa-with-SHA1
- whirlpool
- dsaWithSHA
- ripemd160
- md4

For more information on these algorithms please see the hashlib documentation:

	https://docs.python.org/3/library/hashlib.html
