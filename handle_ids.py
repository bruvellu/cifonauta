#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#

import os
import pickle
from media_utils import read_iptc, rename_file

# Directory with symbolic links files.
BASEPATH = os.path.join(os.environ['HOME'], 'linked_media/oficial')
# Pickled file with unique names dumped from database.
UNIQUE_NAMES = pickle.load(open('unique_names.pkl'))


class File:
    def __init__(self, root, filename):
        self.root = root
        self.filename = filename
        self.filepath = os.path.join(root, filename)
        self.abspath = os.path.join(BASEPATH, self.filepath)
        self.txt_abspath = self.check_txt()
        self.authors = self.get_authors()
        if not self.check_name():
            self.unique_name = ''
            self.get_unique_name()
            self.rename_new()

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
            return info_iptc.data['by-line']
        else:
            if self.txt_abspath:
                info_mov = pickle.load(open(self.txt_abspath))
                return info_mov['author']
            else:
                return ''

    def check_name(self):
        '''Verifies if file name is an ID.'''
        if self.filename in UNIQUE_NAMES:
            return True
        else:
            return False

    def get_unique_name(self):
        '''Get a new unique name.'''
        self.unique_name = rename_file(self.filename, self.authors)
        if self.check_name():
            self.get_unique_name()

    def rename_new(self):
        '''Rename link with unique name.'''
        self.renamed_path = os.path.join(os.path.split(self.abspath)[0], self.unique_name)
        os.rename(self.abspath, self.renamed_path)
        print('\nRenamed %s to %s' % (self.abspath, self.renamed_path))
        if self.txt_abspath:
            self.renamed_txt_abspath = os.path.join(os.path.split(self.txt_abspath)[0], os.path.splitext(self.unique_name)[0] + '.txt')
            os.rename(self.txt_abspath, self.renamed_txt_abspath)
            print('Renamed %s to %s' % (self.txt_abspath, self.renamed_txt_abspath))


# Search all links in linked_media.
for root, dirs, files in os.walk(BASEPATH):
    for filename in files:
        if not filename.endswith('.txt'):
            # Create instance and rename if necessary.
            one_file = File(root, filename)
