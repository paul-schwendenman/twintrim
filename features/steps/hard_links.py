#pylint: disable=missing-docstring, function-redefined
from behave import given, then
import os.path

@then(u'"{filename1}" is link of "{filename2}"')
def step_impl(context, filename1, filename2):
    assert os.path.samefile(os.path.join(context.path, filename1),
                            os.path.join(context.path, filename2))

@given(u'we have two linked files "{filename1}" and "{filename2}"')
def step_impl(context, filename1, filename2):
    data = "dummy data\n"
    with open(os.path.join(context.path, filename1), 'w') as file1:
        file1.write(data)
    os.link(os.path.join(context.path, filename1),
            os.path.join(context.path, filename2))
