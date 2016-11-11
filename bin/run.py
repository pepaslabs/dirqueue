#!/usr/bin/env python

# A filesystem-based queue processing system.
# Copyright 2016 Jason Pepas, released under the terms of the MIT license.
# See https://github.com/pepaslabs/dirqueue

# How does this work?
# - Drag a file into the "queue/in" directory.
# - run.py will move it to "queue/active" and call "job_processor <file>" to perform side-effects.
# - If job_processor succeeds, run.py moves the file to "queue/done"
# - If job_processor fails, run.py moves the file to "queue/failed"
# - run.py then starts processing the next file in "queue/in"

# Note: this doesn't seem to be very robust.  Manually removing a file from "queue/in" seems to cause
# watchdog to get wedged.  If that happens, kill run.py, drag the files from "queue/in" to some other
# location, and then drag them back to "queue/in" (I know, lame...).

import errno
import os
import subprocess
import sys
import time

# exit status codes:
exit_status_unknown_error = 1
exit_status_missing_module = 2

try:
    import watchdog
    import watchdog.events
    import watchdog.observers
except ImportError:
    sys.stderr.write("Error: missing Python module 'watchdog.\n")
    sys.stderr.write("Hint: try 'sudo -H pip install watchdog'\n")
    sys.exit(exit_status_missing_module)


def log(msg):
    sys.stdout.write("Log: %s\n" % msg)


def log_error(msg):
    sys.stderr.write("Error: %s\n" % msg)


def mkdir_p(path):
    # thanks to http://stackoverflow.com/a/600612
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def setup_dir_structure():
    mkdir_p('../queue/in')
    mkdir_p('../queue/active/')
    mkdir_p('../queue/failed/')
    mkdir_p('../queue/done/')


def move_job_from_to(job_filename, from_queue, to_queue):
    src_queuepath = "../queue/%s/" % from_queue
    dest_queuepath = "../queue/%s/" % to_queue
    src_filepath = os.path.join(src_queuepath, job_filename)
    dest_filepath = os.path.join(dest_queuepath, job_filename)
    os.rename(src_filepath, dest_filepath)


def flush_active_to_failed():
    # move any jobs in "queue/active" back to "queue/failed"
    for filename in [f for f in os.listdir("../queue/active/")
                     if os.path.isfile(os.path.join("../queue/active", f))]:
        move_job_from_to(filename, "active", "failed")


def run_job_processor(filename):
    filepath = os.path.join("../queue/active/", filename)
    command = ["./job_processor", filepath]
    subprocess.check_call(command)


def handle_new_job(filename):
    log("moving job to active: %s" % filename)
    move_job_from_to(filename, "in", "active")
    try:
        run_job_processor(filename)
    except Exception, e:
        log_error(e)
        log("moving job to failed: %s" % filename)
        move_job_from_to(filename, "active", "failed")
        return
    log("moving job to done: %s" % filename)
    move_job_from_to(filename, "active", "done")


class NewFileHandler(watchdog.events.FileSystemEventHandler):
    def on_created(self, event):
        if type(event) is not watchdog.events.FileCreatedEvent:
            return
        filename = os.path.basename(event.src_path)
        handle_new_job(filename)


def run_queue():
    observer = watchdog.observers.Observer()
    event_handler = NewFileHandler()
    path = "../queue/in"
    observer.schedule(event_handler, path, recursive=False)
    log("running...")
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("stopping...")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    setup_dir_structure()
    flush_active_to_failed()
    run_queue()
