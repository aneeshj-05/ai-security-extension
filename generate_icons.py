"""Generate extension PNG icons using Pillow."""
import math
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).parent / "extension" / "icons"
OUT.mkdir(exist_ok=True)

def draw_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size

    def p(x, y):
        return (x * s / 128, y * s / 128)

    # ── Shield (fills nearly full canvas) ────────────────────────────────────
    shield = [p(64,1), p(122,20), p(122,68), p(106,96), p(64,127), p(22,96), p(6,68), p(6,20)]

    # Deep blue base
    d.polygon(shield, fill=(10, 30, 80, 255))

    # Lighter blue center fill
    inner_fill = [p(64,10), p(112,28), p(112,68), p(98,91), p(64,118), p(30,91), p(16,68), p(16,28)]
    d.polygon(inner_fill, fill=(20, 60, 140, 255))

    # Silver sheen left highlight
    left_sheen = [p(64,2), p(8,22), p(8,68), p(24,94), p(64,126)]
    d.polygon(left_sheen, fill=(180, 200, 230, 35))

    # Silver center highlight streak
    streak = [p(58,2), p(70,2), p(75,35), p(64,52), p(53,35)]
    d.polygon(streak, fill=(210, 225, 255, 55))

    # Outer silver border
    d.polygon(shield, outline=(180, 200, 230, 255), width=max(2, s // 36))

    # Inner blue border
    d.polygon(inner_fill, outline=(80, 140, 220, 160), width=max(1, s // 70))

    # ── Lock shackle ─────────────────────────────────────────────────────────
    scx, scy = p(64, 54)[0], p(64, 54)[1]
    srx = s * 12 / 128
    sry = s * 14 / 128
    shackle_pts = []
    for angle in range(180, 361, 8):
        rad = math.radians(angle)
        shackle_pts.append((
            scx + srx * math.cos(rad),
            scy - sry * math.sin(rad)
        ))
    if len(shackle_pts) >= 2:
        d.line(shackle_pts, fill=(200, 220, 255, 255), width=max(2, s // 36))

    # ── Lock body ─────────────────────────────────────────────────────────────
    lbx1, lby1 = p(49, 63)[0], p(63, 63)[1]
    lbx2, lby2 = p(79, 63)[0], p(92, 63)[1]

    # Shadow
    d.rounded_rectangle([lbx1+1, lby1+1, lbx2+1, lby2+1],
                        radius=max(2, s//32), fill=(5, 15, 40, 200))
    # Silver body
    d.rounded_rectangle([lbx1, lby1, lbx2, lby2],
                        radius=max(2, s//32), fill=(160, 190, 225, 255))
    # Blue top highlight
    d.rounded_rectangle([lbx1, lby1, lbx2, lby1 + (lby2 - lby1) * 0.4],
                        radius=max(2, s//32), fill=(190, 215, 250, 255))
    # Border
    d.rounded_rectangle([lbx1, lby1, lbx2, lby2],
                        radius=max(2, s//32),
                        outline=(100, 160, 230, 220),
                        width=max(1, s // 64))

    # ── Keyhole ───────────────────────────────────────────────────────────────
    kx, ky = p(64, 74)[0], p(64, 74)[1]
    kr = max(2, s * 4 // 128)
    d.ellipse([kx-kr, ky-kr, kx+kr, ky+kr], fill=(15, 35, 80, 255))
    kw = max(1, s * 3 // 128)
    kh = max(2, s * 5 // 128)
    d.rectangle([kx - kw//2, ky, kx + kw//2, ky + kh], fill=(15, 35, 80, 255))

    # ── Blue glow scan lines ──────────────────────────────────────────────────
    if size >= 32:
        lw = max(1, s // 56)
        for oy in [-7, 0, 7]:
            lx, ly = p(20, 62 + oy)
            d.line([(lx, ly), (lx + s*7//128, ly)], fill=(100, 180, 255, 160), width=lw)
            rx, ry = p(101, 62 + oy)
            d.line([(rx, ry), (rx - s*7//128, ry)], fill=(100, 180, 255, 160), width=lw)

    return img

for size in [16, 32, 48, 128]:
    icon = draw_icon(size)
    icon.save(OUT / f"icon{size}.png")
    print(f"OK icon{size}.png")

print("Done.")
