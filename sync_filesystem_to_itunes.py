#!/usr/bin/env python

"""
Synchronizes a directory in the filesystem with a playlist in iTunes.

Supports directory playlists with:
    * custom ordering and
    * the same video multiple times.
"""

import codecs
import itunes
import os.path
import sys


def main(args):
    # Parse arguments
    input_dirpath, playlist_name = args
    if not os.path.exists(input_dirpath):
        sys.exit('directory not found: %s' % input_dirpath)
    if not os.path.isdir(input_dirpath):
        sys.exit('not a directory: %s' % input_dirpath)
    
    # Verify that the input directory has an ordering file.
    # TODO: If missing, try to construct a reasonable ordering file
    #       based on files in the directory that have recognized
    #       audio or video file extensions.
    ordering_filepath = os.path.join(input_dirpath, '.ordering')
    if not os.path.exists(ordering_filepath):
        sys.exit('Could not locate the ".ordering" file in the input directory.')
    
    # TODO: Refactor this paragraph shared by 'sync_youtube_to_filesystem.py'
    #       to a common file to reduce duplication.
    # Locate all videos already in the filesystem
    ordering_filepath = os.path.join(input_dirpath, '.ordering')
    if os.path.exists(ordering_filepath):
        filesystem_filenames = []
        with codecs.open(ordering_filepath, 'rt', 'utf-8') as ordering_file:
            for line in ordering_file:
                filesystem_filenames.append(line.rstrip(u'\r\n'))
        
        # Ensure all referenced files actually exist
        real_filesystem_filenames = []
        for filename in filesystem_filenames:
            if os.path.exists(os.path.join(input_dirpath, filename)):
                real_filesystem_filenames.append(filename)
            else:
                print ('WARNING: Could not locate file "%s" referenced by ' +
                    '".ordering" file. Assuming deleted.') % filename
        filesystem_filenames = real_filesystem_filenames
    else:
        filesystem_filenames = []
    
    # Create the iTunes playlist if it doesn't already exist
    if not itunes.playlist_exists(playlist_name):
        itunes.create_playlist(playlist_name)
    
    # Set the playlist contents to the videos in the filesystem
    filesystem_filepaths = [os.path.join(input_dirpath, filename) for filename in filesystem_filenames]
    itunes.set_playlist_tracks(playlist_name, filesystem_filepaths)


if __name__ == '__main__':
    main(sys.argv[1:])
