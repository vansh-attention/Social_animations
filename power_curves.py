"""
Graphs of y = x^(1/n) and y = x^n  (n = 1, 2, 3, …, 20)
Beautiful Manim animation with sequential curve drawing,
color gradients, glowing (1,1) dot, and an interactive n-counter.
"""

from prompt_toolkit.key_binding.bindings.mouse import MIDDLE
from manim import MathTex
from manim import *
import numpy as np


# ── 1080 × 1920 portrait config for Instagram Reels ──────
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0


class PowerCurves(Scene):
    def construct(self):
        # ── colours ──────────────────────────────────────────────
        BG = "#0a0a0a"
        AXIS_COLOR = WHITE
        GRID_COLOR = GREY_D
        DOT_COLOR = YELLOW
        DASH_COLOR = "#45b7d1"  # cyan-ish
        UPPER_START = "#ff6b6b"  # warm red  → for x^(1/n) family
        UPPER_END = "#ffd93d"  # gold
        LOWER_START = "#6bcb77"  # green     → for x^n   family
        LOWER_END = "#4d96ff"  # blue

        self.camera.background_color = BG
        N_MAX = 20

        # ── axes (0-1 range, nice ticks) ─────────────────────────
        axes = Axes(
            x_range=[0, 1.05, 0.1],
            y_range=[0, 1.05, 0.1],
            x_length=7.5,
            y_length=7.5,
            axis_config={
                "color": AXIS_COLOR,
                "include_numbers": False,
                "tick_size": 0.05,
                "stroke_width": 2,
                "font_size": 24,
            },
            tips=True,
        )
        axes.move_to(ORIGIN)

        # manually add tick labels
        x_nums = np.arange(0.1, 1.01, 0.1)
        y_nums = np.arange(0.1, 1.01, 0.1)
        x_labels = axes.x_axis.add_numbers(
            x_nums, font_size=24, num_decimal_places=2
        )
        y_labels = axes.y_axis.add_numbers(
            y_nums, font_size=24, num_decimal_places=2
        )

        # axis labels
        x_label = axes.get_x_axis_label(
            MathTex("x", font_size=36, color=AXIS_COLOR),
            direction=RIGHT,
        )
        y_label = axes.get_y_axis_label(
            MathTex("y", font_size=36, color=AXIS_COLOR),
            direction=UP,
        )

        # ── title ────────────────────────────────────────────────

        title2 = MathTex(
            r"\text{Power Curves}",
            font_size=50,
            color="#FFFFFF",
        )
 
        title2.to_edge(UP, buff=1.5)
 
        title = MathTex(
            r"\text{Graphs of } y = x^{\frac{1}{n}}"
            r"\text{ and } y = x^{n}"
            r"\;(n = 1,2,3,\ldots,20)",
            font_size=30,
            color=WHITE,
        )
        title.shift(RIGHT*0.3)
        title.next_to(axes, UP, buff=0.8)

        # ── (1,1) reference geometry ────────────────────────────
        pt_11 = axes.c2p(1, 1)
        dot_11 = Dot(pt_11, radius=0.08, color=DOT_COLOR, z_index=10)
        dot_glow = Dot(pt_11, radius=0.18, color=DOT_COLOR, fill_opacity=0.25, z_index=9)
        label_11 = MathTex("(1,1)", font_size=28, color=DOT_COLOR).next_to(
            dot_11, UR, buff=0.12
        )

        dash_h = DashedLine(
            axes.c2p(0, 1), pt_11,
            color=DASH_COLOR, stroke_width=1.5, dash_length=0.08,
        )
        dash_v = DashedLine(
            pt_11, axes.c2p(1, 0),
            color=DASH_COLOR, stroke_width=1.5, dash_length=0.08,
        )

        # ── helper: colour interpolation ────────────────────────
        def lerp_color(c1, c2, t):
            return interpolate_color(ManimColor(c1), ManimColor(c2), t)

        # ── build curve mobjects ─────────────────────────────────
        upper_curves = []  # x^(1/n)  — above diagonal
        lower_curves = []  # x^n     — below diagonal

        for i in range(1, N_MAX + 1):
            t = (i - 1) / max(N_MAX - 1, 1)
            # upper: x^(1/n)
            upper_c = axes.plot(
                lambda x, n=i: x ** (1 / n),
                x_range=[0, 1, 0.005],
                color=lerp_color(UPPER_START, UPPER_END, t),
                stroke_width=2.2 - 0.06 * i,
            )
            upper_curves.append(upper_c)

            # lower: x^n
            lower_c = axes.plot(
                lambda x, n=i: x ** n,
                x_range=[0, 1, 0.005],
                color=lerp_color(LOWER_START, LOWER_END, t),
                stroke_width=2.2 - 0.06 * i,
            )
            lower_curves.append(lower_c)

        # ── n-counter (dynamic label in bottom-right) ───────────
        n_tracker = ValueTracker(1)

        n_label = always_redraw(
            lambda: MathTex(
                f"n = {int(n_tracker.get_value())}",
                font_size=48,
                color=WHITE,
            ).next_to(axes, DOWN, buff=0.8)
        )

        # ── ANIMATION SEQUENCE ──────────────────────────────────
        # 1. Fade in axes, labels, title
        self.play(
            Create(axes, run_time=1.5),
            FadeIn(x_label),
            FadeIn(y_label),
            Write(title, run_time=1.5),
            Write(title2, run_time=1.5),
        )
        self.wait(0.3)

        # 2. Draw y=x (n=1 case — same for both families)
        self.play(
            Create(upper_curves[0], run_time=1.0),
            Create(lower_curves[0], run_time=1.0),
            FadeIn(n_label),
        )
        self.wait(0.4)

        # 3. Sequentially draw each pair of curves n = 2 … 20
        for i in range(1, N_MAX):
            speed = max(0.25, 0.7 - i * 0.025)  # accelerate gently
            self.play(
                Create(upper_curves[i], run_time=speed),
                Create(lower_curves[i], run_time=speed),
                n_tracker.animate.set_value(i + 1),
                rate_func=smooth,
            )

        self.wait(0.3)

        # 4. Flash the (1,1) convergence point + dashed guides
        self.play(
            Create(dash_h, run_time=0.6),
            Create(dash_v, run_time=0.6),
        )
        self.play(
            GrowFromCenter(dot_11),
            FadeIn(dot_glow, scale=2),
            Write(label_11),
            run_time=0.8,
        )

        # gentle pulse on the dot
        self.play(
            dot_glow.animate.scale(1.5).set_opacity(0.10),
            rate_func=there_and_back,
            run_time=1.0,
        )
        self.wait(0.5)

        # 5. Highlight symmetry: flash diagonal y=x
        diag = axes.plot(
            lambda x: x,
            x_range=[0, 1, 0.01],
            color=WHITE,
            stroke_width=3,
        )
        diag_label = MathTex("y = x", font_size=30, color=WHITE).move_to(
            axes.c2p(0.55, 0.62),
        )
        self.play(
            Create(diag, run_time=0.8),
            FadeIn(diag_label),
        )
        self.wait(0.3)

        # flash to show mirror symmetry
        self.play(
            diag.animate.set_color(YELLOW).set_stroke(width=4),
            rate_func=there_and_back,
            run_time=1.0,
        )
        self.wait(0.5)

        # 6. Add annotation: shaded region label
        upper_label = MathTex(
            r"y = x^{\frac{1}{n}}", font_size=32, color=ManimColor(UPPER_END),
        ).move_to(axes.c2p(0.10, 0.96))
        lower_label = MathTex(
            r"y = x^{n}", font_size=32, color=ManimColor(LOWER_END),
        ).move_to(axes.c2p(0.925, 0.035))

        self.play(Write(upper_label), Write(lower_label), run_time=0.8)
        self.wait(1.5)

        # 7. Grand finale: quick wave / color sweep across all curves
        all_curves = upper_curves + lower_curves
        self.play(
            *[
                c.animate.set_stroke(opacity=0.3)
                for c in all_curves
            ],
            run_time=0.6,
        )
        self.play(
            *[
                c.animate.set_stroke(opacity=1.0)
                for c in all_curves
            ],
            run_time=0.8,
            rate_func=smooth,
        )
        self.wait(2)
