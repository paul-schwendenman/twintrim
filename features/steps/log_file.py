from behave import when, then
import os

@when(u'we run "{program}" with logging: "--log-file {logfile}" and args: "{args}"')
def step_impl(context, program, args, logfile):
    context.logfile = os.path.join(context.path, logfile)
    args = args + " --log-file {}".format(context.logfile)
    context.execute_steps('''
        When we run "{program}" with args: "{args}"
    '''.format(program=program, args=args))

@then(u'the logfile exists')
def step_impl(context):
    context.execute_steps('''
        Then "{}" still exists
    '''.format(context.logfile))
