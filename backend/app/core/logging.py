from __future__ import annotations

import logging


def configure_logging() -> None:
    # Keep it simple for the initial skeleton.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


