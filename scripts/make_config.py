#!/usr/bin/env python3
"""Create a runner-local Telegram-iOS build configuration.

The Telegram API credentials are read from environment variables and are never
printed or written anywhere except the temporary build config (mode 0600).
"""
import argparse
import json
import os
import re
from pathlib import Path

BUNDLE_ID = re.compile(r"^[A-Za-z0-9]+(?:[.-][A-Za-z0-9]+)+$")
URL_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*$")


def fail(message: str) -> None:
    raise SystemExit("config error: " + message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    api_id = os.environ.get("TG_API_ID", "").strip()
    api_hash = os.environ.get("TG_API_HASH", "").strip()
    bundle_id = os.environ.get("APP_BUNDLE_ID", "").strip()
    url_scheme = os.environ.get("APP_URL_SCHEME", "tg").strip() or "tg"

    if not api_id.isdecimal():
        fail("TG_API_ID is missing or is not numeric; add it as a repository secret")
    if len(api_hash) != 32 or any(ch not in "0123456789abcdefABCDEF" for ch in api_hash):
        fail("TG_API_HASH is missing or is not a 32-character hexadecimal string; add it as a repository secret")
    if not BUNDLE_ID.fullmatch(bundle_id):
        fail("bundle_id must be a reverse-DNS identifier, for example com.example.tglandscape")
    if not URL_SCHEME.fullmatch(url_scheme):
        fail("APP_URL_SCHEME is not a valid URL scheme")

    template_path = args.upstream / "build-system" / "template_minimal_development_configuration.json"
    if not template_path.is_file():
        fail("upstream build config template not found: " + str(template_path))

    try:
        config = json.loads(template_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail("could not read the upstream template: " + str(exc))

    # The unsigned device build never installs a profile, so the team id is only
    # a syntactically valid placeholder. The IPA is re-signed on the device.
    config.update({
        "bundle_id": bundle_id,
        "api_id": api_id,
        "api_hash": api_hash,
        "team_id": "0000000000",
        "app_center_id": "0",
        "is_internal_build": "true",
        "is_appstore_build": "false",
        "appstore_id": "0",
        "app_specific_url_scheme": url_scheme,
        "premium_iap_product_id": "",
        "enable_siri": False,
        "enable_icloud": False,
    })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    os.chmod(args.output, 0o600)
    print("wrote build config for bundle id " + bundle_id + " (credentials not printed)")


if __name__ == "__main__":
    main()
