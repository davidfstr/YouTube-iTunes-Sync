#!/usr/bin/env python

"""
Synchronizes a YouTube playlist with a playlist in iTunes.
"""

import sync_youtube_to_filesystem as step_1
import sync_filesystem_to_itunes as step_2
import sys


def main(args):
    # Parse arguments
    playlist_url, filesystem_dirpath, itunes_playlist_name = args
    
    step_1.main([playlist_url, filesystem_dirpath])
    step_2.main([filesystem_dirpath, itunes_playlist_name])


if __name__ == '__main__':
    main(sys.argv[1:])
