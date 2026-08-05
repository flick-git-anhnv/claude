"""Entry point: python -m agent_dashboard"""
from __future__ import annotations

import logging

import uvicorn

from . import config


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    )
    uvicorn.run(
        "agent_dashboard.main:app",
        host=config.DASHBOARD_HOST,
        port=config.DASHBOARD_PORT,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
