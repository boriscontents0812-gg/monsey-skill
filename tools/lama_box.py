"""Remove a small white mark (e.g. a creator watermark) inside a box with LaMa.
python lama_box.py img.jpg x0 y0 x1 y1   (box as fractions of width/height; edits the file in place)"""
import sys

import cv2
import numpy as np

from lama_clean import T, lama

p, (x0, y0, x1, y1) = sys.argv[1], map(float, sys.argv[2:6])
im = cv2.imread(p)
h, w = im.shape[:2]
X0, Y0, X1, Y1 = int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)
hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
m = np.zeros((h, w), np.uint8)
box = (hsv[Y0:Y1, X0:X1, 2] > 150) & (hsv[Y0:Y1, X0:X1, 1] < 60)
m[Y0:Y1, X0:X1] = box
m = cv2.dilate(m, np.ones((15, 15), np.uint8))
assert m.any(), "nothing white in the box"
cy, cx = (Y0 + Y1) // 2, (X0 + X1) // 2
ty, tx = min(max(cy - T // 2, 0), h - T), min(max(cx - T // 2, 0), w - T)
tm = m[ty:ty + T, tx:tx + T]
out = lama(im[ty:ty + T, tx:tx + T], tm)
im[ty:ty + T, tx:tx + T][tm > 0] = out[tm > 0]
cv2.imwrite(p, im, [cv2.IMWRITE_JPEG_QUALITY, 95])
print(p, int(m.sum()), "px")
