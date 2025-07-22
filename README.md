# PartPacker
## All credits go to the original developers🤗

This repo is packaged into 2d1ff1cult/JPL-Su2025-2d3dgen, so nothing else is required here.

# Some notes:
1. app.py has been modified from the original repo to allow for output of multiple .ply files of each segmented mesh part, as opposed to a monolithic .glb
2. Added `block.launch(share=True)`. Allows for sharing of a link to another person with inference performed on your local machine
   - This is supposed to be done in the script `bootstrap.bat` in 2d1ff1cult/JPL-Su2025-2d3dgen, but has been removed since `app.py` here has already been modified

```
@article{tang2024partpacker,
  title={Efficient Part-level 3D Object Generation via Dual Volume Packing},
  author={Tang, Jiaxiang and Lu, Ruijie and Li, Zhaoshuo and Hao, Zekun and Li, Xuan and Wei, Fangyin and Song, Shuran and Zeng, Gang and Liu, Ming-Yu and Lin, Tsung-Yi},
  journal={arXiv preprint arXiv:2506.09980},
  year={2025}
}
```
