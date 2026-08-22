#!/usr/bin/env python3
"""
One-time utility: pull the five Google Places photos into assets/ and repoint
index.html at them.

Why this exists
---------------
index.html currently hotlinks five photos from lh3.googleusercontent.com. Those
are signed Google Places URLs: they expire, and when they do the page loses its
photos silently. This script downloads them, resizes and compresses them for
mobile, and rewrites the <img> tags to relative paths so the page stops
depending on Google.

It could not be run when the page was set up, because the sandbox doing the
work was blocked from reaching lh3.googleusercontent.com by network policy.
Run it from any machine with normal internet access.

Usage
-----
    pip install Pillow
    cd vineyard-birthday
    python3 assets/localize-photos.py

What it does
------------
  * downloads all five photos first, and stops without touching anything if any
    one of them fails (a dead signed URL should be reported, not papered over)
  * resizes each so the longest edge is 1200px
  * writes a .webp and a .jpg for each, stepping quality down until both are
    under ~200KB
  * rewrites index.html to use <picture> with a WebP source and a JPEG fallback
  * adds the small CSS rule that keeps <picture> laying out exactly like the
    bare <img> did, so the design does not shift

Safe to re-run: it writes index.html.bak first and skips work already done.
"""

import io, os, re, sys, shutil, urllib.request

HERE     = os.path.dirname(os.path.abspath(__file__))
PAGE     = os.path.join(os.path.dirname(HERE), "index.html")
ASSETS   = HERE
MAX_EDGE = 1200
MAX_BYTES = 200 * 1024

# Filenames are assigned in the order the photos appear in index.html.
NAMES = [
    "01-hero-tsali-notch",
    "02-estate-vines",
    "03-walnut-hollow-ranch",
    "04-tasting-room",
    "05-cherohala-skyway",
]

# The <picture> element is inline by default; the original <img> tags rely on
# width/height:100% against their container. This keeps the geometry identical.
CSS_SHIM = """
  /* localized photos: keep <picture> laying out exactly as the bare <img> did */
  .hero-img picture,.estate figure picture,.day figure picture{
    display:block;width:100%;height:100%;
  }
"""
CSS_ANCHOR = "  /* ================= velvet plum envelope intro ================= */"


def read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)
    return os.path.getsize(dest)


def encode(img, path, fmt):
    """Write img to path, stepping quality down until it fits MAX_BYTES."""
    for q in (85, 80, 75, 70, 65, 60, 55, 50):
        img.save(path, fmt, quality=q, method=6) if fmt == "WEBP" \
            else img.save(path, fmt, quality=q, optimize=True, progressive=True)
        if os.path.getsize(path) <= MAX_BYTES:
            return q, os.path.getsize(path)
    return q, os.path.getsize(path)


def main():
    try:
        from PIL import Image
    except ImportError:
        sys.exit("Pillow is required:  pip install Pillow")

    html = read(PAGE)
    urls = re.findall(r'src="(https://lh3\.googleusercontent\.com/[^"]+)"', html)

    if not urls:
        print("No lh3.googleusercontent.com URLs left in index.html -- already localized.")
        return 0
    if len(urls) != len(NAMES):
        sys.exit("Expected %d photo URLs, found %d. Aborting rather than guessing."
                 % (len(NAMES), len(urls)))

    # --- 1. download everything up front; abort as a group on any failure ----
    raw, failures = {}, []
    for name, url in zip(NAMES, urls):
        tmp = os.path.join(ASSETS, name + ".orig")
        try:
            size = download(url, tmp)
            raw[name] = tmp
            print("  downloaded  %-24s %7.1f KB" % (name, size / 1024))
        except Exception as e:
            code = getattr(e, "code", None)
            failures.append((name, code or type(e).__name__, url))
            print("  FAILED      %-24s %s" % (name, code or e))

    if failures:
        print("\n%d photo(s) could not be downloaded. index.html was NOT modified." % len(failures))
        for name, code, url in failures:
            print("\n  %s  (HTTP %s)\n  %s" % (name, code, url))
        print("\nSource replacements for these, then re-run.")
        for t in raw.values():
            os.path.exists(t) and os.remove(t)
        return 1

    # --- 2. resize + encode --------------------------------------------------
    print()
    total = 0
    for name in NAMES:
        img = Image.open(raw[name])
        img = img.convert("RGB")
        img.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)
        wq, wsz = encode(img, os.path.join(ASSETS, name + ".webp"), "WEBP")
        jq, jsz = encode(img, os.path.join(ASSETS, name + ".jpg"), "JPEG")
        total += wsz
        print("  %-24s %dx%d  webp %5.1f KB (q%d)  jpg %5.1f KB (q%d)"
              % (name, img.width, img.height, wsz / 1024, wq, jsz / 1024, jq))
        os.remove(raw[name])
    print("\n  WebP total: %.1f KB" % (total / 1024))

    # --- 3. rewrite index.html ----------------------------------------------
    shutil.copyfile(PAGE, PAGE + ".bak")
    out = html
    for name, url in zip(NAMES, urls):
        # capture the whole <img ...> tag carrying this src, keep every other attribute
        m = re.search(r'<img\b[^>]*src="%s"[^>]*>' % re.escape(url), out)
        if not m:
            sys.exit("Could not locate the <img> tag for %s -- aborting." % name)
        tag = m.group(0)
        newtag = tag.replace(url, "assets/%s.jpg" % name)
        out = out.replace(tag,
            '<picture><source srcset="assets/%s.webp" type="image/webp">%s</picture>'
            % (name, newtag))

    if CSS_SHIM.strip() not in out:
        if CSS_ANCHOR not in out:
            sys.exit("Could not find the CSS anchor to insert the <picture> rule.")
        out = out.replace(CSS_ANCHOR, CSS_SHIM + "\n" + CSS_ANCHOR, 1)

    with io.open(PAGE, "w", encoding="utf-8") as f:
        f.write(out)

    print("\nRewrote index.html (backup at index.html.bak).")
    print("Open it and check the five photos, then delete the .bak and the .orig files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
