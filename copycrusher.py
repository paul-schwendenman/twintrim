#! /usr/bin/env python3
import os
import hashlib

def generate_checksum(filename):
    md5 = hashlib.md5()
    with open(filename,'rb') as f: 
        for chunk in iter(lambda: f.read(128 * md5.block_size), b''): 
            md5.update(chunk)
    return md5.digest()

def generate_checksum_dict(path):
    checksum_dict = {}

    for root, dirs, filenames in os.walk(path):
        for filename in filenames:
	    print filename
            checksum_dict[filename] = generate_checksum(filename)
            
    return checksum_dict


def main():
    from pprint import pprint
    #pprint(generate_checksum_dict('/home/paul/downloads'))
    pprint(generate_checksum_dict('.'))
                

    

if __name__ == '__main__':
    main()