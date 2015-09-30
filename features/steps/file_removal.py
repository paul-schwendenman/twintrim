'''
Acceptance style tests
'''
#pylint: disable=missing-docstring, function-redefined
from behave import given, when, then
import os
import shutil
import subprocess
import sys

def run_program(command):
    doit = subprocess.Popen(command, universal_newlines=True, shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (done, fail) = doit.communicate()
    code = doit.wait()
    sys.stdout.write(done)
    sys.stderr.write(fail)
    return code, done, fail

@given(u'we have two files "{filename1}" and "{filename2}"')
def step_impl(context, filename1, filename2):
    data = "dummy data\n"
    with open(os.path.join(context.path, filename1), 'w') as file1:
        file1.write(data)
    with open(os.path.join(context.path, filename2), 'w') as file2:
        file2.write(data)


@given(u'we have "{program}" installed')
def step_impl(context, program):
    assert shutil.which(program)

@then(u'"{filename}" is removed')
def step_impl(context, filename):
    assert not os.path.exists(os.path.join(context.path, filename))

@then(u'"{filename}" still exists')
def step_impl(context, filename):
    assert os.path.exists(os.path.join(context.path, filename))

@when(u'we run "{program}" with no args')
def step_impl(context, program):
    run_program(' '.join([program, context.path]))

@when(u'we run "{program}" with args: "{args}"')
def step_impl(context, program, args):
    run_program(' '.join([program, args, context.path]))
