from .config import *
from raven import Client


def set_logging(sentry=None, progname=None):
    if sentry:
        client = Client(sentry)


