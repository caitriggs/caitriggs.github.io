# assets/

This folder is where the page's five photos are meant to live. It is currently
empty of images, on purpose.

`index.html` still hotlinks its five photos from `lh3.googleusercontent.com`.
Those are **signed Google Places URLs**: they expire, and when they do the photos
disappear from the page silently. They should be pulled local.

That could not be done when the page was set up — the machine doing the work was
blocked from reaching `lh3.googleusercontent.com` by network policy (HTTP 403 at
the proxy, on all five URLs). Nothing is wrong with the URLs themselves; they
simply were not reachable from there.

## To finish the job

From any machine with normal internet access:

```sh
pip install Pillow
cd vineyard-birthday
python3 assets/localize-photos.py
```

That downloads all five photos, resizes them to 1200px on the longest edge,
writes a WebP and a JPEG fallback for each (each kept under ~200KB), and
rewrites `index.html` to point at the local files via `<picture>`.

If any photo 404s or 403s, the script stops and names it **without** touching
`index.html`, so you can source a replacement rather than ending up with a
half-localized page.

The photo credits in the page footer are attribution for these Google-sourced
images and must stay as written.
