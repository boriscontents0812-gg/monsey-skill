"""Flag new stills that were already used: python dedupe.py NEW_DIR USED_DIR [USED_DIR ...]
Prints each new image with its closest used match; distance <= 10 means it's the same still."""
import glob, os, sys
import cv2
import numpy as np

def dhash(f):
    g = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
    if g is None: return None
    s = cv2.resize(g, (9, 8), interpolation=cv2.INTER_AREA)
    return (s[:, 1:] > s[:, :-1]).flatten()

def imgs(d): return [f for e in ("jpg", "jpeg", "png", "webp") for f in glob.glob(os.path.join(d, "**", "*." + e), recursive=True)]

used = [(f, h) for d in sys.argv[2:] for f in imgs(d) if (h := dhash(f)) is not None]
for f in sorted(imgs(sys.argv[1])):
    h = dhash(f)
    if h is None: continue
    best = min(((int(np.count_nonzero(h != u)), uf) for uf, u in used), default=(64, "-"))
    print(f"{'USED ' if best[0] <= 10 else 'fresh'}  {best[0]:2d}  {os.path.basename(f)}  ~ {os.path.basename(best[1])}")
