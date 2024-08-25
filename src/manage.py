#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from jaeger import init_jaeger


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    if not bool(int(os.environ.get("IN_GUNICORN", 1))):
        init_jaeger()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
