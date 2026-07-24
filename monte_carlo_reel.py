"""
Monte Carlo simulation — estimating π with random points.
Random points rain into a square with an inscribed circle; the fraction
landing inside the circle estimates π/4, and the running estimate
4·N_in/N visibly converges to π as N grows.

Vertical 1080 x 1920 Instagram Reel layout:
  - top band    : gradient title + area-ratio equation
  - middle band : square + circle filling up with random points
  - bottom band : estimator box + live N / π HUD
"""

from manim import *
import numpy as np

# ── Portrait 1080 × 1920 (Reels format) ─────────────────────────────────────
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 30
config.background_color = "#000000"
config.disable_caching = True


class MonteCarloPiReel(Scene):
    """1,000 seeded random points in [-1,1]²; the cumulative estimate
    4·N_in/N converges 2.60 → 3.1400 (true π = 3.14159…). Seed 53 was
    pre-screened so the convergence is real, monotone-ish, and lands close."""

    # ── Colour palette ────────────────────────────────────────────────────────
    COL_TITLE_A = "#FCD34D"   # gold  (gradient start)
    COL_TITLE_B = "#F87171"   # coral (gradient end)
    COL_SUB     = "#B0B8D0"   # soft grey-blue
    COL_IN      = "#58C4DD"   # points inside the circle (teal)
    COL_OUT     = "#FB923C"   # points outside (orange)
    COL_DONE    = "#00FF88"   # convergence green
    COL_EQ_BOX  = "#10102A"   # dark panel behind equations

    SIDE = 6.2                # square side length in scene units
    CENTER = np.array([0.0, 0.75, 0.0])
    BATCHES = [20, 40, 60, 100, 180, 280, 320]   # = 1,000 points

    def construct(self):
        # =====================================================================
        # Random points + running estimate (precomputed, seed pre-screened)
        # =====================================================================
        rng = np.random.default_rng(53)
        n_total = sum(self.BATCHES)
        pts = rng.uniform(-1, 1, (n_total, 2))
        inside = (pts ** 2).sum(axis=1) <= 1.0

        cum_n, cum_est = [], []
        n = 0
        for b in self.BATCHES:
            n += b
            cum_n.append(n)
            cum_est.append(4.0 * inside[:n].mean())

        # =====================================================================
        # SECTION 1: Title band (gradient gold→coral, no underline)
        # =====================================================================
        title = Tex("Monte Carlo Simulation", font_size=68)
        title.set_color_by_gradient(self.COL_TITLE_A, self.COL_TITLE_B)
        if title.width > 8.4:
            title.scale_to_fit_width(8.4)
        subtitle = Tex(r"\textit{estimating $\pi$ with random points}",
                       color=self.COL_SUB, font_size=34)
        title.to_edge(UP, buff=0.6)
        subtitle.next_to(title, DOWN, buff=0.25)

        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.3, rate_func=smooth)
        self.play(FadeIn(subtitle, shift=DOWN * 0.2), run_time=0.9)
        self.wait(0.3)

        ratio_eq = MathTex(
            r"P(\text{in circle})", r"=",
            r"\frac{\pi r^{2}}{(2r)^{2}}", r"=", r"\frac{\pi}{4}",
            font_size=32, color=WHITE,
        )
        ratio_eq[0].set_color(self.COL_IN)
        ratio_eq[4].set_color(self.COL_TITLE_A)
        ratio_eq.next_to(subtitle, DOWN, buff=0.42)
        self.play(Write(ratio_eq), run_time=1.4)
        self.wait(0.3)

        # =====================================================================
        # SECTION 2: Square + inscribed circle (middle band)
        # =====================================================================
        square = Square(side_length=self.SIDE, stroke_color=GREY_B,
                        stroke_width=2).move_to(self.CENTER)
        circle = Circle(radius=self.SIDE / 2, stroke_color=WHITE,
                        stroke_width=2.5).move_to(self.CENTER)
        circle.set_z_index(3)
        square.set_z_index(3)

        r_end = self.CENTER + (self.SIDE / 2) * np.array(
            [np.cos(30 * DEGREES), np.sin(30 * DEGREES), 0.0])
        r_line = DashedLine(self.CENTER, r_end, color=GREY_A,
                            stroke_width=2, dash_length=0.09)
        r_lbl = Tex("r", font_size=30, color=GREY_A)
        r_lbl.next_to(r_line.get_center(), UL, buff=0.08)

        self.play(Create(square), run_time=0.9)
        self.play(Create(circle), Create(r_line), FadeIn(r_lbl), run_time=1.1)
        self.wait(0.4)

        # =====================================================================
        # SECTION 3: Estimator box + HUD (bottom band)
        # =====================================================================
        est_eq = MathTex(r"\pi", r"\approx", r"4\cdot\frac{N_{\mathrm{in}}}{N}",
                         font_size=38, color=WHITE)
        est_eq[0].set_color(self.COL_TITLE_A)
        est_eq[2][2:5].set_color(self.COL_IN)
        est_eq.move_to(np.array([0.0, -4.75, 0.0]))

        est_box = SurroundingRectangle(
            est_eq, color=self.COL_TITLE_A, fill_color=self.COL_EQ_BOX,
            fill_opacity=0.78, buff=0.28, corner_radius=0.15, stroke_width=1.5,
        )
        note = Tex(r"uniform random points in $[-1,1]^{2}$",
                   font_size=26, color=GREY_A)
        note.next_to(est_box, DOWN, buff=0.28)

        n_label = Tex("N:", font_size=32, color=GREY_A)
        n_num = Integer(0, font_size=32, color=GREY_A)
        n_hud = VGroup(n_label, n_num).arrange(RIGHT, buff=0.15)
        n_hud.move_to(np.array([-1.6, -6.6, 0.0]))

        pi_label = MathTex(r"\pi \approx", font_size=32, color=GREY_A)
        pi_num = DecimalNumber(0.0, num_decimal_places=4,
                               font_size=32, color=GREY_A)
        pi_hud = VGroup(pi_label, pi_num).arrange(RIGHT, buff=0.15)
        pi_hud.move_to(np.array([1.6, -6.6, 0.0]))

        self.play(FadeIn(est_box, shift=UP * 0.3), Write(est_eq), run_time=1.3)
        self.play(FadeIn(note), FadeIn(n_hud), FadeIn(pi_hud), run_time=0.6)
        self.wait(0.4)

        # caption helper (sits between the square and the estimator box)
        def caption(tex_str, color=None):
            c = Tex(tex_str, font_size=32, color=color or self.COL_SUB)
            c.move_to(np.array([0.0, -3.05, 0.0]))
            return c

        cap = caption(r"Throw random points at the square")
        self.play(FadeIn(cap, shift=UP * 0.15), FadeOut(r_line), FadeOut(r_lbl),
                  run_time=0.6)

        # =====================================================================
        # SECTION 4: The rain — batches of points, estimate converging
        # =====================================================================
        half = self.SIDE / 2
        all_dots = VGroup()
        run_times = [1.0, 1.0, 1.1, 1.2, 1.4, 1.5, 1.6]

        start = 0
        for bi, b in enumerate(self.BATCHES):
            batch = VGroup()
            for x, y in pts[start:start + b]:
                d = Dot(self.CENTER + np.array([x * half, y * half, 0.0]),
                        radius=0.045,
                        color=self.COL_IN if x * x + y * y <= 1.0 else self.COL_OUT,
                        fill_opacity=0.9)
                batch.add(d)
            all_dots.add(*batch)
            start += b

            anims = [
                LaggedStart(*[FadeIn(d, scale=0.3) for d in batch],
                            lag_ratio=min(0.04, 1.2 / b)),
                ChangeDecimalToValue(n_num, cum_n[bi]),
                ChangeDecimalToValue(pi_num, cum_est[bi]),
            ]
            if bi == 3:   # halfway through, swap the caption
                cap2 = caption(r"More points $\rightarrow$ sharper estimate")
                anims.append(ReplacementTransform(cap, cap2))
                cap = cap2
            self.play(*anims, run_time=run_times[bi])
            self.wait(0.15)

        self.wait(0.4)

        # =====================================================================
        # SECTION 5: Convergence — compare with the true value
        # =====================================================================
        true_cap = caption(r"true value: $\pi = 3.14159\ldots$",
                           color=self.COL_TITLE_A)
        self.play(
            ReplacementTransform(cap, true_cap),
            pi_num.animate.set_color(self.COL_DONE),
            pi_label.animate.set_color(self.COL_DONE),
            run_time=0.8,
        )
        self.play(Flash(pi_hud.get_center(), color=self.COL_DONE,
                        line_length=0.3, num_lines=12, flash_radius=0.7),
                  run_time=0.8)

        done_label = Tex("The Law of Large Numbers", font_size=36,
                         color=self.COL_DONE)
        done_label.move_to(np.array([0.0, -7.4, 0.0]))
        self.play(FadeIn(done_label, shift=UP * 0.2), run_time=1.0)
        self.wait(2.4)

        # =====================================================================
        # SECTION 6: Fade out
        # =====================================================================
        everything = VGroup(
            title, subtitle, ratio_eq, square, circle, all_dots, true_cap,
            est_box, est_eq, note, n_hud, pi_hud, done_label,
        )
        self.play(FadeOut(everything, shift=DOWN * 0.3), run_time=1.4,
                  rate_func=smooth)
        self.wait(0.4)
