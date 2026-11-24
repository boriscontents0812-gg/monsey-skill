# Download TikTok photo-post slides: bash tt_dl.sh outdir < lines "host id expires sig"; also writes outdir_sheet.jpg
mkdir -p "$1"; n=0
while read h id ex sig; do n=$((n+1)); curl -s -o "$1/$(printf %02d $n).jpg" -e https://www.tiktok.com/ "https://$h-common-sign.tiktokcdn.com/tos-alisg-i-photomode-sg/$id~tplv-photomode-image.jpeg?dr=14555&x-expires=$ex&x-signature=$sig&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=9b759fb9&idc=my&ftpl=1"; done
python - "$1" <<'PY'
import cv2,glob,numpy as np,sys
fs=sorted(glob.glob(sys.argv[1]+'/*.jpg'));t=[]
for f in fs:
  im=cv2.imread(f);h,w=im.shape[:2];s=cv2.resize(im,(330,int(330*h/w)));c=np.zeros((440,330,3),np.uint8);c[:min(440,s.shape[0])]=s[:440];cv2.putText(c,f[-6:-4],(4,22),0,.7,(0,255,255),2);t.append(c)
while len(t)%6:t.append(np.zeros_like(t[0]))
cv2.imwrite(sys.argv[1]+'_sheet.jpg',np.vstack([np.hstack(t[i:i+6]) for i in range(0,len(t),6)]))
print(len(fs))
PY
