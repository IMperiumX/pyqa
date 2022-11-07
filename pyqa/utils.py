import inspect
import logging
import os
from pyqa import __version__
import appdirs
from cachelib import NullCache, FileSystemCache

get_env = os.getenv
from .constants import *


def get_cache_dir():
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
    cache_dir = get_cache_dir()
    if cache_dir is not None:
        cache = FileSystemCache(cache_dir, CACHE_ENTRY_MAX, default_timeout=0)
    return cache


def _get_cache_key(args):
    frame = inspect.currentframe()
    calling_func = inspect.getouterframes(frame)[1].function
    return f"{calling_func} {args} {__version__}"


def _get_from_cache(cache_key):
    # As of cachelib 0.3.0, it internally logging a warning on cache miss
    current_log_level = logging.getLogger().getEffectiveLevel()
    # Reduce the log level so the warning is not printed
    logging.getLogger().setLevel(logging.ERROR)
    cache = get_cache()
    page = cache.get(cache_key)  # pylint: disable=assignment-from-none
    # Restore the log level
    logging.getLogger().setLevel(current_log_level)
    return page
