#!/usr/bin/env python3
"""Genere des images de nebuleuses en fausses couleurs SHO (SII->R, Ha->G, OIII->B).

Usage : python3 tools/generate_images.py
Sortie : assets/*.jpg
"""

import math
import os

import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
os.makedirs(ASSETS, exist_ok=True)


def smooth_noise(w, h, rng, cells):
    """Bruit value-noise lisse : grille aleatoire rééchantillonnée en bicubique."""
    gw, gh = max(2, cells), max(2, int(cells * h / w))
    grid = rng.random((gh, gw), dtype=np.float32)
    img = Image.fromarray(grid, mode="F").resize((w, h), Image.BICUBIC)
    return np.asarray(img, dtype=np.float64)


def fbm(w, h, rng, octaves=6, start=5):
    total = np.zeros((h, w))
    amp, freq, norm = 1.0, start, 0.0
    for _ in range(octaves):
        n = smooth_noise(w, h, rng, freq)
        total += amp * n
        norm += amp
        amp *= 0.5
        freq *= 2
    total /= norm
    lo, hi = total.min(), total.max()
    return (total - lo) / max(hi - lo, 1e-9)


def smoothstep(x, e0, e1):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def coords(w, h):
    y, x = np.mgrid[0:h, 0:w].astype(np.float64)
    return (x - w / 2) / (w / 2), (y - h / 2) / (h / 2)


def add_stars(img, rng, n, w, h, max_bright=1.0):
    for _ in range(n):
        x = rng.uniform(0, w)
        y = rng.uniform(0, h)
        b = (rng.pareto(2.2) + 0.05) * max_bright
        b = min(b, 3.0)
        r = 0.6 + min(b, 1.5) * 1.6
        tint = rng.uniform(0.75, 1.0)
        win = int(math.ceil(r * 4)) + 1
        x0, x1 = int(x - win), int(x + win + 1)
        y0, y1 = int(y - win), int(y + win + 1)
        x0, y0 = max(x0, 0), max(y0, 0)
        x1, y1 = min(x1, w), min(y1, h)
        if x1 <= x0 or y1 <= y0:
            continue
        yy, xx = np.mgrid[y0:y1, x0:x1]
        g = np.exp(-(((xx - x) ** 2 + (yy - y) ** 2) / (2 * r * r)))
        img[y0:y1, x0:x1, 0] += g * b * tint
        img[y0:y1, x0:x1, 1] += g * b * (0.85 + 0.15 * tint)
        img[y0:y1, x0:x1, 2] += g * b * (0.7 + 0.3 * tint)
        if b > 1.2:  # halo des grosses étoiles
            r2 = r * 5
            g2 = np.exp(-(((xx - x) ** 2 + (yy - y) ** 2) / (2 * r2 * r2)))
            for c in range(3):
                img[y0:y1, x0:x1, c] += g2 * b * 0.12


def finish(channels, w, h, seed, dust_strength=0.75, star_count=260, vignette=0.38):
    """channels = (sii, ha, oiii) normalisés ; applique poussière, étoiles, vignette, stretch."""
    rng = np.random.default_rng(seed)
    sii, ha, oiii = channels

    dust = fbm(w, h, rng, octaves=5, start=7)
    lane = smoothstep(dust, 0.62, 0.82) * dust_strength
    fx = 1.0 - lane
    r = sii * fx
    g = ha * (1.0 - lane * 0.92)
    b = oiii * (1.0 - lane * 1.05)

    img = np.stack([r, g, b], axis=-1)

    ny, nx = coords(w, h)
    dist = np.sqrt(nx ** 2 + ny ** 2)
    img *= (1.0 - vignette * dist ** 2)[:, :, None]

    add_stars(img, rng, star_count, w, h)

    img = np.clip(img, 0, None)
    for c in range(3):
        ch = img[:, :, c]
        peak = np.percentile(ch, 99.9)
        peak = max(peak, 1e-6)
        img[:, :, c] = np.arcsinh(ch / (peak * 0.08)) / np.arcsinh(1 / 0.08)
    img /= img.max()

    lum = img.mean(axis=-1, keepdims=True)
    img = lum + (img - lum) * 1.25
    img = np.clip(img, 0, 1) ** (1 / 1.15)

    out = Image.fromarray((img * 255).astype(np.uint8), "RGB")
    out = out.filter(ImageFilter.GaussianBlur(0.4))
    return out


def blob_mask(w, h, rng, cx=0.0, cy=0.0, radius=0.85, rough=0.55):
    nx, ny = coords(w, h)
    dist = np.sqrt((nx - cx) ** 2 + (ny - cy) ** 2)
    warp = fbm(w, h, rng, octaves=5, start=4)
    return smoothstep(dist, radius * (1 + rough * (warp - 0.5)) * 1.35, radius * (1 + rough * (warp - 0.5)) * 0.45)


