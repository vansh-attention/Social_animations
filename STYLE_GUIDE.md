# Reel Design Style Guide

The visual language for the math/AI explainer reels in this repo. Derived from
(a) frame-by-frame study of 3Blue1Brown's "Attention in transformers" video
(July 2026) and (b) conventions already established across the reels here
(`gradient_ripple_reel`, `linear_regression_reel`, `svm_kernel_reel`,
`kmeans_clustering_reel`, `neural_network_reel`, `monte_carlo_reel`,
`monte_carlo_trading_reel`, `attention_qkv_reel`). New reels should follow
this document.

## Core principles (the 3B1B doctrine)

1. **Color is semantic, and strict.** One concept = one color, everywhere it
   appears, for the whole video. Never reuse a concept color for decoration.
   In the attention video: Queries/W_Q = yellow, Keys/W_K = teal-green,
   Values/W_V = red-orange, updated embeddings E' = green; inside matrices,
   positive entries are blue and negative entries red — with zero exceptions.
2. **Focus by dimming.** To spotlight something, drop everything else to
   ~20% opacity grey and put a thin box around the subject. No zooms, no
   glows. The world fades; the subject stays.
3. **Real numbers, always.** Precompute the actual math (softmax weights,
   losses, estimates) with seeded numpy and display those values. Pre-screen
   seeds so the story lands (convergence, clean clusters, near-π estimates).
   Never fake a number that could be computed.
4. **Meaning is geometry.** Abstract quantities become arrows on faint
   wireframe grids. Change of meaning = visible displacement of an arrow.
   Mappings between spaces = two side-by-side panels with a labeled arrow.
5. **One idea moves at a time.** Grids fill in cell-by-cell, bars rise in a
   lagged cascade, equations Write on after their concept exists on screen.

## Palette

- Background: pure black `#000000` (math scenes). 3B1B uses a lighter grey
  only for pi-creature interludes — reels have no interludes, so always black.
- Panel/equation-box fill: `#10102A` at ~0.78 opacity, corner_radius 0.15,
  stroke 1.5 in the reel's accent color.
- Success/convergence: `#00FF88`. The subject eases into green and gets a
  **quiet** emphasis — a gentle `Indicate` pulse, a brief stroke swell
  (`there_and_back`), or a `Circumscribe` box — then rests with a plain label.
  **Never** manim's `Flash` (a sparkle/firework burst — 3B1B never uses it) and
  **never** emoji checkmarks/✓ or other emoji. Keep emphasis subtle: dimming,
  a color shift, a small pulse. That restraint *is* the 3B1B look.
- Per-reel gradient headings (two-color `set_color_by_gradient`), one unique
  pair per reel so the series thumbnails don't repeat. Used so far:
  linear `#FFE259→#FFA751`, logistic `#F472B6→#A78BFA`, kmeans
  `#2DD4BF→#A3E635`, NN `#22D3EE→#A78BFA`, SVM `#5EEAD4→#818CF8`,
  MC-π `#FCD34D→#F87171`, MC-trading `#34D399→#22D3EE`,
  attention `#E879F9→#22D3EE`.
- Q/K/V convention (any transformer/attention content): Q = yellow
  `#FBBF24`-ish, K = teal `#34D399`/`#5EEAD4`, V = red-orange `#FB6B6B`/
  `#FB923C`, updated embedding = `#00FF88`.
- Matrix/vector numerals: positive blue `#60A5FA`, negative red `#FF6B6B`.

## Typography

- Headings, labels, captions: LaTeX Computer Modern via `Tex` — plain, never
  `\textbf` for the big title, italics (`\textit`) for subtitles/captions.
  No underline/divider below headings.
- Math: `MathTex`, coloring semantic sub-parts via indexed submobjects.
- Code (code reels only): `Code` with Menlo + `github-dark` on a `#0D1117`
  window.
- Tokens/words: thin sharp white-outline rectangles with minimal padding
  (3B1B style) — prefer over chunky rounded pills for new reels.
- Vectors: bracketed columns of real numbers with `\vdots`, dimension labeled
  with a brace. Show "a thing becomes numbers" at least once when relevant.

## Portrait reel layout (1080×1920, frame 9×16)

Three bands, y ∈ [-8, 8]:

- **Title band** (y ≈ 7.0 … 4.8): gradient title (`to_edge(UP, buff≈0.6)`),
  italic subtitle, then the governing equation(s), font_size 30–42.
- **Visual band** (y ≈ 4.5 … -3.0): the animation. 2D axes/planes centered
  around y ≈ 0–0.7, or a 3D scene positioned via `frame_center` (never by
  shifting mobjects — that breaks orbit centering).
