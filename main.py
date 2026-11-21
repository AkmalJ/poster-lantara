#!/usr/bin/env python3
"""The Poster for a Place That Isn't There: LANTARA.

Lantara is a harbour town that lives inside a colossal brass lantern
afloat on a dusk sea: lit windows, a church spire and festoon lights
behind the glass, rowing boats with lanterns of their own circling it,
and its light laid out on the water in a golden path. The artwork was
painted for this entry (kept beside this file as art.jpg); this program
sets the poster's type and frame the way a poster shop would: the
place's name in big display serif capitals across the night sky, its
descriptor in letterspaced gold small caps above it, and the cream
border every vintage travel poster carries.

The finished poster is written to /output/entry.png (or to
$MAKEFUN_OUTPUT_DIR/entry.png when that variable is set), 1024 by 1024,
inside the one-megabyte gate.
"""

import io
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SIZE = 1024

CREAM = (247, 238, 214)
GOLD = (232, 200, 126)
FRAME = (243, 233, 210)

# The poster typefaces travel with the repository: the grading sandbox
# has no font library of ours to borrow from, so the program loads the
# two Noto Serif faces (SIL Open Font License) from ./fonts and only
# falls back to system paths, then PIL's default, if they are missing.
SERIF_DISPLAY = os.path.join(HERE, "fonts", "NotoSerifDisplay-Bold.ttf")
SERIF = os.path.join(HERE, "fonts", "NotoSerif-SemiBold.ttf")


def load_font(path, size):
    candidates = [
        path,
        "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSerif-SemiBold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    ]
    for cand in candidates:
        try:
            return ImageFont.truetype(cand, size)
        except OSError:
            continue
    return ImageFont.load_default()


def tracked_width(draw, text, font, tracking):
    w = 0
    for ch in text:
        w += draw.textlength(ch, font=font) + tracking
    return w - tracking


def draw_tracked(draw, cx, y, text, font, fill, tracking, shadow=None):
    w = tracked_width(draw, text, font, tracking)
    x = cx - w / 2
    for ch in text:
        if shadow:
            draw.text((x + shadow[0], y + shadow[1]), ch, font=font, fill=shadow[2])
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking
    return w


def main():
    art = Image.open(os.path.join(HERE, "art.jpg")).convert("RGB")
    art = art.resize((SIZE, SIZE), Image.LANCZOS)
    # Set the scene a little lower in the frame: the top band of sky is
    # stretched gently upward so the masthead gets clean night sky and
    # the lantern's finial clears the name. The sea loses a ribbon at
    # the bottom that the eye never misses.
    img = Image.new("RGB", (SIZE, SIZE), (10, 16, 34))
    img.paste(art.crop((0, 0, SIZE, 34)).resize((SIZE, 54)), (0, 0))
    img.paste(art, (0, 54))
    d = ImageDraw.Draw(img, "RGBA")

    # A soft night gradient behind the title so the type sits in the
    # sky the way a poster's masthead does, never fighting the clouds.
    shade = Image.new("L", (1, 210), 0)
    for i in range(210):
        shade.putpixel((0, i), int(118 * (1 - i / 210) ** 1.4))
    shade = shade.resize((SIZE, 210))
    img.paste(Image.new("RGB", (SIZE, 210), (10, 16, 34)), (0, 0), shade)
    d = ImageDraw.Draw(img, "RGBA")

    cx = SIZE // 2
    # Descriptor first (small, gold, widely tracked), then the name.
    small = load_font(SERIF, 26)
    draw_tracked(d, cx, 34, "THE TOWN INSIDE THE LANTERN", small, GOLD, 7,
                 shadow=(0, 2, (8, 12, 26, 160)))
    tw = tracked_width(d, "THE TOWN INSIDE THE LANTERN", small, 7)
    for sx in (-1, 1):
        x0 = cx + sx * (tw / 2 + 22)
        x1 = cx + sx * (tw / 2 + 118)
        d.line([(min(x0, x1), 47), (max(x0, x1), 47)], fill=GOLD + (200,), width=2)

    name_font = load_font(SERIF_DISPLAY, 106)
    draw_tracked(d, cx, 62, "LANTARA", name_font, CREAM, 12,
                 shadow=(0, 3, (8, 12, 26, 170)))

    # The cream poster frame, with a hairline inside it.
    d.rectangle([10, 10, SIZE - 11, SIZE - 11], outline=FRAME, width=22)
    d.rectangle([26, 26, SIZE - 27, SIZE - 27], outline=(20, 26, 44, 120), width=2)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    if buf.tell() > 1_000_000:
        img.save(path, "JPEG", quality=92)
    else:
        with open(path, "wb") as fh:
            fh.write(buf.getvalue())
    print(f"wrote {path} ({os.path.getsize(path)} bytes)")


if __name__ == "__main__":
    main()
