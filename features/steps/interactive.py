'''
Steps for running interactively
'''
#pylint: disable=missing-docstring
from behave import when
from file_removal import run_program

@when(u'we run "twintrim" with interactive mode')
def step_impl(context):
    run_program(' '.join(['twintrim -i', context.path]), 'foo (1).txt')
