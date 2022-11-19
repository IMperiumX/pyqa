import inspect
import logging
import os
from urllib.request import getproxies

import appdirs
import requests

from cachelib import FileSystemCache, NullCache
from pyqa.constants import (APP_NAME, CACHE_ENTRY_MAX, END_FORMAT, GREEN,
                            NO_ANSWER_MSG, RED, SUPPORTED_SEARCH_ENGINES,
                            USER_AGENTS, VERIFY_SSL_CERTIFICATE)
from pyqa.erros import (BingValidationError, DDGValidationError,
                        GoogleValidationError)

# =======================================
#         get page content             ||
# =======================================

pyqa_session = requests.session()


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
            cookies={"CONSENT": "YES+US.en+20221119-00-0"},
        )
        resp.raise_for_status()
        return resp.text
    except requests.exceptions.SSLError as error:
        logging.error(
            "%sEncountered an SSL Error. Try using HTTP instead of "
            'HTTPS by setting the environment variable "PYQA_DISABLE_SSL".\n%s',
            RED,
            END_FORMAT,
        )
        raise error


# =======================================
#            extract answer            ||
# =======================================
from pyquery import PyQuery as pq


def _add_links_to_text(element):
    hyperlinks = element.find("a")

    for hyperlink in hyperlinks:
        pquery_object = pq(hyperlink)
        href = hyperlink.attrib["href"]
        copy = pquery_object.text()
        if copy == href:
            replacement = copy
        else:
            replacement = f"[{copy}]({href})"
        pquery_object.replace_with(replacement)


def get_text(element):
    """return inner text in pyquery element"""
    _add_links_to_text(element)
    try:
        return element.text(squash_space=False)
    except TypeError:
        return element.text()


def _get_answer(args, url):  # pylint: disable=too-many-branches
    logging.info("Fetching page: %s", url)
    page = _get_result(url + "?answertab=votes")

    html = pq(page)

    first_answer = html(".answercell").eq(0) or html(".answer").eq(0)

    instructions = first_answer.find("pre") or first_answer.find("code")
    args["tags"] = [t.text for t in html(".post-tag")]
    # make decision on answer body class.
    if first_answer.find(".js-post-body"):
        answer_body_cls = ".js-post-body"
    else:
        # rollback to post-text class
        answer_body_cls = ".post-text"

    if not instructions and not args["all"]:
        logging.info("No code sample found, returning entire answer")
        text = get_text(first_answer.find(answer_body_cls).eq(0))
    elif args["all"]:
        logging.info("Returning entire answer")
        texts = []
        for html_tag in first_answer.items(f"{answer_body_cls} > *"):
            current_text = get_text(html_tag)
            if current_text:
                if html_tag[0].tag in ["pre", "code"]:
                    texts.append(current_text)
                else:
                    texts.append(current_text)
        text = "\n".join(texts)
    else:
        text = get_text(instructions.eq(0))
    if text is None:
        logging.info("%sAnswer was empty%s", RED, END_FORMAT)
        text = NO_ANSWER_MSG
    text = text.strip()
    return text

