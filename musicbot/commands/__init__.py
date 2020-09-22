'''Import dynamically all modules presents in the same folder'''
from click_skeleton import importdir
modules = importdir.import_all_modules(__file__, globals())
