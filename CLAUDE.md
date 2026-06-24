# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A collection of standalone Manim Community **v0.20.1** animation scripts for math-explainer videos (many formatted as portrait Instagram Reels). There is no package structure, build system, test suite, or linter — each `.py` file is an independent script containing one Scene class, run directly with the `manim` CLI.

## Environment & rendering

`manim` is **not** on the default PATH, and LaTeX (required for `Tex`/`MathTex`) lives in a separate MacTeX dir. Every render must activate the conda env and prepend MacTeX to PATH:

```bash
export PATH="/Library/TeX/texbin:$PATH"
source /opt/anaconda3/etc/profile.d/conda.sh && conda activate manim_proj

# Fast low-quality preview (renders and opens the video)
manim -pql <file>.py <SceneName>

# High-quality final render
manim -qh <file>.py <SceneName>
```

- The Scene class name usually differs from the file name — check the `class X(Scene)` / `class X(ThreeDScene)` definition before rendering (e.g. `svm_kernel_reel.py` → `SVMKernelReel`).
- Reel scripts set portrait resolution via module-level `config` (see below), which **overrides the `-ql`/`-qh` quality flag's resolution** — output always lands in `media/videos/<file>/1920p30/<SceneName>.mp4`, never the usual `480p15`.
- 3D scenes with surfaces take a few minutes even at `-ql`; run renders in the background.
- Verify a render without watching it: extract frames with `ffmpeg` (also in the env) and inspect the PNGs, e.g. `ffmpeg -y -ss 14 -i <out>.mp4 -frames:v 1 /tmp/f.png`. Use `ffprobe -show_entries format=duration` to confirm the clip length.

## Script conventions

- Every script does `from manim import *` plus `import numpy as np`, defines one Scene subclass, and builds everything in `construct()`.
- Reel-format scripts set portrait resolution via module-level `config` assignments at the top of the file (before the class definition):
  ```python
  config.pixel_width = 1080
  config.pixel_height = 1920
  config.frame_width = 9.0      # frame coords run x∈[-4.5,4.5], y∈[-8,8]
  config.frame_height = 16.0
  config.background_color = "#000000"
  config.disable_caching = True
  ```
  Scripts without this block render in the default 16:9 landscape.
- `config.disable_caching = True` is set on newer reels deliberately: Manim caches each animation as a partial-movie file and re-splices matching segments on later renders, so an old buggy segment can reappear in a fresh render after you've fixed the code. Leave it on while iterating.
- Color palettes are hex-string class attributes (`COL_*`), with a 3Blue1Brown-style dark/black background.

## Reel layout architecture

The reel scripts (`gradient_ripple_reel`, `linear_regression_reel`, `svm_kernel_reel`, `blockchain_code_reel`) share a three-band vertical structure built in numbered `SECTION` blocks within `construct()`:

- **Top band** — CM-serif `Tex` title + subtitle, sometimes a model/loss equation.
- **Middle band** — the visual (2D plot, or a 3D surface/scatter in a `ThreeDScene`).
- **Bottom band** — a boxed equation (`SurroundingRectangle` over a `MathTex`, often a gradient-descent update rule with an explicit `∂L/∂w, ∂L/∂b` column vector) plus a live HUD.

For `ThreeDScene` reels, the top/bottom 2D bands are pinned with `self.add_fixed_in_frame_mobjects(...)` so they don't rotate with the camera — forgetting this makes equation boxes tilt in 3D. The 3D content is centered in the middle band via `frame_center=...` in `set_camera_orientation`/`move_camera` (a `mobject.shift` would move the surface off the camera's rotation axis and make it drift while orbiting).

Live numeric HUDs (step counter, loss value) use `Integer`/`DecimalNumber`; update them with `ChangeDecimalToValue` inside a `play`, or `.set_value()` followed by **`self.camera.add_fixed_in_frame_mobjects(...)`** to re-pin them each step (the scene-level `self.add_fixed_in_frame_mobjects` also re-`add`s them top-level, drawing them doubled).

## Gotchas

- Headings use plain `Tex` (Computer Modern serif), not `Text`/Pango and not `\textbf` — this is the intended "3Blue1Brown font" look.
- `LaggedStartMap(GrowArrow, vgroup)` crashes: it unpacks each submobject into positional args, feeding the arrow tip in as `point_color`. Use explicit `LaggedStart(GrowArrow(a), GrowArrow(b))` instead.
- `DashedLine` errors on zero length — guard residual/connector lines whose endpoints can coincide.
- `.env` exists locally and is gitignored — do not commit it or reference its contents in code.
