#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

EXTENSIONS = (
    'jpg', 'jpeg', 'avi', 'mov', 'mp4', 'ogg', 'ogv', 'dv', 'mpg',
    'mpeg', 'flv', 'm2ts', 'wmv', 'txt',
)


class LinkManager:
    '''Handles links and original files.'''
    def __init__(self):
        # Define home.
        home = os.environ['HOME']
        # Directory with original files and folder structure.
        self.storage = os.path.join(home, 'storage/oficial')
        # Directory containing links to original files.
        self.linked_media = os.path.join(home, 'linked_media/oficial')

        # Check if directories exist.
        if not os.path.isdir(self.linked_media):
            os.makedirs(self.linked_media)

        # Variables to be processed. XXX
        self.healthy_links = []
        self.broken_links = {}
        self.tofix = {}
        self.lost = {}

        # List with original files.
        self.sources = self.get_paths(self.storage)

        # List of linked files.
        self.linked_paths = self.get_paths(self.linked_media)

        # Distribute files and links to list variables.
        self.deal_links(self.linked_paths)

    def get_paths(self, folder):
        '''Recursively search files in the directory.'''
        filepaths = []
        for root, dirs, files in os.walk(folder):
            for filename in files:
                if filename.lower().endswith(EXTENSIONS):
                    filepath = os.path.join(root, filename)
                    filepaths.append(filepath)
                else:
                    continue
            else:
                continue
        else:
            print('%s files in folder %s.' % (len(filepaths), folder))

        # Is the folder empty?
        if not filepaths:
            print('Empty folder %s?' % folder)
        return filepaths

    def deal_links(self, paths):
        '''Verify broken links and adds to the right list.'''
        for path in paths:
            linkpath = os.readlink(path)
            if self.check_link(linkpath):
                self.healthy_links.append(linkpath)
            else:
                self.broken_links[path] = linkpath

    def handle_broken(self):
        '''Process broken links

        Returns dictionary with files to fix and lost.
        '''
        if self.broken_links:
            print('\nThere are broken links:')
            for k, v in self.broken_links.iteritems():
                print('\nBROKEN %s -> %s' % (k, v))
                matches = self.get_matches(v)
                # No matches suggests file was deleted.
                if not matches:
                    print('\nNo candidate for %s was found!' % k)
                    # Adds to the list of lost links.
                    self.lost[k] = v
                elif len(matches) == 1:
                    print('AUTOFIX: Link %s will be fixed.' % matches[0])
                    self.tofix[matches[0]] = k
                else:
                    # If it is just a root change, fix it.
                    std_v = v.split('oficial')[1]
                    link_found = False
                    for match in matches:
                        std_match = match.split('oficial')[1]
                        if std_match == std_v:
                            print('AUTOFIX: Link %s will be fixed.' % match)
                            self.tofix[match] = k
                            link_found = True
                            break
                    if not link_found:
                        print('\nSelect the correct path:\n')
                        print('\t%s\n' % v)
                        for idx, val in enumerate(matches):
                            print('\t[%d] ' % idx + val)
                        index = raw_input('\nType the number of the correct image '
                                        '("i" to ignore; "l" to lost): ')
                        if index == 'i':
                            print('\n\tIgnoring broken link: %s.' % v)
                        elif index == 'l':
                            print('\n\tLost image: %s' % v)
                            self.lost[k] = v
                        elif not index.strip():
                            print('\n\tEmpty value, try again.')
                        elif int(index) > len(matches) - 1:
                            print('\n\tInvalid number, try again.')
                        else:
                            print('\n\tLink %s will be fixed.' % matches[int(index)])
                            self.tofix[matches[int(index)]] = k
                        print
        else:
            print('\nNo broken links.')


    def get_matches(self, link):
        '''Compares broken link destination to the list of original files.'''
        matches = []
        for source in self.sources:
            # Identical names suggest file changed folder.
            if os.path.basename(link) == os.path.basename(source):
                matches.append(source)
        return matches

    def check_link(self, linkpath):
        '''Verifies if symbolic link is broken or not.'''
        try:
            if os.lstat(linkpath):
                return True
        except:
            return False

    def fixlinks(self):
        '''Fix broken links.'''
        if self.tofix:
            print('\nFixing links.')
            for sourcepath, linkpath in self.tofix.iteritems():
                print('FIX %s -> %s' % (linkpath, sourcepath))

                # Instantiate link name.
                linkname = os.path.basename(linkpath)

                # Standardize relative path.
                relative_path = self.standardize_path(sourcepath)

                # Join relative link with unique name.
                relative_link = os.path.join(os.path.dirname(relative_path), linkname)
                # Final link path.
                final_link = os.path.join(self.linked_media, relative_link)

                # Rename file cleaning empty folders.
                os.renames(linkpath, final_link)
                # Remove file to create new updated link.
                os.remove(final_link)
                # Create updated symbolic link.
                os.symlink(sourcepath, final_link)

            if self.check_link(final_link):
                # Needed for the comparison in the add_new function.
                self.healthy_links.append(final_link)
            else:
                print('Problems in the new link: %s' % final_link)
        else:
            print('\nNo link to fix...')


    def standardize_path(self, linkpath):
        '''Standardize link paths.

        >>> path = '/home/nelas/storage/oficial/Vellutini/Clypeaster/DSCN1999.JPG'
        >>> standardize_path(path)
        'Vellutini/Clypeaster/DSCN1999.JPG'
        '''
        # Split by slash.
        linklist = linkpath.split(os.sep)
        try:
            # Point where link will be cut.
            point = linklist.index('oficial')
            del linklist[:point + 1]
            return os.path.join(*linklist)
        except:
            print('Something is wrong with the path %s' % linkpath)
            return None

    def handle_lost(self):
        '''Handle lost files.'''
        if self.lost:
            print('\n%s lost files' % len(self.lost))
            for k, v in self.lost.iteritems():
                print('LOST %s -> %s' % (k, v))
                confirm = raw_input('Erase lost files? (y or n): ')
                if confirm == 'y':
                    try:
                        os.remove(k)
                        print('DELETED %s' % k)
                    except:
                        print('Maybe already gone: %s' % k)
                    try:
                        os.remove(v)
                        print('DELETED %s' % v)
                    except:
                        print('Maybe already gone: %s' % v)
                else:
                    continue
        else:
            print('\nNo file to be deleted.')


    def add_new(self):
        '''Create links for new files.'''
        # Select files without links.
        diff = set(self.sources) - set(self.healthy_links)
        if diff:
            print('\n%s new links will be created.' % len(diff))
            for filepath in diff:
                linkpath = self.standardize_path(filepath)
                linkpath = os.path.join(self.linked_media, linkpath)
                dirpath = os.path.dirname(linkpath)
                # Create necessary directories.
                try:
                    os.makedirs(dirpath)
                    print('Directory created: %s' % dirpath)
                except OSError:
                    pass
                # Remove possible duplicate.
                try:
                    os.remove(linkpath)
                    print('Duplicate %s removed!' % linkpath)
                except:
                    pass
                # Create link.
                try:
                    os.symlink(filepath, linkpath)
                    print('LINK %s -> %s' % (filepath, linkpath))
                except:
                    print('Link could not be created: %s -> %s' %
                            (filepath, linkpath))
        else:
            print('\nNo new file.')

def main():
    print('\nChecking links...')

    # Instantiate manager.
    manager = LinkManager()

    # Handle broken links.
    manager.handle_broken()
    manager.fixlinks()

    # Handle lost links.
    manager.handle_lost()

    # Add new links.
    manager.add_new()

if __name__ == '__main__':
    main()
