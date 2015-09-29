from behave import given, when, then
import os
import shutil
import subprocess

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
    subprocess.call([program, context.path])
