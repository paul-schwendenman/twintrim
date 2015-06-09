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

usage: twintrimmer.py [-h] [-n] [-r] [-c] [--verbosity VERBOSITY]
                      [--log-file LOG_FILE] [--log-level LOG_LEVEL]
                      path

positional arguments:
  path                  This is the path you want to run the checker against

optional arguments:
  -h, --help            show this help message and exit
  -n, --no-action       This will print the output without changing anyfiles
  -r, --recursive       This option toggles whether the program should search
                        recursively
  -c, --checksum        This option toggles whether the program searchs first
                        by checksum rather than name
  --verbosity VERBOSITY
                        Set debug level
  --log-file LOG_FILE   This option sets a log file to write.
  --log-level LOG_LEVEL
                        Set debug level in log file

Usage example::

	./twintrimmer.py ~/downloads/



Try it out
-----------

If you would like to try it out I have included an example directory. After
cloning the repository, try running::

	./twintrimmer.py examples/

