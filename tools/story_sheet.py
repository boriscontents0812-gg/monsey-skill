import os, sys
from PIL import Image, ImageDraw
d = sys.argv[1]; out = sys.argv[2]; cols = int(sys.argv[3]) if len(sys.argv) > 3 else 6
fs = sorted(f for f in os.listdir(d) if f.startswith('slide-') and f.endswith('.png'))
c = 400
rows = (len(fs) + cols - 1) // cols
S = Image.new('RGB', (cols * c, rows * c), (40, 40, 40)); D = ImageDraw.Draw(S)
for i, f in enumerate(fs):
    im = Image.open(os.path.join(d, f)).convert('RGB'); im.thumbnail((c - 8, c - 8))
    x = (i % cols) * c; y = (i // cols) * c
    S.paste(im, (x + (c - im.width) // 2, y + (c - im.height) // 2))
    D.text((x + 6, y + 4), f[6:8], fill=(255, 220, 0))
S.save(out, quality=88)
