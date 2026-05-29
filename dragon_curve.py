"""
Dragon Curve - Manim Animation  (Portrait 1080 × 1920)
──────────────────────────────────────────────────────
Render commands
  Preview  : manim -pql dragon_curve.py DragonCurveScene
  Full HD  : manim -pqh dragon_curve.py DragonCurveScene
  4K/1080p : manim -pqk dragon_curve.py DragonCurveScene

The resolution flag sets pixel dimensions; the frame_width / frame_height
below set the coordinate-space aspect ratio to match 9 : 16 portrait.
"""

# ── Portrait frame ──────────────────────────────────────────────────────────
from manim import config
config.pixel_width   = 1080
config.pixel_height  = 1920
config.frame_width   = 9        # coordinate units wide
config.frame_height  = 16       # coordinate units tall  (9 : 16)
# ───────────────────────────────────────────────────────────────────────────

from manim import *
import numpy as np


# ╔══════════════════════════════════════════════════════╗
#  Dragon-curve math helpers
# ╚══════════════════════════════════════════════════════╝

def generate_turn_sequence(iterations: int) -> list:
    """
    Dragon-curve turn sequence.
    1 = turn left,  0 = turn right.
    """
    seq = [1]
    for _ in range(iterations - 1):
        seq = seq + [1] + [1 - x for x in reversed(seq)]
    return seq


def turns_to_points(turns: list, step: float = 0.25) -> list:
    """Turn sequence → list of numpy 3-D points (z = 0)."""
    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]   # E  N  W  S
    d, x, y = 0, 0.0, 0.0
    pts = [np.array([x, y, 0.0])]
    for t in turns:
        d = (d + (1 if t == 1 else -1)) % 4
        dx, dy = dirs[d]
        x += dx * step
        y += dy * step
        pts.append(np.array([x, y, 0.0]))
    return pts


def center_and_fit(pts: list, target_size: float = 4.5) -> list:
    """Centre + uniformly scale so the longest axis = target_size."""
    arr = np.array(pts)
    cx  = arr[:, 0].mean()
    cy  = arr[:, 1].mean()
    span = max(
        arr[:, 0].max() - arr[:, 0].min(),
        arr[:, 1].max() - arr[:, 1].min(),
    )
    s = target_size / span if span else 1.0
    return [np.array([(p[0] - cx) * s, (p[1] - cy) * s, 0.0]) for p in pts]


# ╔══════════════════════════════════════════════════════╗
#  Scene
# ╚══════════════════════════════════════════════════════╝

