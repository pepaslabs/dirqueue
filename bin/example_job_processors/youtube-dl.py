#!/usr/bin/env python2

# This job processor downloads a youtube video when a link is dragged into the "queue/in" directory.

# To use this job processor, symlink it into place:
# $ cd dirqueue/bin
# $ ln -s example_job_processors/youtube-dl.py job_processor
# $ ./run.py

# exit status codes
exit_status_could_not_read_url = 2

import errno
import os

def mkdir_p(path):
    # thanks to http://stackoverflow.com/a/600612
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

import sys

def is_xml_plist(filepath):
    with open(filepath, 'r') as f:
        first_line = f.readline()
        second_line = f.readline()
    return first_line.startswith("<?xml") and second_line.startswith("<!DOCTYPE plist")

import plistlib

def url_from_xml_plist(filepath):
    root_node = plistlib.readPlist(filepath)
    return root_node["URL"]

def url_from_file(filepath):
    if is_xml_plist(filepath):
        return url_from_xml_plist(filepath)
    else:
        return None

import subprocess

def log(msg):
    sys.stdout.write("Log: %s\n" % msg)

def log_error(msg):
    sys.stderr.write("Error: %s\n" % msg)

def download_youtube_video(url):
    command = ["youtube-dl", "--newline", url]
    log("downloading url: %s" % url)
    subprocess.check_call(command)

if __name__ == "__main__":
    mkdir_p("../videos/")
    os.chdir("../videos/")
    bookmark_filepath=sys.argv[1]
    url = url_from_file(bookmark_filepath)
    if url is None:
        log_error("could not read URL from file: %s" % bookmark_filepath)
        sys.exit(exit_status_could_not_read_url)
    download_youtube_video(url)
