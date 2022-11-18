"""Console script for pyqa."""
import sys
import click
import logging
import os

"""
"-f", "--foo-bar", the name is foo_bar

"-x", the name is x

"-f", "--filename", "dest", the name is dest

"--CamelCase", the name is camelcase

"-f", "-fb", the name is f

"--f", "--foo-bar", the name is f

"---f", the name is _f
"""
from pyqa import __version__


@click.group(invoke_without_command=True)
@click.version_option(message="pyQA, version %(version)s")
@click.argument("query", nargs=-1)
@click.pass_context
def main(ctx, query):
    ctx.ensure_object(dict)
    args = ctx.obj
    args["runner"] = "pyQA"
    query = " ".join(query)
    args["query"] = query
    args["search_engine"] = "google"
    click.echo(args)


@click.option(
    "--version",
    expose_value=False,
    is_flag=True,
)
def version():
    click.echo(f"pyQA, version {__version__}")


@main.command()
@click.option(
    "--explain",
    help="Print explanation of the error.",
    expose_value=False,
    show_default=True,
)
def explain():
    """Explain the error."""
    logging.getLogger().setLevel(logging.INFO)
    logging.info("Version: %s", __version__)


@main.command()
@click.pass_context
def run(ctx):
    from .pyqa import pyqa

    pyqa_result = pyqa(ctx)
    # if os.name == "nt":
    #     # Windows
    #     print(pyqa_result)
    # else:
    #     utf8_result = pyqa_result.encode("utf-8", "ignore")
    #     # Write UTF-8 to stdout
    #     click.echo(utf8_result)
    click.echo(pyqa_result)


# If you have a subcommand called run taking an option called reload
# and the prefix is WEB, then the variable is WEB_RUN_RELOAD.
if __name__ == "__main__":
    main(obj={})  # pragma: no cover
