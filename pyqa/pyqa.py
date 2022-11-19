"""Main module."""
import os


from .constants import DEFAULT_URL

get_env = os.getenv
URL = get_env("PYQA_URL", DEFAULT_URL)


def command_line_runner():
    """Command line runner."""
    print(f"pyQA Runnser")


if __name__ == "__main__":
    command_line_runner()
