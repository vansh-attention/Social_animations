# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A collection of standalone Manim Community v0.19.0 animation scripts for math-explainer videos (many formatted as Instagram Reels). There is no package structure, build system, test suite, or linter — each `.py` file is an independent script containing one Scene class, run directly with the `manim` CLI.

## Commands

```bash
# Fast low-quality preview (renders and opens the video)
manim -pql <file>.py <SceneName>

# High-quality final render
manim -qh <file>.py <SceneName>

# Example
manim -pql power_curves.py PowerCurves
```

The scene class name usually differs from the file name — check the `class X(Scene)` / `class X(ThreeDScene)` definition in the file before rendering. Rendered output goes to `media/` (videos, images, Tex caches), which is not committed.

## Conventions

- Every script does `from manim import *` plus `import numpy as np`, defines one Scene subclass, and builds everything in `construct()`.
- Reel-format scripts set portrait resolution via module-level `config` assignments at the top of the file (before the class definition):
  ```python
  config.pixel_width = 1080
  config.pixel_height = 1920
  config.frame_width = 9.0
  config.frame_height = 16.0
  ```
  This applies to any scene rendered from that file. Scripts without this block render in the default 16:9 landscape.
- Color palettes are defined as hex-string constants at the top of `construct()` or as class attributes, with a 3Blue1Brown-style dark background.
- 3D scenes (gradient descent, Lorenz attractor) subclass `ThreeDScene`.
- `.env` exists locally and is gitignored — do not commit it or reference its contents in code.
