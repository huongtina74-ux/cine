"""Make all image assets for scene 03 into WORKDIR/proj: skins, faceless skins, face parts (scene 02 kit + new states), fx."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fx  # noqa: E402

work = sys.argv[1]
subprocess.run([sys.executable, os.path.join(HERE, '..', 'binbo_thu02', 'prep.py'), work], check=True, stdout=subprocess.DEVNULL)
fx.main(os.path.join(work, 'proj', 'fx'))
print('PREP_OK')
