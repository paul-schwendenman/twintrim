from behave import then
import os.path

@then(u'"{filename1}" is link of "{filename2}"')
def step_impl(context, filename1, filename2):
    assert os.path.samefile(os.path.join(context.path, filename1),
                            os.path.join(context.path, filename2))
