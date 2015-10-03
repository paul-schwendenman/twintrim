'''
magic module to help with setting up behave scenarios
'''
#pylint: disable=unused-argument
import shutil
import tempfile

def before_scenario(context, scenario):
    '''
    create a temporary directory for running the scenario
    '''
    context.path = tempfile.mkdtemp(suffix='twintrimmer')

def after_scenario(context, scenario):
    '''
    remove the temporary directory
    '''
    shutil.rmtree(context.path)
