#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#

import os
import pickle
from media_utils import read_iptc, rename_file

BASEPATH = os.path.join(os.environ['HOME'], 'linked_media/oficial')
DB_KV = pickle.load(open('db_kv.pkl'))

class File:
    def __init__(self, root, filename):
        # Load data.
        self.new = False
        self.root = root
        self.filename = filename
        self.filepath = os.path.join(root, filename)
        self.abspath = os.path.join(BASEPATH, self.filepath)
        self.txt_abspath = self.check_txt()
        self.authors = self.get_authors()
        self.file_id = self.filename
        if not self.check_id():
            self.get_new_id()
            self.new = True

    def check_txt(self):
        '''Check if there is a .txt associated file.'''
        txt_abspath = os.path.splitext(self.abspath)[0] + '.txt'
        try:
            os.lstat(txt_abspath)
            return txt_abspath
        except:
            return ''

    def get_authors(self):
        '''Reads IPTC and extracts authors.'''
        info_iptc = read_iptc(self.abspath)
        if info_iptc:
            self.authors = info_iptc.data['by-line']
        else:
            if self.txt_abspath:
                info_mov = pickle.load(open(self.txt_abspath))
                self.authors = info_mov['author']
            else:
                self.authors = ''

    def check_id(self):
        '''Verifies if file name is an ID.'''
        if self.file_id in DB_KV.keys():
            return True
        else:
            return False

    def get_new_id(self):
        '''Get a new unique ID.'''
        self.file_id = rename_file(self.filename, self.authors)
        if self.check_id():
            self.get_new_id()

    def rename_new(self):
        '''Rename new file to ID.'''
        self.renamed_path = os.path.join(os.path.split(self.abspath)[0], self.file_id)
        os.rename(self.abspath, self.renamed_path)
        print('\nRenamed %s to %s' % (self.abspath, self.renamed_path))
        if self.txt_abspath:
            self.renamed_txt_abspath = os.path.join(os.path.split(self.txt_abspath)[0], os.path.splitext(self.file_id)[0] + '.txt')
            os.rename(self.txt_abspath, self.renamed_txt_abspath)
            print('Renamed %s to %s' % (self.txt_abspath, self.renamed_txt_abspath))


def check_path(filepath):
    '''Verifies if file path is in pickled database.'''
    db = pickle.load(open('db_vk.pkl'))
    db_paths = db.keys()
    if filepath in db_paths:
        original = os.path.join(BASEPATH, filepath)
        renamed = os.path.join(os.path.split(original)[0], db[filepath])
        os.rename(original, renamed)
        print('Renamed %s to %s' % (original, db[filepath]))


# Search all links in linked_media.
for root, dirs, files in os.walk(BASEPATH):
    for filename in files:
        # Standardize root.
        std_root = root.split('oficial')[1][1:]
        # Define file path.
        filepath = os.path.join(std_root, filename)
        filepath = filepath.decode('utf8')
        # Add file path to list, except for txt files.
        if not filename.endswith('.txt'):
            #check_path(filepath)
            a_file = File(root, filename)
            if a_file.new:
                a_file.rename_new()
    else:
        continue
