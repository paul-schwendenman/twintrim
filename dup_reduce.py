# !/usr/bin/python

import os
import re
import pprint

def hashfile(filepath):
    sha1 = hashlib.sha1()
    f = open(filepath, 'rb')
    try:
        sha1.update(f.read())
    finally:
        f.close()
    return sha1.hexdigest()

def flatten_tuple(t):
    return [(a[0], a[1], b[0]) for a, b in t]

for root, dirs, files in os.walk(".", topdown=False):
    #files_list = [(os.path.splitext(file), (file,)) for file in files]
    files_list = flatten_tuple([(os.path.splitext(file), (file,)) for file in files])

    #files_list = [(re.match(r"(\w+) ?(\([0-9]+\))?", file).groups(), ext) for file, ext in files_list]
    
    #roots = set([item[0][0] for item in files_list])
    
    pprint.pprint(files_list)
    print files_list
    #print roots
    
    #for item in roots:
    #    items = [a for a in files_list if a[0][0] == item]
    #    print items
    #	 print [has]
    
    #for name in files:
    #    print(os.path.join(root, name))
    #for name in dirs:
    #    print(os.path.join(root, name))

