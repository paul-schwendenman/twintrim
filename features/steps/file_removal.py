'''
Steps for creating and checking the existance of files
'''
#pylint: disable=missing-docstring, function-redefined, unused-argument
from behave import given, when, then
import os
import shutil
import subprocess
import sys

def run_program(command, stdinput=""):
    doit = subprocess.Popen(command, universal_newlines=True, shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE)
    (done, fail) = doit.communicate(stdinput)
    code = doit.wait()
    sys.stdout.write(done)
    sys.stderr.write(fail)
    return code, done, fail

@given(u'we have two matching files "{filename1}" and "{filename2}"')
def step_impl(context, filename1, filename2):
    data = "dummy data\n"
    with open(os.path.join(context.path, filename1), 'w') as file1:
        file1.write(data)
    with open(os.path.join(context.path, filename2), 'w') as file2:
        file2.write(data)

@given(u'we have two different files "{filename1}" and "{filename2}"')
def step_impl(context, filename1, filename2):
    data1 = "dummy data\n"
    with open(os.path.join(context.path, filename1), 'w') as file1:
        file1.write(data1)
    data2 = "dummer data\n"
    with open(os.path.join(context.path, filename2), 'w') as file2:
        file2.write(data2)

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

@given(u'"{filename}" was last modified {minutes} minutes ago')
def step_impl(context, filename, minutes):
    filepath = os.path.join(context.path, filename)
    statinfo = os.stat(filepath)
    mtime = statinfo.st_mtime - 60 * int(minutes)
    atime = statinfo.st_atime
    os.utime(filepath, (atime, mtime))
