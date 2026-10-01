# Azurite Avalanche

Full-colour Python 3 neon crystal-bank arcade for [ElbowOS](https://x.com/ElbowOS).

Falling azure, gold, coral, and mint gems tumble down a cobalt shaft. Sweep a copper plow under each gem and flip the ramp so it banks into the matching side vault. Miss the plow and the shard cracks.

Left / Right (or A / D) sweep the plow. Space / W / Up flips the ramp. R restarts.

## Play

```bash
pip install -r requirements.txt
python3 azurite_avalanche.py --play
```

## Record a 9:16 reel

```bash
python3 azurite_avalanche.py --record
```

Writes a 1080x1920 h264 clip (15s @ 30fps) with title, score, and `x.com/ElbowOS` burned into the frames. Headless runs use `SDL_VIDEODRIVER=dummy`.

- Featured account: https://x.com/ElbowOS
- Drive reel: https://drive.google.com/file/d/1FMNVFH56xVIkm_GJNaYXbAdXCr7NOOds/view

Original arcade. Not a ROM, not an emulator, no trademarked characters.
