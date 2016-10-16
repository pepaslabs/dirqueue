#!/bin/bash

# Do nothing and succeed.  Use this to test the run.py mechanism (it should move jobs to "queue/done").

# To use this job processor, symlink it into place:
# $ cd dirqueue/bin
# $ ln -s example_job_processors/test_success.sh job_processor
# $ ./run.py

true
