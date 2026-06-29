#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Backward-compatible entry point for the SECOND-KNOWLEDGE-BRAIN pipeline.

Delegates to :mod:`interior_layout.knowledge_updater`. Add ``src`` to the path
so the script works without installing the package::

    python tools/knowledge_updater.py            # live crawl (ArXiv API + crawl4ai)
    python tools/knowledge_updater.py --no-crawl4ai --dry-run

Schedule weekly (Linux/macOS cron, Windows Task Scheduler). See
``cron/knowledge_updater.cron``.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.abspath(os.path.join(_HERE, "..", "src"))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from interior_layout.knowledge_updater import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
