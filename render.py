#!/usr/bin/env python3
"""Render the news-image-20261119-v2 front page to entry.png (1024x1024).

v2 concept — "THE WORLD TODAY: 11 stories that defined the day".
A magazine-cover layout, deliberately different from v1's newspaper grid:
a dark navy header with the date set huge, one dominant hero panel (the
first-ever Trump-Xi-Putin trilateral in Shenzhen, drawn as three flags over
a summit table), two stacked side cards (Gulf escalation, Crimean Bridge),
a numbered 3-8 rundown with pictogram icons, and a "BY THE NUMBERS" strip
(GTA VI 99, Anthropic $81.3bn, Van Gogh $190.4m, Voyager 1 light-day).

Every story was verified against reporting dated Thursday 19 November 2026
(see SOURCES.md). Two v1 errors are fixed here: the ICJ Myanmar ruling is
shown as delivered today with NO outcome claimed (the verdict was still
being read when this was built), and v1's 18-November stories (EU 45bn loan
proposal, Jeffries nomination) and its unverified cyclone are dropped in
favour of stories first reported on 19 November.

Build-time script only: main.py copies the finished entry.png. Deterministic
(fixed text, fixed geometry, no network, no randomness). Run: python3 render.py
"""
import math
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
NAVY = (15, 30, 51)
NAVY2 = (24, 46, 78)
PAPER = (247, 243, 232)
CARD = (255, 252, 244)
INK = (20, 20, 20)
RED = (176, 30, 30)
GOLD = (212, 164, 60)
GREY = (74, 68, 58)
RULE = (196, 187, 168)
FAINT = (122, 113, 96)

SERIF_B = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
SANS_R = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, max_w, leading, fill=GREY):
    for ln in wrap(draw, text, fnt, max_w):
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def star(cx, cy, r_out, r_in, fill):
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def flag_us(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=INK, width=2)
    for i in range(13):
        c = (178, 34, 52) if i % 2 == 0 else (255, 255, 255)
        d.rectangle([x + 2, y + 2 + i * (h - 4) / 13,
                     x + w - 2, y + 2 + (i + 1) * (h - 4) / 13], fill=c)
    cw, chh = w * 0.4, (h - 4) * 7 / 13
    d.rectangle([x + 2, y + 2, x + 2 + cw, y + 2 + chh], fill=(60, 59, 110))
    for r in range(4):
        for c in range(5):
            px = x + 8 + c * (cw - 12) / 4
            py = y + 8 + r * (chh - 12) / 3
            d.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5], fill=(255, 255, 255))


def flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16), outline=INK, width=2)
    d.polygon(star(x + w * 0.22, y + h * 0.32, 15, 6, (255, 222, 0)), fill=(255, 222, 0))
    for sx, sy in [(0.52, 0.12), (0.66, 0.22), (0.66, 0.42), (0.52, 0.52)]:
        d.polygon(star(x + w * sx, y + h * sy, 5, 2, (255, 222, 0)), fill=(255, 222, 0))


def flag_ru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=INK, width=2)
    for i, c in enumerate([(255, 255, 255), (0, 57, 166), (213, 43, 30)]):
        d.rectangle([x + 2, y + 2 + i * (h - 4) / 3,
                     x + w - 2, y + 2 + (i + 1) * (h - 4) / 3], fill=c)


def icon_burst(d, cx, cy, col):
    """Explosion / missile burst pictogram."""
    r = 11
    d.polygon(star(cx, cy, r, r * 0.45, col), fill=col)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=PAPER)


def icon_bridge(d, cx, cy, col):
    d.arc([cx - 16, cy - 14, cx + 16, cy + 14], 180, 360, fill=col, width=4)
    d.line([(cx - 16, cy + 2), (cx + 16, cy + 2)], fill=col, width=3)
    d.line([(cx - 16, cy + 2), (cx - 16, cy + 12)], fill=col, width=3)
    d.line([(cx + 16, cy + 2), (cx + 16, cy + 12)], fill=col, width=3)
    d.line([(cx, cy - 14), (cx, cy + 2)], fill=col, width=3)


