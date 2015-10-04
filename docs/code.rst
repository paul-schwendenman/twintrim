Documentation for the Code
**************************

Base twintrimmer module
------------------------

.. automodule:: twintrimmer

Twintrimmer Functions
----------------------------

.. automodule:: twintrimmer.twintrimmer
    :members:
              remove_by_clump, Filename,
              remove_file, create_filenames, walk_path

Clumpers
----------

.. autoclass:: twintrimmer.twintrimmer.Clumper
    :members: make_clump, dump_clumps

.. autoclass:: twintrimmer.twintrimmer.PathClumper
    :members: make_clump, dump_clumps, create_filename_object_from_string, create_filenames_from_list

.. autoclass:: twintrimmer.twintrimmer.RegexClumper
    :members: make_clump, dump_clumps

.. autoclass:: twintrimmer.twintrimmer.HashClumper
    :members: make_clump, dump_clumps

.. autoclass:: twintrimmer.twintrimmer.ClumperError


Pickers
--------

.. autoclass:: twintrimmer.twintrimmer.Picker
    :members: sift
.. autoclass:: twintrimmer.twintrimmer.ShortestPicker
    :members: sift, pick_shorter_name
.. autoclass:: twintrimmer.twintrimmer.InteractivePicker
    :members: sift

Documentation for the command line tool
----------------------------------------

.. automodule:: twintrimmer.twintrimmer
    :members: main
