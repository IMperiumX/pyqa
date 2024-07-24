"""Console script for pyqa."""

import click

from pyqa import __version__
from pyqa import utils
from pyqa.constants import EPILOG


@click.group(invoke_without_command=True, epilog=EPILOG)
@click.version_option(__version__, message="pyQA, version %(version)s")
@click.option("-a", "--all", is_flag=True)
@click.option("-n", "--num-asnwers", type=click.IntRange(1, 20, clamp=True), default=1)
@click.argument("query", nargs=-1)
@click.option(
    "-e",
    "--engine",
    help="search engine for this query (google, bing, duckduckgo)",
    default="google",
)
@click.pass_context
def main(ctx, **kwargs):
    ctx.ensure_object(dict)
    args = ctx.obj
    get = kwargs.get

    args.update(
        engine=get("engine", "google"),
        all=get("all", False),
        query=get("query", ()),
        num_answers=get("num_answers", 1),
    )
    utils.display_answers_panel(args)


if __name__ == "__main__":
    main(obj={})  # pragma: no cover