def icon_gavel(d, cx, cy, col):
    d.rectangle([cx - 14, cy - 10, cx + 6, cy - 2], fill=col)
    d.line([(cx - 2, cy - 6), (cx + 12, cy + 10)], fill=col, width=4)
    d.line([(cx - 12, cy + 12), (cx + 12, cy + 12)], fill=col, width=4)


def icon_pad(d, cx, cy, col):
    d.rounded_rectangle([cx - 16, cy - 9, cx + 16, cy + 9], radius=8, fill=col)
    d.line([(cx - 10, cy), (cx - 4, cy)], fill=PAPER, width=3)
    d.line([(cx - 7, cy - 3), (cx - 7, cy + 3)], fill=PAPER, width=3)
    d.ellipse([cx + 5, cy - 4, cx + 9, cy], fill=PAPER)
    d.ellipse([cx + 10, cy + 1, cx + 14, cy + 5], fill=PAPER)


def icon_chart(d, cx, cy, col):
    for i, h in enumerate([8, 14, 20]):
        x0 = cx - 14 + i * 11
        d.rectangle([x0, cy + 10 - h, x0 + 7, cy + 10], fill=col)
    d.line([(cx - 16, cy + 10), (cx + 16, cy + 10)], fill=col, width=3)


def icon_tank(d, cx, cy, col):
    d.rectangle([cx - 15, cy - 4, cx + 8, cy + 6], fill=col)
    d.line([(cx + 8, cy - 2), (cx + 17, cy - 2)], fill=col, width=3)
    for wx in (-10, 0):
        d.ellipse([cx + wx - 4, cy + 6, cx + wx + 4, cy + 14], outline=col, width=2)


def icon_megaphone(d, cx, cy, col):
    d.polygon([(cx - 14, cy - 4), (cx + 2, cy - 10), (cx + 2, cy + 10),
               (cx - 14, cy + 4)], fill=col)
    d.rectangle([cx + 2, cy - 10, cx + 8, cy + 10], fill=col)
    d.line([(cx - 14, cy - 4), (cx - 14, cy + 10)], fill=col, width=3)
    d.arc([cx + 8, cy - 6, cx + 18, cy + 6], -60, 60, fill=col, width=2)


