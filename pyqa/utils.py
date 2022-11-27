import logging
import os
import re
from urllib.parse import parse_qs
from urllib.parse import quote as url_quote
from urllib.parse import urlparse
from urllib.request import getproxies

import requests
from rich import print
from rich.align import Align
from rich.panel import Panel
from rich.text import Text

from .constants import (
    END_FORMAT,
    LOGO,
    NO_ANSWER_MSG,
    RED,
    USER_AGENTS,
    VERIFY_SSL_CERTIFICATE,
    URL,
    SEARCH_ENGINE,
    SEARCH_URLS,
    BLOCK_INDICATORS,
    DEFUALT_QUERY,
)

from .erros import BlockError

# =======================================
#        extract links from query      ||
# =======================================


def _extract_links_from_bing(html):
    html.remove_namespaces()
    return [a.attrib["href"] for a in html(".b_algo")("h2")("a")]


def _clean_google_link(link):
    if "/url?" in link:
        parsed_link = urlparse(link)
        query_params = parse_qs(parsed_link.query)
        url_params = query_params.get("q", []) or query_params.get("url", [])
        if url_params:
            return url_params[0]
    return link


def _extract_links_from_google(query_object):
    html = query_object.html()
    link_pattern = re.compile(rf"https?://{URL}/questions/[0-9]*/[a-z0-9-]*")
    links = link_pattern.findall(html)
    links = [_clean_google_link(link) for link in links]
    return links


def _extract_links_from_duckduckgo(html):
    html.remove_namespaces()
    links_anchors = html.find("a.result__a")
    results = []
    for anchor in links_anchors:
        link = anchor.attrib["href"]
        url_obj = urlparse(link)
        parsed_url = parse_qs(url_obj.query).get("uddg", "")
        if parsed_url:
            results.append(parsed_url[0])
    return results


def _extract_links(html, search_engine):
    if search_engine == "bing":
        return _extract_links_from_bing(html)
    if search_engine == "duckduckgo":
        return _extract_links_from_duckduckgo(html)
    return _extract_links_from_google(html)


def _get_search_url(search_engine):
    return SEARCH_URLS.get(search_engine, SEARCH_URLS["google"])


def _is_blocked(page):
    for indicator in BLOCK_INDICATORS:
        if page.find(indicator) != -1:
            return True

    return False


def _get_links(query):
    search_url = _format_query_url(query)

    try:
        result = _get_result(search_url)
    except requests.HTTPError:
        logging.info("Received HTTPError")
        result = None
    if not result or _is_blocked(result):
        logging.error(
            "%sUnable to find an answer because the search engine temporarily blocked the request. "
            "Attempting to use a different search engine.%s",
            RED,
            END_FORMAT,
        )
        raise BlockError("Temporary block by search engine")

    links = _get_result_links(result)
    return links
    # return list(dict.fromkeys(links))


def _get_result_links(result):
    html = pq(result)
    links = _extract_links(html, SEARCH_ENGINE)
    if len(links) == 0:
        logging.info(
            "Search engine %s found no StackOverflow links, returned HTML is:",
            SEARCH_ENGINE,
        )
        logging.info(result)
    return links


def _format_query_url(query):
    query = query or DEFUALT_QUERY
    query = " ".join(query)
    search_url = _get_search_url(SEARCH_ENGINE).format(URL, url_quote(query))

    logging.info("Searching %s with URL: %s", SEARCH_ENGINE, search_url)
    return search_url  # remove any duplicates


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


random_agent = _random_choice(USER_AGENTS)
HEADER = {"User-Agent": random_agent}

PROXIES = get_proxies()
COOKIES = {"CONSENT": "YES+US.en+20221119-00-0"}


def _get_result(url):
    try:
        resp = pyqa_session.get(
            url,
            headers=HEADER,
            proxies=PROXIES,
            verify=VERIFY_SSL_CERTIFICATE,
            cookies=COOKIES,
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
    logging.info(f"Fetching page: {url}")
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


def _get_answers(args, urls):
    # TODO: use pygments for syntax highlighting
    res = {}

    for i, url in enumerate(urls):
        # return url
        res[i] = _get_answer(args, url)
    return list(res.values())


# =======================================
#            CLI interface            ||
# =======================================


def display_panel(text=None, show_welcome_msg=True):
    if show_welcome_msg:
        display_logo()

    answer = text

    def display_answer(answer):
        print(
            Panel(
                Align.left(
                    Text.from_ansi(answer, no_wrap=True),
                    vertical="middle",
                ),
                border_style="green",
                title="pyQA",
                subtitle="Tank you for using pyQA",
            )
        )

    return display_answer(answer)


def display_logo():
    print(
        Panel(
            Align.center(
                Text.from_ansi(LOGO, no_wrap=True),
                vertical="middle",
            ),
            border_style="green",
            title="pyQA",
            subtitle="Thank you for using pyQA",
        )
    )


def _disply_answers_panel(args):
    urls = _get_links(args["query"])
    n = args["num_asnwers"]
    best_links = urls[:n]
    answers = _get_answers(args, best_links)

    display_logo()

    for answer in answers:
        display_panel(answer, show_welcome_msg=False)