- **Caption line** (y ≈ -3.1 … -3.6): one-sentence morphing caption,
  font_size ~31, width-guarded to ≤ 8.3.
- **Equation box** (y ≈ -4.7 … -5.0): `SurroundingRectangle` panel with the
  update/estimator rule; grey note line below (buff 0.28).
- **HUD** (y ≈ -6.6): `Integer`/`DecimalNumber` counters at x ≈ ±1.6,
  font_size 32, GREY_A.
- **Done label** (y ≈ -7.4): green closing line.

## Motion grammar

- Intro: title `FadeIn(shift=DOWN*0.3)` 1.2–1.3 s, subtitle 0.8–0.9 s,
  equation `Write` 1.2–1.4 s, `wait(0.3)`.
- Reveals: `LaggedStart` of per-element `FadeIn(scale≈0.4)`; lag_ratio small
  enough to finish in ~1.5 s.
- Iterative algorithms: discrete steps at 0.35–0.6 s each with HUD counters
  animating via `ChangeDecimalToValue`.
- 3D: start near-flat (phi ≈ 14°) and swoop to phi ≈ 62° with
  `move_camera(added_anims=[...])` as the 3D object builds; one slow
  `begin_ambient_camera_rotation(rate≈0.09–0.10)` showcase; content morphs
  mid-orbit (Transform) for the "same thing, new view" beat.
- Ending: subject eases to `#00FF88` with a subtle pulse (see above — no
  `Flash`), the closing line (plain `Tex`, no emoji) fades up, ~2.2 s hold,
  everything `FadeOut(shift=DOWN*0.3)` (3D: `shift=IN*0.4`).

## Attention-pattern specifics

- 3B1B canonical form: grid where **dot radius encodes weight**, filling in
  incrementally, occasional numeric values. Reel-native alternative
  (established in `attention_qkv_reel`): 3D bar city with token-colored axis
  strips. Either is acceptable; bar city for 3D wow, dot grid for fidelity.
- Weighted links between tokens: `ArcBetweenPoints` below the token row,
  stroke width `1.5 + ~12·weight`, opacity scaled by weight. NEVER
  `set_opacity` on arcs (turns on white fill) — `set_stroke(opacity=...)`.

## Verified from the 3b1b source (`~/Documents/manim/3b1b-videos`)

Shallow clone of github.com/3b1b/videos; the attention video's code is
`_2024/transformers/attention.py` (~4,100 lines, manimgl). Confirmed
constants and mechanics:

- Colors in code: queries/W_Q = `YELLOW`, keys/W_K = `TEAL`, updated
  embedding symbols = `TEAL`, value-related rects = `ORANGE`, focus boxes =
  3-width strokes in the concept color.
- Attention-pattern dots: `Dot(radius=0.3 * weight**0.75)` — the **0.75
  exponent** keeps small weights visible; fill `GREY_C` at 0.8 opacity;
  negative pre-softmax values tinted toward `RED_E`.
- Dimming: literal `set_color(GREY_...)` / low-opacity strokes on everything
  out of focus (`stroke opacity = random()**0.25`-style variation for organic
  connection webs).
- Scene granularity: one `InteractiveScene` class per video segment
  (`AttentionPatterns`, `QueryMap`, `KeyMap`, `IntroduceValueMatrix`,
  `MultiHeadedAttention`, …) — mirrors how reels should stay one-file,
  one-scene.

## Manim CE gotchas (hard-won)

- `ThreeDScene` 2D bands: pin with `add_fixed_in_frame_mobjects`. Counters
  that change re-generate digits and lose the pin — re-pin with
  `self.camera.add_fixed_in_frame_mobjects(num)` (camera method, or they
  double-draw).
- `add_fixed_in_frame_mobjects(a, b, c)` makes ALL of them visible at full
  opacity the instant it is called. If you then animate them in one at a time
  (title, then subtitle, then equation), the not-yet-animated ones show early
  — the title appears to arrive last. Fix: register each mobject right before
  its own `FadeIn`/`Write`, OR add them all then `set_opacity(0)` before the
  first play (the pattern used for morphing captions).
- `LaggedStartMap` unpacks submobjects into positional args — use explicit
  `LaggedStart(Anim(a), Anim(b), ...)`.
- Guard `DashedLine` against zero length; width-guard every caption/heading.
- `config.disable_caching = True` in every reel.
- 3B1B's own code (github.com/3b1b/videos) is **manimgl**, not CE — port
  ideas, not code.
