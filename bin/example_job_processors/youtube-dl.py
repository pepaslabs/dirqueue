#!/usr/bin/env python

"""Download the YouTube video listed in a .webloc file.

The .webloc file should be specified as sys.argv[1].

The video will be downloaded to ../videos/by-youtube-id/<youtube_id>.<ext>
and will be symlinked as ../videos/by-channel/<channel>/<title>.<ext>.
"""

import errno
import os
import plistlib
import subprocess
import sys
import tempfile


# exit status codes
exit_status_could_not_read_url = 2


def log(msg):
    sys.stdout.write("Log: %s\n" % msg)


def log_error(msg):
    sys.stderr.write("Error: %s\n" % msg)


def mkdir_p(path):
    """Python equivalent of 'mkdir -p path'."""
    # thanks to http://stackoverflow.com/a/600612
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def url_from_webloc_file(filepath):
    """Return the bookmark URL listed in a .webloc file, or None."""
    def is_xml_plist(filepath):
        with open(filepath, 'r') as f:
            first_line = f.readline()
            second_line = f.readline()
        return (first_line.startswith("<?xml")
                and second_line.startswith("<!DOCTYPE plist"))

    def url_from_xml_plist(filepath):
        root_node = plistlib.readPlist(filepath)
        return root_node["URL"]

    if is_xml_plist(filepath):
        return url_from_xml_plist(filepath)
    else:
        return None


def fetch_youtube_video_metadata(url):
    log("fetching metadata for %s" % url)
    command = ["youtube-dl", "--get-filename", "-o", "%(id)s:%(uploader)s:%(title)s:%(ext)s", url]
    output = subprocess.check_output(command).rstrip()
    return output.split(":")


def download_youtube_video(url, metadata, limit_quality_to_SD=False):
    log("downloading %s" % url)
    command = ["youtube-dl", "--newline"]
    if limit_quality_to_SD:
        command += ["--format", "best[height<=480]"]
    (youtube_id, _, _, ext) = metadata
    command += ["-o", "by-youtube-id/%s.%s" % (youtube_id, ext), url]
    try:
        subprocess.check_call(command)
    except:
        os.unlink(temp_file)
        raise


def symlink_youtube_video(url, metadata):
    (youtube_id, channel, title, ext) = metadata
    dest_dir = "by-channel/%s" % channel
    mkdir_p(dest_dir)
    source_filepath = "../../by-youtube-id/%s.%s" % (youtube_id, ext)
    dest_filepath = "%s/%s.%s" % (dest_dir, title, ext)
    command = ["ln", "-s", source_filepath, dest_filepath]
    subprocess.check_call(command)


if __name__ == "__main__":
    webloc_filepath = sys.argv[1]
    url = url_from_webloc_file(webloc_filepath)
    if url is None:
        log_error("could not read URL from file: %s" % webloc_filepath)
        sys.exit(exit_status_could_not_read_url)

    mkdir_p("../videos/")
    os.chdir("../videos/")
    metadata = fetch_youtube_video_metadata(url)
    download_youtube_video(url, metadata)
    symlink_youtube_video(url, metadata)
