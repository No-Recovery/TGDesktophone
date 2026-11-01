#!/usr/bin/env python3
"""Package the built Telegram.app as an unsigned IPA.

Stale _CodeSignature directories and embedded provisioning profiles are removed:
the IPA is intentionally unsigned and is re-signed on the device (eSign,
Sideloadly, TrollStore, ...). The archive is created with ditto so symlinks and
executable permissions survive.
"""
import argparse
import hashlib
import plistlib
import shutil
import subprocess
import tempfile
from pathlib import Path


def fail(message: str) -> None:
    raise SystemExit("package error: " + message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if not args.input.is_file():
        fail("input IPA not found: " + str(args.input))

    with tempfile.TemporaryDirectory(prefix="tg-ipa-") as temp_name:
        work = Path(temp_name)
        subprocess.run(["/usr/bin/ditto", "-x", "-k", str(args.input), str(work)], check=True)

        payload = work / "Payload"
        apps = sorted(payload.glob("*.app")) if payload.is_dir() else []
        if len(apps) != 1:
            fail("expected exactly one Payload/*.app, found " + str(len(apps)))
        app = apps[0]

        info_path = app / "Info.plist"
        if not info_path.is_file():
            fail("main app Info.plist is missing")
        with info_path.open("rb") as stream:
            info = plistlib.load(stream)

        # Remove signatures and profiles deepest-first.
        for path in sorted(payload.rglob("*"), key=lambda item: len(item.parts), reverse=True):
            if path.is_dir() and path.name == "_CodeSignature":
                shutil.rmtree(path, ignore_errors=True)
            elif path.is_file() and path.name == "embedded.mobileprovision":
                path.unlink(missing_ok=True)

        if list(payload.rglob("_CodeSignature")):
            fail("a _CodeSignature directory remains")
        if list(payload.rglob("embedded.mobileprovision")):
            fail("an embedded.mobileprovision remains")

        args.output.parent.mkdir(parents=True, exist_ok=True)
        if args.output.exists():
            args.output.unlink()
        subprocess.run(
            ["/usr/bin/ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", "Payload", str(args.output.resolve())],
            cwd=work,
            check=True,
        )

    size_mib = args.output.stat().st_size / (1024 * 1024)
    digest = hashlib.sha256()
    with args.output.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)

    print("created " + str(args.output) + " ({:.1f} MiB)".format(size_mib))
    print("bundle id: " + str(info.get("CFBundleIdentifier")))
    print("version: " + str(info.get("CFBundleShortVersionString")) + " (" + str(info.get("CFBundleVersion")) + ")")
    print("sha256: " + digest.hexdigest())


if __name__ == "__main__":
    main()
