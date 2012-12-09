"""
Provides functions to safely manipulate an iTunes Library on OS X.

Manipulation is performed through the use of Apple Events sent to the iTunes
application. Therefore the iTunes application will be launched if necessary
(in the background). This is a lot safer than editing the iTunes Library XML
file directly, but has the disadvantage of only working on OS X.

Requires:
* Mac OS X 10.7 or later
* iTunes 10 or later
* Python 2.6 or later (but not Python 3)
"""

from contextlib import contextmanager
import json
import os
import os.path
import subprocess2 as subprocess
from subprocess2 import DEVNULL


def playlist_exists(playlist_name):
    return _parse_boolean(_check_output_osascript(
        'tell application "iTunes" to get exists playlist %s' % 
            _quote_string(playlist_name)))

def create_playlist(playlist_name):
    _check_call_osascript(
        'tell application "iTunes" to make new playlist with properties {name:%s}' %
            _quote_string(playlist_name))

def get_playlist_track_names(playlist_name):
    with unshuffled_playlist(playlist_name):
        return _parse_string_array(_check_output_osascript(
            'tell application "iTunes" to get the name of every track in playlist %s' % 
                _quote_string(playlist_name)))

def set_playlist_tracks(playlist_name, track_filepaths):
    with unshuffled_playlist(playlist_name):
        # Remove all old tracks from the playlist.
        # (The tracks will remain in the iTunes Library.)
        _check_call_osascript(
            'tell application "iTunes" to delete tracks in playlist %s' %
                _quote_string(playlist_name))
        
        # Add all new tracks to the playlist.
        # (For each track, if the track was already in the iTunes Library
        #  it will retain its old properties, otherwise a new track will
        #  be added to the iTunes Library.)
        for cur_track_filepath in track_filepaths:
            result = _check_output_osascript(
                'tell application "iTunes" to add POSIX file %s to playlist %s' %
                    (_quote_string(os.path.abspath(cur_track_filepath)),
                     _quote_string(playlist_name)))
            success = (result != '')

# ------------------------------------------------------------------------------

# Useful for temporarily unshuffling an iTunes playlist,
# which is necessary for the reported track order to be consistent.
@contextmanager
def unshuffled_playlist(playlist_name):
    if not _is_playlist_shuffled(playlist_name):
        yield
    else:
        _set_playlist_shuffled(playlist_name, False)
        try:
            yield
        finally:
            _set_playlist_shuffled(playlist_name, True)

def _is_playlist_shuffled(playlist_name):
    return _parse_boolean(_check_output_osascript(
        'tell application "iTunes" to get shuffle of playlist %s' %
            _quote_string(playlist_name)))

def _set_playlist_shuffled(playlist_name, shuffled):
    _check_call_osascript(
        'tell application "iTunes" to set shuffle of playlist %s to %s' %
            (_quote_string(playlist_name), _quote_boolean(shuffled)))

# ------------------------------------------------------------------------------

def _check_output_osascript(command):
    return subprocess.check_output(['osascript', '-s', 's', '-e', command],
        stderr=DEVNULL)

def _check_call_osascript(command):
    subprocess.check_call(['osascript', '-s', 's', '-e', command],
        stdout=DEVNULL, stderr=DEVNULL)

def _parse_boolean(result):
    return result.rstrip('\r\n') == 'true'

def _parse_string_array(result):
    # HACK: The output format is similar enough to JSON that we will parse it as JSON.
    return json.loads('[' + result.rstrip('\r\n')[1:-1] + ']')

def _quote_string(value):
    return '"%s"' % value.replace('"', '\"')

def _quote_boolean(value):
    return 'true' if value else 'false'