#!/usr/bin/env python3
import os
import sys


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from checkin.token_site import TokenSiteConfig, run_as_script, run_token_checkin


CONFIG = TokenSiteConfig(
    platform="Jiuuij",
    env_prefix="JIUUIJ",
    default_base_url="https://jiuuij.de5.net",
)


def main() -> dict:
    return run_token_checkin(CONFIG)


if __name__ == "__main__":
    run_as_script(CONFIG)
