"""Console script for pyqa."""
import sys

import click


from pyqa import __version__
from pyqa import utils
from pyqa.constants import DEFUALT_QUERY, EPILOG


# TODO: take query from the execuatble directly with no sub command (query)
# pyqa <QUERY> instead of pyqa query <QUERY>
@click.group()  # invoke_without_command=True
@click.version_option(__version__, message="pyQA, version %(version)s")
@click.option("-a", "--all", is_flag=True)
@click.option(
    "-e",
    "--engine",
    help="search engine for this query (google, bing, duckduckgo)",
    default="bing",
)
@click.pass_context
def main(ctx, **kwargs):
    ctx.ensure_object(dict)
    args = ctx.obj
    # TODO: set number of answers to show
    args["engine"] = kwargs["engine"]
    args["all"] = kwargs["all"]


@main.command(epilog=EPILOG)
@click.argument("query", nargs=-1)
@click.pass_context
def query(ctx, **kwargs):
    args = ctx.obj

    query = kwargs["query"] or DEFUALT_QUERY
    query = " ".join(query)
    args["query"] = query

    links = utils._get_links(query)

    best_link = links[0]  # TODO: iterate over links until user find his answer
    res = utils._get_answer(
        args, best_link
    )  # TODO: use pygments for syntax highlighting

    utils.display_panel(text=res)


# If you have a subcommand called run taking an option called reload
# and the prefix is WEB, then the variable is WEB_RUN_RELOAD.
if __name__ == "__main__":
    main(obj={})  # pragma: no cover
