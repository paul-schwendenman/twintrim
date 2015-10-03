'''
twintrimmer - a duplicate file remover

The goal for this project is to help identify and remove files that have
matching names and content.

Copyright (c) 2015 Paul Schwendenman

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
'''
#from .twintrimmer import (create_filenames, generate_checksum, is_substring,
#                          walk_path,
from .twintrimmer import (generate_checksum_dict, create_filenames,
                          pick_shorter_name, remove_by_checksum, walk_path,
                          Filename, ask_for_best, generate_filename_dict,
                          is_substring, generate_checksum, main,
                          remove_files_for_deletion)
from .twintrimmer import __author__, __email__, __license__, __version__

__all__ = ['create_filenames', 'generate_checksum', 'walk_path', 'main']
