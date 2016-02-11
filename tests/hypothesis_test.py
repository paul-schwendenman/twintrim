'''
Play with hypothesis
'''

from hypothesis import given
import hypothesis.strategies as st
import twintrimmer

@given(st.text(), st.text())
def test_create_filename_from_string(filename, root):
    filename = twintrimmer.twintrimmer.PathClumper.create_filename_from_string(filename, root)
    assert isinstance(filename, twintrimmer.Filename)
