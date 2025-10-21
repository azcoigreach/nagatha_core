#!/usr/bin/env python
"""
Entry point for nagatha_core CLI.
"""

import sys

if __name__ == "__main__":
    from nagatha_core.cli import cli
    sys.exit(cli())
