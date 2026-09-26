"""Helpers for long runs: worker pools that leave Ctrl-C to the main process,
progress lines with an estimated time remaining, and checkpoints so an
interrupted run resumes where it stopped.

Resuming gives exactly the result of an uninterrupted run: every simulation's
seed is fixed in advance by its position in the job list, not by when it runs.
"""
from __future__ import annotations

import json
import os
import signal
import time
from multiprocessing import Pool

import numpy as np


def _ignore_sigint():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def make_pool(cores):
    """A process pool whose workers ignore Ctrl-C: the main process receives
    the interrupt, saves progress and shuts the pool down, instead of every
    worker printing its own traceback."""
    return Pool(cores, initializer=_ignore_sigint)


def fmt_duration(seconds: float) -> str:
    seconds = int(round(seconds))
    if seconds < 90:
        return f"{seconds}s"
    minutes, s = divmod(seconds, 60)
    if minutes < 90:
        return f"{minutes}m"
    hours, m = divmod(minutes, 60)
    return f"{hours}h {m:02d}m"


class Progress:
    """Prints 'k/total (elapsed, ~remaining left)' every `every` items.
    `already` counts items finished in an earlier (resumed) session; the
    time estimate uses only this session's rate."""

    def __init__(self, total, *, already=0, every=100, indent="  "):
        self.total, self.done, self.every, self.indent = total, already, every, indent
        self.start_done = already
        self.t0 = time.time()

    def tick(self, n=1):
        self.done += n
        if self.done % self.every == 0 or self.done == self.total:
            elapsed = time.time() - self.t0
            new = self.done - self.start_done
            eta = ""
            if 0 < new and self.done < self.total:
                eta = f", ~{fmt_duration(elapsed / new * (self.total - self.done))} left"
            print(f"{self.indent}{self.done}/{self.total} ({fmt_duration(elapsed)}{eta})",
                  flush=True)


class Checkpoint:
    """Arrays saved atomically to `path` together with a `key` describing the
    run. `load` returns the arrays only if the saved key matches exactly, so a
    checkpoint is never resumed with different settings."""

    def __init__(self, path, key: dict, every_seconds: float = 120.0):
        self.path = str(path)
        self.key = json.dumps(key, sort_keys=True, default=str)
        self.every = every_seconds
        self._last = time.time()

    def load(self):
        if not os.path.exists(self.path):
            return None
        try:
            with np.load(self.path, allow_pickle=False) as z:
                if str(z["__key__"]) != self.key:
                    print(f"  (ignoring {self.path}: it was made with different settings)")
                    return None
                return {k: z[k] for k in z.files if k != "__key__"}
        except Exception as exc:                     # corrupt or partial file
            print(f"  (ignoring unreadable checkpoint {self.path}: {exc})")
            return None

    def due(self) -> bool:
        return time.time() - self._last >= self.every

    def save(self, **arrays):
        tmp = self.path + ".tmp.npz"
        np.savez(tmp, __key__=np.array(self.key), **arrays)
        os.replace(tmp, self.path)
        self._last = time.time()

    def remove(self):
        for p in (self.path, self.path + ".tmp.npz"):
            if os.path.exists(p):
                os.remove(p)


def interrupted_message(done, total, path):
    return (f"\nInterrupted after {done}/{total}. Progress is saved in {path}; "
            f"run the same command again to resume (add --fresh to start over).")
