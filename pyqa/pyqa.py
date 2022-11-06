"""Main module."""
import os
import appdirs
from cachelib import NullCache, FileSystemCache

import requests

get_env = os.getenv
from .constants import *


def _get_cache_dir():
    # Get the cache directory
    cache_dir = get_env("PYQA_CACHE_DIR")
    if cache_dir is None:
        cache_dir = appdirs.user_cache_dir(
            appname=APP_NAME
        )  # return /home/yusufadell/.cache/APP_NAME
    return cache_dir


def get_cache():
    # Get the cache
    cache = NullCache()
    cache_dir = _get_cache_dir()
    if cache_dir is not None:
        cache = FileSystemCache(cache_dir, CACHE_ENTRY_MAX, default_timeout=0)
    return cache


if get_env("PYQA_DISABLE_CACHE"):
    # works like an always empty cache
    cache = NullCache()
else:
    cache = get_cache()

pyqa_session = requests.session()
pyqa_session.headers.update({"User-Agent": USER_AGENTS[0]})


def command_line_runner():
    """Command line runner."""
    import click

    from .cli import main

    main()