def arc_mask(w, h, rng, cx=0.1, cy=0.05, radius=0.62, width=0.16, a0=200, a1=80):
    nx, ny = coords(w, h)
    dx, dy = nx - cx, ny - cy
    dist = np.sqrt(dx ** 2 + dy ** 2)
    ang = (np.degrees(np.arctan2(dy, dx)) + 360) % 360
    ring = np.exp(-(((dist - radius) / width) ** 2))
    if a0 > a1:
        sector = ((ang >= a0) | (ang <= a1))
    else:
        sector = (ang >= a0) & (ang <= a1)
    warp = fbm(w, h, rng, octaves=4, start=6)
    return ring * sector * (0.55 + 0.9 * warp)


def ring_mask(w, h, rng, cx=0.0, cy=0.0, radius=0.55, width=0.13):
    nx, ny = coords(w, h)
    dist = np.sqrt((nx - cx) ** 2 + (ny - cy) ** 2)
    warp = fbm(w, h, rng, octaves=4, start=5)
    ring = np.exp(-(((dist - radius * (0.8 + 0.5 * warp)) / width) ** 2))
    core = smoothstep(dist, 0.22, 0.1)
    return np.clip(ring - core * 0.8, 0, 1), core


def lobes_mask(w, h, rng, sep=0.55, sx=0.30, sy=0.62):
    nx, ny = coords(w, h)
    warp = fbm(w, h, rng, octaves=4, start=5)
    l1 = np.exp(-(((nx + sep) ** 2) / (2 * sx ** 2) + (ny ** 2) / (2 * sy ** 2)))
    l2 = np.exp(-(((nx - sep) ** 2) / (2 * sx ** 2) + (ny ** 2) / (2 * sy ** 2)))
    bar = np.exp(-((ny ** 2) / (2 * 0.13 ** 2))) * smoothstep(np.abs(nx), 0.42, 0.1)
    return np.clip((l1 + l2) * (0.6 + 0.8 * warp) + bar, 0, 1)


def build(w, h, seed, mask, outer=None):
    rng = np.random.default_rng(seed)
    ha_raw = fbm(w, h, rng, octaves=6, start=4)
    clump = fbm(w, h, rng, octaves=5, start=9)
    ha = (ha_raw ** 1.4) * (0.55 + 0.9 * clump) * mask
    ha = ha / max(ha.max(), 1e-9)

    rim = np.gradient(mask)
    edge = np.sqrt(rim[0] ** 2 + rim[1] ** 2)
    oiii_raw = fbm(w, h, rng, octaves=6, start=6)
    oiii = (0.25 + 0.9 * ha) * (0.35 + 1.6 * edge + 0.8 * oiii_raw) * mask
    if outer is not None:
        oiii = oiii + 0.5 * outer * fbm(w, h, rng, octaves=5, start=8)
    oiii = oiii / max(oiii.max(), 1e-9)

    sii_raw = fbm(w, h, rng, octaves=6, start=7)
    boundary = np.clip(mask - smoothstep(mask, 0.55, 0.75), 0, 1)
    sii = (0.35 + 1.5 * boundary) * (0.4 + 1.1 * sii_raw) * mask
    if outer is not None:
        sii = sii + 0.9 * outer * fbm(w, h, rng, octaves=5, start=10)
    sii = sii / max(sii.max(), 1e-9)

    return sii, ha, oiii


def main():
    jobs = [
        # (nom, largeur, hauteur, graine, masque, nombre d'etoiles)
        ("neb-coeur.jpg", 1280, 854, 11, lambda w, h, r: blob_mask(w, h, r, cx=-0.05, cy=0.02, radius=0.8, rough=0.6), 240),
        ("neb-croissant.jpg", 1280, 854, 23, lambda w, h, r: arc_mask(w, h, r, cx=0.12, cy=0.06, radius=0.6, width=0.17, a0=195, a1=75), 300),
        ("neb-rosette.jpg", 1280, 854, 37, lambda w, h, r: ring_mask(w, h, r, cx=0.0, cy=0.0, radius=0.55, width=0.14)[0], 280),
        ("neb-dumbbell.jpg", 1280, 854, 51, lambda w, h, r: lobes_mask(w, h, r, sep=0.5, sx=0.3, sy=0.6), 200),
        ("hero.jpg", 1920, 1080, 77, lambda w, h, r: blob_mask(w, h, r, cx=0.25, cy=-0.1, radius=0.95, rough=0.8), 520),
    ]
    for name, w, h, seed, mask_fn, stars in jobs:
        rng = np.random.default_rng(seed + 999)
        mask = mask_fn(w, h, rng)
        outer = smoothstep(1.0 - mask, 0.0, 0.25) * 0.6
        sii, ha, oiii = build(w, h, seed, mask, outer=outer)
        img = finish((sii, ha, oiii), w, h, seed + 5, dust_strength=0.8, star_count=stars)
        path = os.path.join(ASSETS, name)
        img.save(path, "JPEG", quality=90)
        print("OK", path, img.size)


if __name__ == "__main__":
    main()
