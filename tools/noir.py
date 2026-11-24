"""Film-noir look: black and white, crushed blacks, punchy contrast, vignette, light grain.
python noir.py in.jpg out.jpg"""
import sys

import cv2
import numpy as np

im = cv2.imread(sys.argv[1]).astype(np.float32) / 255
g = im @ np.array([0.114, 0.587, 0.299], np.float32)  # BGR luma
g = np.clip((g - 0.06) / 0.88, 0, 1)
g = g * g * (3 - 2 * g) * 0.7 + g * 0.3  # S-curve: deep shadows, bright highlights
h, w = g.shape
yy, xx = np.mgrid[0:h, 0:w]
r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
g *= np.clip(1.15 - 0.45 * r ** 2, 0.35, 1)  # vignette
g += np.random.default_rng(0).normal(0, 0.018, g.shape).astype(np.float32)  # grain
cv2.imwrite(sys.argv[2], (np.clip(g, 0, 1) * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])
