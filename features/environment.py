import shutil
import tempfile

def before_scenario(context, scenario):
    context.path = tempfile.mkdtemp(suffix='twintrimmer')

def after_scenario(context, scenario):
    shutil.rmtree(context.path)
