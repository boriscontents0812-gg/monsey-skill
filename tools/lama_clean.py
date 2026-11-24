"""Remove burned-in white captions from a still with LaMa (~/.lama/lama_fp32.onnx, 512x512 tiles at native res).
python lama_clean.py in.jpg out.jpg   -> prints the caption's centre as a fraction of the cleaned height"""
import os
import sys

import cv2
import numpy as np
import onnxruntime as ort

T = 512
sess = ort.InferenceSession(os.path.expanduser("~/.lama/lama_fp32.onnx"), providers=["CPUExecutionProvider"])


def text_mask(im):
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    m = ((hsv[..., 2] > 190) & (hsv[..., 1] < 50)).astype(np.uint8)
    rows = m.sum(1) > im.shape[1] * 0.02  # caption lines are rows full of white letters
    rows = cv2.dilate(rows.astype(np.uint8)[:, None], np.ones((61, 1), np.uint8))[:, 0] > 0
    m[~rows] = 0
    return cv2.dilate(m, np.ones((31, 31), np.uint8)), np.where(rows)[0]  # covers the dark outline + shadow


def lama(tile, mask):
    img = tile[..., ::-1].astype(np.float32).transpose(2, 0, 1)[None] / 255 * (1 - mask[None, None])  # the model expects the hole blanked
    out = sess.run(None, {"image": img, "mask": mask[None, None].astype(np.float32)})[0][0]
    if out.max() <= 1.5:
        out = out * 255
    return np.clip(out.transpose(1, 2, 0)[..., ::-1], 0, 255).astype(np.uint8)


def clean(src, dst):
    im = cv2.imread(src)
    g = im.max(2)
    rows = np.where((g > 14).mean(1) > 0.08)[0]  # drop the black bars
    im = im[rows.min():rows.max() + 1].copy()
    h, w = im.shape[:2]
    m, trows = text_mask(im)
    if not len(trows):
        cv2.imwrite(dst, im); return 0.5
    cy = (trows.min() + trows.max()) / 2
    while m.any():  # 512 tiles at native res, centred on the next masked rows
        ys = np.where(m.any(1))[0]
        y0 = int(min(max(ys.min() - 60, 0), h - T))
        for x0 in sorted(set(list(range(0, max(w - T, 0) + 1, T - 104)) + [w - T])):
            tm = m[y0:y0 + T, x0:x0 + T].copy()
            if not tm.any():
                continue
            out = lama(im[y0:y0 + T, x0:x0 + T], tm)
            sel = tm > 0
            im[y0:y0 + T, x0:x0 + T][sel] = out[sel]
            m[y0:y0 + T, x0:x0 + T] = 0
    cv2.imwrite(dst, im, [cv2.IMWRITE_JPEG_QUALITY, 95])
    return round(cy / h, 3)


if __name__ == "__main__":
    print(clean(sys.argv[1], sys.argv[2]))
