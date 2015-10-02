'''
Steps for creating subdirectories
'''
#pylint: disable=missing-docstring, function-redefined
from behave import given
import os

@given(u'we have a subdirectory "{directory}"')
def step_impl(context, directory):
    os.mkdir(os.path.join(context.path, directory))
