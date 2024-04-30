# PandaFlowGen

This code uses the Panda3D game engine in order to create synthetic optical flow from moving 3D objects

https://github.com/jamt9000/pandaflowgen/assets/1186841/ec0e5e4e-6b10-4e32-a622-7014af34cd57

## Instructions

```bash
pip install panda3d scikit-image
python panda.py

# You can visualise the saved optical flow maps with ffmpeg's ffplay
ffplay -framerate 24 -i "out/%05d_flow_vis.png"
```
