# YouTube-iTunes Sync 1.0

Synchronizes a YouTube music playlist with iTunes. Once synchronized with iTunes they become available on your iPhone and other Apple devices.

This is useful if you have a YouTube playlist full of music or music videos and want to be able to play them anywhere.

## Requirements

* Mac OS X 10.7+ (Lion)
    * 10.6 (Snow Leopard) probably works too, but I have not tested this.
* iTunes 10+
    * Probably any iTunes version works, but this is the one I have tested.
* Python 2.6
    * This is included with the above Mac OS X version.

And additionally:

* **youtube_dl** installed in your `PYTHONPATH`.
    * You will need to download a source package from the [youtube-dl Github page]. The binary version on the main youtube-dl website is not sufficient
    * The [2012.11.29] version is recommend, since it has been tested.
* **ffmpeg** and **ffprobe** commands installed in your system `PATH`
    * You will probably need to [compile ffmpeg] to get **ffprobe**, since
      it is typically not included in binary distributions of ffmpeg.

[youtube-dl Github page]: https://github.com/rg3/youtube-dl/tags
[2012.11.29]: https://github.com/rg3/youtube-dl/archive/2012.11.29.zip
[compile ffmpeg]: http://ffmpeg.org/trac/ffmpeg/wiki/MacOSXCompilationGuide

## Usage

```
./sync_youtube_to_itunes.py <YouTube-Playlist-URL> <Directory-Path> <iTunes-Playlist-Name>
```

For example:

```
./sync_youtube_to_itunes.py http://www.youtube.com/playlist?list=PL5F93ED354981399F /Users/davidf/Music/YT-Music YT-Music
```

### Multi-Step

Or, if you would like to perform the synchronization in two steps for some reason:

```
./sync_youtube_to_filesystem.py <YouTube-Playlist-URL> <Directory-Path>

./sync_filesystem_to_itunes.py <Directory-Path> <iTunes-Playlist-Name>
```

## Special Features

* Handles **[Video Deleted]** items in YouTube playlists
* Unicode support (for playlist item titles and similar)

## Design

Here's how the script works:

* YouTube playlists are downloaded to the local filesystem using the excellent [youtube_dl] library. An invisible `.ordering` file tracks the original order of downloaded items.
    * The youtube-dl library is maintained independently by the community and is regularly updated when YouTube changes their unofficial APIs.
* Downloaded videos are converted to the MP4 (AAC) format that iTunes expects using [ffmpeg].
* iTunes playlists are manipulated using the actual iTunes application via Apple Events sent by the [osascript] tool (available only on Mac OS X).
    * This is much safer than the alternative approach of editing the existing the iTunes Library XML file directly.


[youtube_dl]: http://rg3.github.com/youtube-dl/
[ffmpeg]: http://ffmpeg.org
[osascript]: http://developer.apple.com/library/mac/#documentation/Darwin/Reference/ManPages/man1/osascript.1.html

## Wishlist

Some improvements I would like to make:

* Better error handling.
    * Complain if ffmpeg & ffprobe are not installed.
    * Compiain if the specified filesystem directory does not exist.
* Simplify installation by providing a binary distribution.
    * It is cumbersome to require users to install youtube_dl, ffmpeg, and ffprobe manually.
* Improve marketing by creating a custom website (likely via GitHub Pages).
* &#x2606; Sync the YouTube thumbnail to iTunes as album art.
* Support syncing full *videos* from YouTube playlists to iTunes (in addition to the audio track).
    * For videos unavailable in an iTunes-friendly format (i.e. MP4/M4V), ffmpeg or HandBrakeCLI could be used to transcode videos.
* &#x2606; Download video metadata (ex: title, description, etc) for archival purposes.
* &#x2606; If a video becomes **[Video Deleted]** on YouTube, preserve the downloaded version of the video (if available).
* Improved support for Python 2.6.
    * Fix deprecation warning related to [BaseException.message](http://stackoverflow.com/questions/1272138/baseexception-message-deprecated-in-python-2-6).

Starred items (&#x2606;) are my personal most-wanted improvements.

## License

This software is freeware. For details, see the [LICENSE] file.

[LICENSE]: https://github.com/davidfstr/YouTube-iTunes-Sync/blob/master/LICENSE.txt