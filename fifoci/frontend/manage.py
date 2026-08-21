#!/usr/bin/env python
import os
import sys


def main():
    settings_name = "test" if len(sys.argv) > 1 and sys.argv[1] == "test" else "local"
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", f"fifoci.frontend.settings.{settings_name}"
    )

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
