#!/usr/bin/env python

"""
Synchronizes a YouTube playlist with a directory in the filesystem.

Supports YouTube playlists with
    * [Deleted Video] items and
    * the same video multiple times.
"""

import codecs
import os.path
import re
import sys
import youtube_dl
from youtube_dl import FFmpegExtractAudioPP
from youtube_dl.utils import DownloadError
from youtube_dl.utils import sanitize_filename


def main(args):
    # Parse arguments
    playlist_url, output_dirpath = args
    if not os.path.exists(output_dirpath):
        sys.exit('directory not found: %s' % output_dirpath)
    if not os.path.isdir(output_dirpath):
        sys.exit('not a directory: %s' % output_dirpath)
    
    # Default settings
    restrictfilenames = False
    # (TODO: Enable again when it plays nicely with 'extract_audio_for_itunes')
    writeinfojson = False
    extract_audio_for_itunes = True
    
    # Locate all videos already in the filesystem
    ordering_filepath = os.path.join(output_dirpath, '.ordering')
    if os.path.exists(ordering_filepath):
        filesystem_filenames = []
        with codecs.open(ordering_filepath, 'rt', 'utf-8') as ordering_file:
            for line in ordering_file:
                filesystem_filenames.append(line.rstrip(u'\r\n'))
        
        # Ensure all referenced files actually exist
        real_filesystem_filenames = []
        for filename in filesystem_filenames:
            if os.path.exists(os.path.join(output_dirpath, filename)):
                real_filesystem_filenames.append(filename)
            else:
                print ('WARNING: Could not locate file "%s" referenced by ' +
                    '".ordering" file. Assuming deleted.') % filename
        filesystem_filenames = real_filesystem_filenames
    else:
        filesystem_filenames = []
    
    # Prepare downloader
    video_filename_template = u'%(title)s.%(ext)s'
    downloader = youtube_dl.FileDownloader({
        'outtmpl': os.path.join(
            # (Be robust against output_dirpath containing %)
            output_dirpath.replace('%', '%%'),
            video_filename_template),
        'restrictfilenames': restrictfilenames,
        'writeinfojson': writeinfojson,
    })
    if not extract_audio_for_itunes:
        final_filename_template = video_filename_template
    else:
        final_filename_template = video_filename_template.replace(u'%(ext)s', u'm4a')
        downloader.add_post_processor(FFmpegExtractAudioPP(
            preferredcodec='m4a',   # iTunes compatible.
            preferredquality=None,  # default audio quality
            keepvideo=False))
    
    # Locate all videos in the playlist
    video_infos = extract_youtube_playlist_info(playlist_url)
    playlist_filenames = []
    for cur_info in video_infos:
        cur_filename = sanitize_filename(final_filename_template % cur_info, restrictfilenames)
        playlist_filenames.append(cur_filename)
    
    # Download videos to filesystem that are missing
    for cur_info in video_infos:
        cur_filename = sanitize_filename(final_filename_template % cur_info, restrictfilenames)
        if not os.path.exists(os.path.join(output_dirpath, cur_filename)):
            # Download (and optionally extract the audio)
            downloader.process_info(cur_info)
            
            # Verify downloaded
            if not os.path.exists(os.path.join(output_dirpath, cur_filename)):
                raise ValueError('Could not locate downloaded video: %s' % cur_filename)
    
    # Remove filesystem files not in playlist
    playlist_filename_set = set(playlist_filenames)
    for cur_filename in filesystem_filenames:
        if cur_filename not in playlist_filename_set:
            # Remove video (if present)
            video_filepath = os.path.join(output_dirpath, cur_filename)
            if os.path.exists(video_filepath):
                os.remove(video_filepath)
            
            # Remove info json (if present)
            # TODO: This is not the correct path for the info json file
            #       if 'extract_audio_for_itunes' is True.
            #       (The info json will be proceded by the *video* extension,
            #        instead of the output audio file extension.)
            infojson_filepath = os.path.join(output_dirpath, cur_filename + u'.info.json')
            if os.path.exists(infojson_filepath):
                os.remove(infojson_filepath)
    
    # Rewrite the ordering file
    with codecs.open(ordering_filepath, 'wt', 'utf-8') as ordering_file:
        for cur_filename in playlist_filenames:
            ordering_file.write(cur_filename)
            ordering_file.write(u'\n')

# ------------------------------------------------------------------------------

def extract_youtube_playlist_info(youtube_playlist_url):
    """
    Given a YouTube playlist URL, returns a list of video info
    dictionaries describing the contained videos.
    
    Supports [Deleted Video] items.
    
    The implementation of this method would be trivial if:
        (1) YoutubePlaylistIE.extract() actually returned a list
            of video info dictionaries, as the IE superclass requires.
        (2) YoutubeIE recognized [Deleted Video] items natively.
    Alas neither is the case presently.
    """
    
    # (Written to by ExtractingDownloader.download)
    video_infos = []
    
    # `YoutubePlaylistIE.extract()` calls `FileDownloader.download()`
    # on each URL it finds in its playlist (probably in violation of
    # the behavioral contract of `extract`). We change the default
    # `FileDownloader.download()` to gather up the video infos instead
    # of actually performing the downloads.
    class ExtractingDownloader(youtube_dl.FileDownloader):
        def download(self, url_list):
            for url in url_list:
                video_infos.extend(youtube_ie.extract(url))
    
    extracting_downloader = ExtractingDownloader({
        # (This parameter is required even if it is not used. Probably a bug.)
        'outtmpl': 'BOGUS'
    })
    
    # (Shared by multiple calls to ExtractingDownloader.download)
    youtube_ie = YoutubeIEWithMissingVideos(extracting_downloader)
    
    playlist_parser = youtube_dl.YoutubePlaylistIE(extracting_downloader)
    playlist_parser.extract(youtube_playlist_url)
    
    return video_infos


class YoutubeIEWithMissingVideos(youtube_dl.YoutubeIE):
    """
    Extends YoutubeIE with support for [Deleted Video] items
    in a YouTube playlist.
    """
    
    def _real_extract(self, url):
        try:
            return super(YoutubeIEWithMissingVideos, self)._real_extract(url)
        except DownloadError as e:
            if 'HTTP Error 404' in e.message:
                # Encountered a [Deleted Video].
                # Extract what little information we can...
                
                # Extract video id from URL
                mobj = re.match(self._VALID_URL, url, re.VERBOSE)
                video_id = mobj.group(2)
                
                # Output a stripped-down video info dictionary
                return [{
                    'id': video_id,
                    # Make up plausible values for the remaining required keys
                    'url': url,
                    'uploader': '',
                    'upload_date': '20000101',
                    'title': video_id,
                    'ext': 'html',
                    
                    # Special key to mark deleted videos
                    'deleted': True
                }]
            else:
                raise

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    main(sys.argv[1:])