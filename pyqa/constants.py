from pyfiglet import figlet_format
import textwrap

APP_NAME = "pyQA"
LOGO = figlet_format(APP_NAME, font="slant")

DEFUALT_QUERY = "how to center a div"

EPILOG = textwrap.dedent(
    """\
                                    environment variable examples:
                                    PYQA_COLORIZE=1
                                    PYQA_DISABLE_CACHE=1
                                    PYQA_DISABLE_SSL=1
                                    PYQA_SEARCH_ENGINE=google
                                    PYQA_URL=serverfault.com
                                    """
)
# variables for text formatting, prepend to string to begin text formatting.
BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
UNDERLINE = "\033[4m"
END_FORMAT = "\033[0m"  # append to string to end text formatting.

NO_RESULTS_MESSAGE = "Sorry, couldn't find any help with that topic"
NO_ANSWER_MSG = "< no answer given >"

# stash options
STASH_SAVE = "save"
STASH_VIEW = "view"
STASH_REMOVE = "remove"
STASH_EMPTY = "empty"

BLOCKED_ENGINES = []

SCHEME = "https://"
VERIFY_SSL_CERTIFICATE = True

SUPPORTED_SEARCH_ENGINES = ("google", "bing", "duckduckgo")

DEFAULT_URL = "stackoverflow.com"

USER_AGENTS = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0",
    "Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0",
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) "
        "Chrome/19.0.1084.46 Safari/536.5"
    ),
    (
        "Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46"
        "Safari/536.5"
    ),
)

SEARCH_URLS = {
    "bing": SCHEME + "www.bing.com/search?q=site:{0}%20{1}&hl=en",
    "google": SCHEME + "www.google.com/search?q=site:{0}%20{1}&hl=en",
    "duckduckgo": SCHEME + "duckduckgo.com/html?q=site:{0}%20{1}&t=hj&ia=web",
}

BLOCK_INDICATORS = (
    'form id="captcha-form"',
    "This page appears when Google automatically detects requests coming from your computer "
    'network which appear to be in violation of the <a href="//www.google.com/policies/terms/">Terms of Service',
)

CACHE_EMPTY_VAL = "NULL"
CACHE_ENTRY_MAX = 128

URL = "https://stackoverflow.com/questions/64007220/how-to-use-django-filters-to-filter-for-many-values-for-the-same-field"
