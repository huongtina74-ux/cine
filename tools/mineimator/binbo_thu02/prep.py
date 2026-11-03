"""Make all image assets for scene 02 into WORKDIR/proj: base skins, faceless skins, face-part textures."""
import os, subprocess, sys
import faces
HERE = os.path.dirname(os.path.abspath(__file__))
work = sys.argv[1]
skins, face = os.path.join(work, 'proj', 'skins'), os.path.join(work, 'proj', 'face')
subprocess.run([sys.executable, os.path.join(HERE, 'skins.py'), skins], check=True, stdout=subprocess.DEVNULL)
faces.main(face)
for n, c in faces.CH.items():
    faces.faceless_skin(f'{skins}/{n}_neutral.png', f'{skins}/{n}_faceless.png', c)
print('PREP_OK')
