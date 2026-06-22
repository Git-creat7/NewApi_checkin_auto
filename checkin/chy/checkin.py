#!/usr/bin/env python3
import os
import sys


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from checkin.token_site import TokenSiteConfig, run_as_script, run_token_checkin, validate_token_site


CONFIG = TokenSiteConfig(
    platform="CHY公益站",
    env_prefix="CHY",
    default_base_url="https://chybenzun.top",
)


def main() -> dict:
    return run_token_checkin(CONFIG)


def validate() -> dict:
    return validate_token_site(CONFIG)


if __name__ == "__main__":
    run_as_script(CONFIG)