class DragonCurveScene(Scene):

    # ── tuneable constants ──────────────────────────────
    ITERATIONS   = 13      # fractal depth  (12 – 14 look great)
    STROKE_W     = 1.3     # line thickness for the curve
    DRAW_TIME    = 9.0     # seconds to sweep the full curve

    # 3Blue1Brown-style: light weight, airy colour (not heavy bold)
    TITLE_COLOR  = ManimColor("#FF6EB4")   # soft magenta-pink
    TITLE_SHADOW = ManimColor("#8B0045")   # deep rose shadow

    # Rainbow palette – same direction as 3b1b vibes
    PALETTE = [
        "#FF3333",   # red
        "#FF7700",   # orange
        "#FFE000",   # yellow
        "#22DD44",   # green
        "#00CCEE",   # cyan
        "#4488FF",   # blue
        "#9933FF",   # violet
        "#FF3399",   # pink
    ]

    # ── Portrait layout (frame_height = 16, y ∈ [-8, +8]) ──
    #   Title centre  : y =  6.8
    #   Formula band  : y =  4.8 … 3.6
    #   Curve centre  : y = -1.2   (well below the formula band)
    TITLE_Y    =  6.80
    FORM1_Y    =  4.80
    FORM2_Y    =  3.55
    CURVE_Y    = -1.20
    CURVE_SIZE =  4.60   # coordinate units; curve fits inside a 4.6 × 4.6 box

    # ── builders ───────────────────────────────────────────

    def _title(self):
        """Lightweight 3b1b-style title – normal weight, elegant serif."""
        shadow = Text(
            "Dragon Curve",
            font       = "Georgia",
            weight     = NORMAL,          # ← not BOLD; lighter feel
            font_size  = 68,
            color      = self.TITLE_SHADOW,
        ).move_to([0, self.TITLE_Y, 0]).shift(RIGHT * 0.04 + DOWN * 0.04)

        label = Text(
            "Dragon Curve",
            font       = "Georgia",
            weight     = NORMAL,
            font_size  = 68,
            color      = self.TITLE_COLOR,
        ).move_to([0, self.TITLE_Y, 0])

        return shadow, label

    def _formulas(self):
        """IFS equations, positioned just below the title."""
        kw = dict(font_size=40, color=WHITE)

        f1 = MathTex(r"f_1(z) \;=\; \dfrac{(1+i)\,z}{2}", **kw)
        f2 = MathTex(r"f_2(z) \;=\; 1 - \dfrac{(1-i)\,z}{2}", **kw)

        f1.move_to([0, self.FORM1_Y, 0])
        f2.move_to([0, self.FORM2_Y, 0])
        return f1, f2

    def _curve(self) -> VGroup:
        """Build the rainbow dragon-curve VGroup, centred on CURVE_Y."""
        turns  = generate_turn_sequence(self.ITERATIONS)
        raw    = turns_to_points(turns)
        pts    = center_and_fit(raw, target_size=self.CURVE_SIZE)

        n      = len(pts) - 1
        colors = color_gradient(self.PALETTE, n)

        segs = VGroup()
        for i in range(n):
            segs.add(Line(
                pts[i], pts[i + 1],
                stroke_width = self.STROKE_W,
                stroke_color = colors[i],
            ))

        segs.move_to([0, self.CURVE_Y, 0])
        return segs

    # ── main animation sequence ─────────────────────────────

    def construct(self):
        self.camera.background_color = "#070707"

        # ── 1. TITLE ──────────────────────────────────────
        shadow, label = self._title()

        self.play(
            FadeIn(shadow, shift=UP * 0.2, run_time=0.7),
            Write(label, run_time=1.6),
        )
        self.wait(0.35)

        # ── 2. EQUATIONS ──────────────────────────────────
        f1, f2 = self._formulas()

        # Each formula slides up from below and fades in
        for f in (f1, f2):
            f.save_state()
            f.shift(DOWN * 0.7).set_opacity(0)

        self.play(
            f1.animate.restore(),
            run_time=0.90,
            rate_func=smooth,
        )
        self.play(
            f2.animate.restore(),
            run_time=0.90,
            rate_func=smooth,
        )
        self.wait(0.45)

        # ── 3. CURVE ──────────────────────────────────────
        curve = self._curve()

        # Thin divider between formula zone and curve zone (optional aesthetics)
        divider = Line(
            LEFT * 3.5, RIGHT * 3.5,
            stroke_width=0.6,
            stroke_color=ManimColor("#333333"),
        ).move_to([0, (self.FORM2_Y + self.CURVE_SIZE / 2 + self.CURVE_Y) / 2, 0])

        # Position divider between formula bottom and curve top
        divider_y = self.FORM2_Y - 0.55
        divider.move_to([0, divider_y, 0])

        self.play(Create(divider, run_time=0.5))

        # Draw the curve segment by segment
        self.play(
            LaggedStart(
                *[Create(seg, rate_func=linear) for seg in curve],
                lag_ratio = 2.5 / len(curve),
                run_time  = self.DRAW_TIME,
            )
        )
        self.wait(0.5)

        # ── 4. GLOW PULSE ─────────────────────────────────
        glow = curve.copy().set_stroke(width=self.STROKE_W * 4, opacity=0.20)
        self.play(FadeIn(glow,  run_time=0.5))
        self.play(FadeOut(glow, run_time=1.0))

        # ── 5. SLOW ROTATION ──────────────────────────────
        self.play(
            Rotate(
                curve,
                angle       = TAU,
                about_point = curve.get_center(),
                rate_func   = linear,
                run_time    = 20,
            )
        )

        self.wait(1.5)