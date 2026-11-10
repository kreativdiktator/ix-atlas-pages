#!/usr/bin/env python3
"""Publish only the public book labels and atlas images used by VRChat."""

import argparse
import json
import math
from pathlib import Path
import re
import struct
import tempfile
import time
from urllib.error import URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

SOURCE = "https://immersive-x.de/wp-json/ix/v1/atlas"
PUBLISHED_MANIFEST = "https://kreativdiktator.github.io/ix-atlas-pages/manifest.json"
PAGE_CAPACITY = 256
SLOTS_PER_PAGE = 8
MAX_PNG_BYTES = 32 * 1024 * 1024


class DirectOnly(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def fetch(url, mime, limit):
    request = Request(url, headers={
        "User-Agent": "Immersive-X-Atlas-Pages",
        "Cache-Control": "no-cache",
        "Accept": mime,
    })
    with build_opener(DirectOnly()).open(request, timeout=45) as response:
        if response.headers.get_content_type() != mime:
            raise ValueError(f"Unexpected content type at {url}")
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"Response exceeded the size limit at {url}")
    return data


def public_manifest():
    data = json.loads(fetch(f"{SOURCE}/manifest", "application/json", 4 * 1024 * 1024))
    revision = data.get("revision")
    books = data.get("books")
    if data.get("schemaVersion") != 1 or not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{64}", revision) or not isinstance(books, list):
        raise ValueError("Unexpected WordPress atlas manifest")
    result = []
    occupied = set()
    counts = {}
    for entry in books:
        username, atlas = entry["username"], entry["atlas"]
        page, rect = atlas["pageIndex"], atlas["uvRect"]
        if not isinstance(username, str) or not username.strip() or type(page) is not int or not 0 <= page < PAGE_CAPACITY:
            raise ValueError("Invalid public username or atlas page")
        if not isinstance(rect, list) or len(rect) != 4 or not all(type(n) in (float, int) and math.isfinite(n) for n in rect):
            raise ValueError("Invalid cover coordinates")
        x, y, width, height = rect
        if min(x, y) < 0 or min(width, height) <= 0 or x + width > 1 or y + height > 1:
            raise ValueError("Cover coordinates fall outside the atlas")
        slot = (page, *rect)
        counts[page] = counts.get(page, 0) + 1
        if slot in occupied or counts[page] > SLOTS_PER_PAGE:
            raise ValueError("Duplicate cover slot or too many covers on an atlas page")
        occupied.add(slot)
        result.append({
            "username": username,
            "bodyColor": binding_color(entry.get("bodyColor")),
            "atlas": {"pageIndex": page, "uvRect": rect},
        })
    return {"schemaVersion": 1, "revision": revision, "books": result}, sorted(counts)


def binding_color(value):
    if not isinstance(value, str) or not re.fullmatch(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})", value):
        return "#282b34"
    digits = value[1:].lower()
    return "#" + ("".join(digit * 2 for digit in digits) if len(digits) == 3 else digits)


def download_page(index):
    data = fetch(f"{SOURCE}/pages/{index}.png", "image/png", MAX_PNG_BYTES)
    if (len(data) < 45 or data[:16] != b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
            or struct.unpack(">II", data[16:24]) != (2048, 2048)
            or not data.endswith(b"\x00\x00\x00\x00IEND\xaeB\x60\x82")):
        raise ValueError(f"Invalid 2048 × 2048 atlas image on page {index}")
    return data


def already_published(manifest):
    try:
        published = fetch(PUBLISHED_MANIFEST, "application/json", 4 * 1024 * 1024)
        return json.loads(published) == manifest
    except (URLError, TimeoutError, ValueError):
        return False


def sync(output, only_if_changed):
    if output.exists():
        raise FileExistsError(f"Output directory already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(3):
        try:
            manifest, pages = public_manifest()
            if only_if_changed and already_published(manifest):
                print("The public atlas is already current.")
                return False
            with tempfile.TemporaryDirectory(prefix="atlas-", dir=output.parent) as temporary:
                site = Path(temporary) / "site"
                (site / "pages").mkdir(parents=True)
                total = 0
                for index in pages:
                    image = download_page(index)
                    total += len(image)
                    if total > 950 * 1024 * 1024:
                        raise ValueError("Atlas images exceed the GitHub Pages site size limit.")
                    (site / "pages" / f"{index}.png").write_bytes(image)
                latest, _ = public_manifest()
                if latest != manifest:
                    raise ValueError("The WordPress atlas changed during the download.")
                (site / "manifest.json").write_text(
                    json.dumps(manifest, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n",
                    encoding="utf-8",
                )
                site.rename(output)
            print(f"Prepared {len(manifest['books'])} public books in {len(pages)} atlas pages.")
            return True
        except (URLError, TimeoutError, ValueError, KeyError, TypeError) as error:
            if attempt == 2:
                raise
            print(f"Retrying the atlas export: {error}")
            time.sleep(4)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--only-if-changed", action="store_true")
    options = parser.parse_args()
    sync(options.output, options.only_if_changed)


if __name__ == "__main__":
    main()
