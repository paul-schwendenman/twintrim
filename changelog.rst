Change log
------------------

v0.14
================

- added instructions to build documentation to readme
- more documentation changes

v0.13
================

- added catch for older pythons

v0.12
================

- changed the underlying API to be flatter and more extensible
  - created two clases clumpers and pickers
  - clumpers lump groups of file together
  - pickers select one of the group for a purpose (example: to keeprather than delete)
- added coverage and doc generation to builds
- cleaned up documentation
- Re-arranged the readme file.
- Refactor tests a little
- Flattened the walk_path function


v0.11
================

- added "--version"

v0.10
================

- moved command line interface to better location
- refactor arg parsing to make it testable
- added tests for argument parsing
- added behavior tests to prevent regression in overall functionality

v0.9.1
================

- updated setup.py to fix regression

v0.9
================

- setup sphinx
- improved documentation
- full test coverage


v0.8
================

- reformat project
- more tests

v0.7
================

- isolate argument handling and logging setup

v0.6
================

- added option for making hard links instead of deleting
- added detection for hard links
- added unit tests

v0.5
================

- fix some formatting


v0.4
================

- added option for selecting hashing function
- added some error catching

v0.3
================

- cleaned up code
- added more doc strings


v0.2
================

- added flag for no action
- custom pattern matching
- external log file
- interactive mode
- checksum only mode
