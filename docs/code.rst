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
              remove_file, create_filenames, main

Clumpers
----------

.. autoclass:: twintrimmer.twintrimmer.Clumper
    :members: make_clump, dump_clumps

.. autoclass:: twintrimmer.twintrimmer.PathClumper
    :members: make_clump, dump_clumps

.. autoclass:: twintrimmer.twintrimmer.RegexClumper
    :members: make_clump, dump_clumps

.. autoclass:: twintrimmer.twintrimmer.HashClumper
    :members: make_clump, dump_clumps

Sifter
-------

.. autoclass:: twintrimmer.twintrimmer.Sifter
    :members: sift, filter
.. autoclass:: twintrimmer.twintrimmer.ShortestSifter
    :members: sift, filter
.. autoclass:: twintrimmer.twintrimmer.InteractiveSifter
    :members: sift, filter

Documentation for the command line tool
----------------------------------------

.. automodule:: twintrimmer.tool
    :members: terminal
