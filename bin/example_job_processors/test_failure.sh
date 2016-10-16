#!/bin/bash

# Do nothing and fail.  Use this to test the run.py mechanism (it should move jobs to "queue/failed").

# To use this job processor, symlink it into place:
# $ cd dirqueue/bin
# $ ln -s example_job_processors/test_failure.sh job_processor
# $ ./run.py

false
