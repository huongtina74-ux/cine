"""Assets for the Mine-imator version of MC-S1 Short #01: scene-03 kit (skins, faces, fx) + glow eyes for Zu + ruler numbers.

    python prep.py WORKDIR      # -> WORKDIR/proj/{skins,face,fx}
All drawn in code (original): no downloaded skins, no third-party textures.
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
work = sys.argv[1]
subprocess.run([sys.executable, os.path.join(HERE, '..', 'binbo_thu03', 'prep.py'), work], check=True, stdout=subprocess.DEVNULL)
face, fx = os.path.join(work, 'proj', 'face'), os.path.join(work, 'proj', 'fx')

# Zu's "secret power" eyes: bright yellow cores with a lime rim, on the same 32x32 face grid as faces.py (EYE_R / EYE_L boxes)
im = Image.new('RGBA', (32, 32), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
for x0, y0, x1, y1 in ((3, 12, 11, 21), (21, 12, 29, 21)):
    d.rectangle((x0 - 1, y0 - 1, x1, y1), fill=(20, 24, 20, 255))
    d.rectangle((x0, y0, x1 - 1, y1 - 1), fill=(120, 255, 60, 255))
    d.rectangle((x0 + 2, y0 + 2, x1 - 3, y1 - 3), fill=(255, 250, 140, 255))
im.save(os.path.join(face, 'zu_eyes_glow.png'))

# ruler numbers (white digits, black outline) for the height tower
try:
    font = ImageFont.truetype('DejaVuSans-Bold.ttf', 74)
except OSError:
    font = ImageFont.load_default()
for n in range(4, 29, 4):
    im = Image.new('RGBA', (128, 128), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((64, 66), str(n), font=font, anchor='mm', fill=(255, 225, 77, 255), stroke_width=9, stroke_fill=(0, 0, 0, 255))
    im.save(os.path.join(fx, f'fx_num{n}.png'))
print('PREP_S01_OK')
