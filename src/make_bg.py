"""Generate the soft motion-blurred sage/mint/cream streak backgrounds (img/bg.webp, img/bg-dark.webp)."""
import os, numpy as np
from PIL import Image, ImageFilter
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rng = np.random.default_rng(7)

def make(palette, out, W=900, H=1600, angle=-28):
    S = 2200  # oversized square canvas so rotation leaves no corners
    xs = np.linspace(0, 1, S)
    # base: smooth random walk across the palette, stretched along y -> streaks
    def smooth(n, k):
        v = rng.random(n); 
        for _ in range(k): v = np.convolve(v, np.ones(9)/9, mode="same")
        return (v - v.min()) / (v.max() - v.min() + 1e-9)
    t = 0.65*smooth(S, 30) + 0.35*smooth(S, 4)   # broad bands + fine streaks
    t = np.argsort(np.argsort(t)) / (S-1)            # equalize so the full palette shows
    t = np.clip(t, 0, 1)
    pal = np.array(palette, dtype=float)
    pos = t * (len(pal)-1); i0 = np.floor(pos).astype(int); i1 = np.minimum(i0+1, len(pal)-1); f = (pos-i0)[:, None]
    row = pal[i0]*(1-f) + pal[i1]*f               # (S,3)
    img = np.repeat(row[None, :, :], S, axis=0)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    im = im.rotate(angle, resample=Image.BICUBIC)
    c = (S - W)//2, (S - H)//2
    im = im.crop((c[0], c[1], c[0]+W, c[1]+H))
    # soft light bloom from the upper area
    yy, xx = np.mgrid[0:H, 0:W]
    glow = np.exp(-(((xx-W*0.55)/(W*0.7))**2 + ((yy-H*0.28)/(H*0.35))**2))[..., None]
    arr = np.asarray(im, dtype=float)
    # deeper tone pooled toward lower-left, airy light toward upper-right (like the reference)
    shade = np.clip(((H-yy)/H*0.6 + xx/W*0.4), 0, 1)[..., None]
    arr = arr*(0.82+0.22*shade)
    arr = arr*(1-0.45*glow) + np.array(palette[-1], float)*0.45*glow
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(22))
    # fine grain to avoid banding
    a = np.asarray(im, dtype=float) + rng.normal(0, 1.6, (H, W, 1))
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(os.path.join(here, "img", out), "WEBP", quality=72, method=6)
    print(out, os.path.getsize(os.path.join(here, "img", out))//1024, "KB")

light = [(96,134,86),(140,172,118),(182,206,160),(214,230,200),(236,242,228),(248,249,242)]
dark  = [(10,18,12),(18,30,20),(28,44,30),(40,60,40),(58,80,54),(80,104,74)]
make(light, "bg.webp")
make(dark, "bg-dark.webp")