def icon_atom(d, cx, cy, col):
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=col)
    for ang in (0, 60, 120):
        d.arc([cx - 15, cy - 8, cx + 15, cy + 8], 0, 360, fill=col, width=2)
        # rotate by drawing ellipse via polygon approximation
        pts = []
        for t in range(0, 360, 10):
            a = math.radians(t)
            ex, ey = 15 * math.cos(a), 8 * math.sin(a)
            ra = math.radians(ang)
            pts.append((cx + ex * math.cos(ra) - ey * math.sin(ra),
                        cy + ex * math.sin(ra) + ey * math.cos(ra)))
        d.line(pts + [pts[0]], fill=col, width=2)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 28
    right = W - mx

    # --- Header: dark navy band ----------------------------------------
    d.rectangle([0, 0, W, 118], fill=NAVY)
    d.rectangle([0, 118, W, 122], fill=GOLD)
    d.text((W // 2, 14), "THE WORLD TODAY", font=font(SERIF_B, 52),
           fill=(255, 255, 255), anchor="ma")
    d.text((W // 2, 76), "THURSDAY  ·  19 NOVEMBER 2026  ·  11 STORIES THAT DEFINED THE DAY",
           font=font(SANS_B, 16), fill=GOLD, anchor="ma")

    # --- Hero panel: Shenzhen summit ------------------------------------
    hx, hy, hw, hh = mx, 138, 606, 330
    d.rectangle([hx, hy, hx + hw, hy + hh], fill=CARD, outline=INK, width=2)
    d.rectangle([hx, hy, hx + hw, hy + 30], fill=RED)
    d.text((hx + 14, hy + 5), "1  ·  THE SUMMIT  —  SHENZHEN, CHINA",
           font=font(SANS_B, 14), fill=(255, 255, 255))
    # three flags over a summit table
    fw, fh = 150, 96
    fx0 = hx + 28
    fy = hy + 48
    for i, (fn, lbl) in enumerate([(flag_us, "TRUMP · USA"),
                                   (flag_cn, "XI · CHINA"),
                                   (flag_ru, "PUTIN · RUSSIA")]):
        x0 = fx0 + i * (fw + 26)
        fn(d, x0, fy, fw, fh)
        d.rectangle([x0, fy + fh + 6, x0 + fw, fy + fh + 28], fill=NAVY)
        d.text((x0 + fw / 2, fy + fh + 10), lbl, font=font(SANS_B, 11),
               fill=(255, 255, 255), anchor="ma")
    # agenda line at the foot of the hero panel
    d.line([(hx + 16, hy + 306), (hx + hw - 16, hy + 306)], fill=RULE, width=1)
    d.text((hx + hw // 2, hy + 312), "First-ever trilateral: Ukraine · Iran · Trade",
           font=font(SANS_B, 13), fill=RED, anchor="ma")
    y = para(d, hx + 16, hy + 196, "Three leaders, one table",
             font(SERIF_B, 30), hw - 32, 34, fill=INK)
    para(d, hx + 16, y + 4,
         "Xi Jinping hosts Donald Trump and Vladimir Putin at the APEC summit "
         "in Shenzhen — the first meeting of the three ever. Europe watches "
         "from the sidelines as Kyiv's fate is discussed without it.",
         font(SERIF_R, 16), hw - 32, 21)

    # --- Right column: two stacked cards --------------------------------
    rx, rw = 660, right - 660
    cards = [
        ("2  ·  THE GULF", "Iran hits back at Kuwait and Bahrain",
         "Iran fires drones at US bases in Kuwait and Bahrain after American "
         "jets strike a missile site on Qeshm Island. A tanker is hit in the "
         "Strait of Hormuz; no casualties reported.", icon_burst),
        ("3  ·  UKRAINE", "Crimean Bridge hit for a third time",
         "Ukraine strikes the Crimean Bridge for the third time in a week as "
         "the Shenzhen summit opens. Traffic is halted while damage is "
         "assessed; Kyiv's allies meet in Berlin.", icon_bridge),
    ]
    cy = hy
    chh = 162
    for i, (kick, head, body, ic) in enumerate(cards):
        d.rectangle([rx, cy, rx + rw, cy + chh], fill=CARD, outline=INK, width=2)
        d.rectangle([rx, cy, rx + rw, cy + 28], fill=NAVY)
        d.text((rx + 12, cy + 5), kick, font=font(SANS_B, 13), fill=(255, 255, 255))
        # icon badge
        d.ellipse([rx + rw - 46, cy + 40, rx + rw - 12, cy + 74], fill=RED)
        ic(d, rx + rw - 29, cy + 57, PAPER)
        y = para(d, rx + 12, cy + 36, head, font(SERIF_B, 21), rw - 58, 24, fill=INK)
        para(d, rx + 12, y + 4, body, font(SERIF_R, 14), rw - 24, 18)
        cy += chh + 6

    # --- Numbered rundown 4-9 -------------------------------------------
    d.line([(mx, 486), (right, 486)], fill=INK, width=2)
    d.text((mx, 496), "THE REST OF THE DAY", font=font(SANS_B, 14), fill=RED)
    stories = [
        ("4", "JUSTICE", "World court rules on Myanmar",
         "The ICJ delivers its verdict in The Gambia's genocide case over the "
         "2017 Rohingya crackdown.",
         icon_gavel),
        ("5", "CULTURE", "Vice City opens: GTA VI is out",
         "After 13 years, Grand Theft Auto VI launches worldwide — 17.1m "
         "pre-orders, $79.99, and a 99 on Metacritic.",
         icon_pad),
        ("6", "MARKETS", "Anthropic's record debut",
         "The Claude maker prices its IPO at $83 a share, raising a record "
         "$81.3bn at a ~$1.5tn valuation. Shares start trading today as ANT.",
         icon_chart),
        ("7", "GAZA", "Tanks cross the ceasefire line",
         "Israeli tanks advance beyond the Yellow Line in a rare ground "
         "operation, as four nations demand aid access to flooded Gaza.",
         icon_tank),
        ("8", "EUROPE", "Spain strikes; Estonia shuts a border",
         "A general strike disrupts Spanish ports and factories; Estonia "
         "plans to close its Russian border crossings from December.",
         icon_megaphone),
        ("9", "SECURITY", "North Korea enriches more uranium",
         "The IAEA says Pyongyang has expanded uranium enrichment at "
         "Yongbyon; Trump warns Iran may seek biological weapons.",
         icon_atom),
    ]
    gx, gy = mx, 524
    cw, ch = 482, 92
    for i, (num, kick, head, body, ic) in enumerate(stories):
        cx = gx + (i % 2) * (cw + 4)
        cyy = gy + (i // 2) * (ch + 4)
        d.rectangle([cx, cyy, cx + cw, cyy + ch], fill=CARD, outline=RULE, width=1)
        d.ellipse([cx + 10, cyy + 10, cx + 42, cyy + 42], fill=RED)
        d.text((cx + 26, cyy + 13), num, font=font(SANS_B, 20),
               fill=(255, 255, 255), anchor="ma")
        d.text((cx + 52, cyy + 8), kick, font=font(SANS_B, 12), fill=RED)
        d.text((cx + 52, cyy + 26), head, font=font(SERIF_B, 18), fill=INK)
        para(d, cx + 52, cyy + 50, body, font(SERIF_R, 13), cw - 64, 17)
        ic(d, cx + cw - 24, cyy + 26, RED)

    # --- By the numbers ---------------------------------------------------
    ny = 824
    d.line([(mx, ny), (right, ny)], fill=INK, width=2)
    d.text((mx, ny + 8), "BY THE NUMBERS", font=font(SANS_B, 14), fill=RED)
    stats = [
        ("99", "GTA VI scores 99 on Metacritic at launch"),
        ("$81.3bn", "Anthropic's record IPO, the largest debut ever"),
        ("$190.4m", "Van Gogh record: 'Chestnut Trees in Blossom'"),
        ("1 light-day", "Voyager 1 nears one light-day from Earth"),
    ]
    sw = (right - mx) // 4
    for i, (big, small) in enumerate(stats):
        sx = mx + i * sw
        d.text((sx + 8, ny + 32), big, font=font(SERIF_B, 26), fill=NAVY)
        para(d, sx + 8, ny + 66, small, font(SERIF_R, 13), sw - 20, 17)
        if i < 3:
            d.line([(sx + sw - 4, ny + 34), (sx + sw - 4, ny + 108)], fill=RULE, width=1)

    d.line([(mx, 948), (right, 948)], fill=INK, width=2)
    d.text((W // 2, 958), "SOURCES: LE MONDE · BBC · REUTERS · AP · SOTHEBY'S · NASA — ALL STORIES FIRST REPORTED THURSDAY 19 NOVEMBER 2026",
           font=font(SANS_B, 11), fill=FAINT, anchor="ma")
    d.text((W // 2, 980), "THE WORLD TODAY — ONE DAY, ONE IMAGE",
           font=font(SANS_B, 11), fill=FAINT, anchor="ma")

    img.save("entry.png", format="PNG", optimize=True)
    print("entry.png written")


if __name__ == "__main__":
    main()
