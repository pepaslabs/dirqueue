# dirqueue

A simple filesystem-based queue processing system

## Rationale

I threw this together because I needed to download a bunch of videos from YouTube.  It does that job pretty well!

## How does it work?

- Drag a file into the `queue/in` directory (a directory created by `run.py`)
- `run.py` will move it into `queue/active` and call `job_processor <file>`
- If `job_processor` succeeds, `run.py` moves the file into `queue/done`
- If `job_processor` fails, `run.py` moves the file into `queue/failed`
- `run.py` then starts processing the next file in `queue/in`

## How do I use it?

- Write a custom `bin/job_processor` to fit your needs (or symlink one of the provided examples)
- Start it: `cd bin && ./run.py`
- Drag some files into `queue/in` (a directory created by `run.py`)

## Caveat

This is flaky -- do not use it in any sort of production environment.

If you manually remove one of the files from `queue/in`, this seems to cause `watchdog` to get stuck, and the queue has to be killed and restarted (you'll also have to drag the files out of `queue/in` and then drag them back in).

## License

MIT
