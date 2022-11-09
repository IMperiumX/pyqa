import inspect
import logging
import os
from urllib.parse import parse_qs
from urllib.parse import quote as url_quote
from urllib.parse import urlparse
from urllib.request import getproxies

import appdirs
import requests
from cachelib import FileSystemCache
from cachelib import NullCache

from .constants import *
from pyqa import __version__

get_env = os.getenv


def get_cache_dir():
    # Get the cache directory
    cache_dir = get_env("PYQA_CACHE_DIR")
    if cache_dir is None:
        cache_dir = appdirs.user_cache_dir(
            appname=APP_NAME)  # return /home/yusufadell/.cache/APP_NAME
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


URL = get_env("HOWDOI_URL", DEFAULT_URL)

pyqa_session = requests.session()


def _get_search_url(search_engine):
    return SEARCH_URLS.get(search_engine, SEARCH_URLS["google"])


def get_proxies():
    proxies = getproxies()
    filtered_proxies = {}
    for key, value in proxies.items():
        if key.startswith("http"):
            if not value.startswith("http"):
                filtered_proxies[key] = f"http://{value}"
            else:
                filtered_proxies[key] = value
    return filtered_proxies


def _random_int(width):
    bres = os.urandom(width)
    import sys

    if sys.version < "3":
        ires = int(bres.encode("hex"), 16)
    else:
        ires = int.from_bytes(bres, "little")

    return ires


def _random_choice(seq):
    return seq[_random_int(1) % len(seq)]


def _get_result(url):
    try:
        resp = pyqa_session.get(
            url,
            headers={"User-Agent": _random_choice(USER_AGENTS)},
            proxies=get_proxies(),
            verify=VERIFY_SSL_CERTIFICATE,
            cookies={"CONSENT": "YES+US.en+20170717-00-0"},
        )
        resp.raise_for_status()
        return resp.text
    except requests.exceptions.SSLError as error:
        logging.error(
            "%sEncountered an SSL Error. Try using HTTP instead of "
            'HTTPS by setting the environment variable "HOWDOI_DISABLE_SSL".\n%s',
            RED,
            END_FORMAT,
        )
        raise error
