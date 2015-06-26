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

usage: twintrimmer.py [-h] [-n] [-r] [--verbosity VERBOSITY]
                      [--log-file LOG_FILE] [--log-level LOG_LEVEL]
                      [-p PATTERN] [-c]
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

examples:

    find matches with default regex::

        $ ./twintrimmer.py -n ~/downloads

    find matches ignoring the extension::

        $  ls examples/
        Google.html  Google.html~
        $ ./twintrimmer.py -n -p '(^.+?)(?: \(\d\))*\..+' examples/
        examples/Google.html~ to be deleted

    find matches with "__1" added to basename::

        $ ls examples/underscore/
        file__1.txt  file.txt
        $ ./twintrimmer.py -n -p '(.+?)(?:__\d)*\..*' examples/underscore/
        examples/underscore/file__1.txt to be deleted



Try it out
-----------

If you would like to try it out I have included an example directory. After
cloning the repository, try running::

	./twintrimmer.py examples/

