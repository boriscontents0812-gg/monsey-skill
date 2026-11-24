"""SF Pro text drawing with real GPOS kerning + tracking (Pillow has no shaping here)."""
from fontTools.ttLib import TTFont
from PIL import ImageFont
_cache = {}
class Kern:
    def __init__(self, path):
        f = TTFont(path)
        self.cmap = f.getBestCmap(); self.upm = f['head'].unitsPerEm
        self.hmtx = f['hmtx'].metrics
        gpos = f['GPOS'].table
        lis = []
        for fr in gpos.FeatureList.FeatureRecord:
            if fr.FeatureTag == 'kern':
                for i in fr.Feature.LookupListIndex:
                    if i not in lis: lis.append(i)
        self.subs = []
        for li in sorted(lis):
            lk = gpos.LookupList.Lookup[li]
            for st in lk.SubTable:
                if lk.LookupType == 9: st = st.ExtSubTable
                if getattr(st, 'LookupType', 2) != 2 and lk.LookupType not in (2, 9): continue
                if not hasattr(st, 'Coverage'): continue
                if st.Format == 1:
                    d = {}
                    for i, g1 in enumerate(st.Coverage.glyphs):
                        for pvr in st.PairSet[i].PairValueRecord:
                            v = getattr(pvr.Value1, 'XAdvance', 0) if pvr.Value1 else 0
                            d[(g1, pvr.SecondGlyph)] = v or 0
                    self.subs.append(('p', set(st.Coverage.glyphs), d))
                else:
                    self.subs.append(('c', set(st.Coverage.glyphs), (st.ClassDef1.classDefs if st.ClassDef1 else {}, st.ClassDef2.classDefs if st.ClassDef2 else {}, st.Class1Record)))
    def gname(self, ch):
        return self.cmap.get(ord(ch))
    def pair(self, a, b):
        g1, g2 = self.gname(a), self.gname(b)
        if g1 is None or g2 is None: return 0
        for kind, cov, data in self.subs:
            if g1 not in cov: continue
            if kind == 'p':
                if (g1, g2) in data: return data[(g1, g2)]
            else:
                cd1, cd2, rec = data
                c1 = cd1.get(g1, 0); c2 = cd2.get(g2, 0)
                v = rec[c1].Class2Record[c2].Value1
                v = getattr(v, 'XAdvance', 0) if v else 0
                if v: return v
                # class pair with 0 still terminates in OpenType only if the pair is matched; continue to be lenient
        return 0
    def adv(self, ch):
        g = self.gname(ch)
        return self.hmtx[g][0] if g in self.hmtx else 0
def kern_for(path):
    if path not in _cache: _cache[path] = Kern(path)
    return _cache[path]
def layout(text, path, size, track=0.0):
    """return list of (char, x) pen positions and total advance, in px"""
    k = kern_for(path); s = size / k.upm
    xs = []; x = 0.0
    for i, ch in enumerate(text):
        xs.append((ch, x))
        x += k.adv(ch) * s + track
        if i + 1 < len(text): x += k.pair(ch, text[i + 1]) * s
    return xs, x - track
def draw(d, xy, text, path, size, track=0.0, fill=255, font=None):
    font = font or ImageFont.truetype(path, size)
    x0, y0 = xy
    pos, w = layout(text, path, size, track)
    for ch, x in pos:
        d.text((x0 + x, y0), ch, font=font, fill=fill)
    return w
