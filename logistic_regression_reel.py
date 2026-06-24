"""
Logistic regression learning to classify, step by step.
A sigmoid σ(wx + b) fits binary 0/1-labelled points by gradient descent on
the cross-entropy loss; the decision boundary at p = 0.5 slides into place.

Vertical 1080 x 1920 Instagram Reel layout:
  - top band    : gradient title + sigmoid / model equations
  - middle band : 1D classification data, descending sigmoid + boundary
  - bottom band : update rule + live step / loss HUD
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


class LogisticRegressionReel(Scene):
    """
    Fits p = σ(w x + b) to two overlapping 1D classes by gradient descent on
    binary cross-entropy. Descent runs in standardized-x space so both
    parameters converge in ~18 visible steps; everything shown is data space.
    """

    # ── Colour palette ────────────────────────────────────────────────────────
    COL_TITLE_A = "#F472B6"   # pink  (gradient start)
    COL_TITLE_B = "#A78BFA"   # purple (gradient end)
    COL_SUB     = "#B0B8D0"   # soft grey-blue
    COL_C0      = "#58C4DD"   # class 0 points
    COL_C1      = "#FF6B6B"   # class 1 points
    COL_CURVE   = "#FFD93D"   # sigmoid while descending
    COL_DONE    = "#00FF88"   # converged sigmoid
    COL_BOUND   = "#C9B6FF"   # decision boundary
    COL_EQ_BOX  = "#10102A"   # dark panel behind equations

    @staticmethod
    def sigmoid(z):
        return 1.0 / (1.0 + np.exp(-z))

    def construct(self):
        # =====================================================================
        # Data + gradient-descent path (precomputed)
        # =====================================================================
        rng = np.random.default_rng(3)
        n0, n1 = 11, 11
        x0 = np.clip(rng.normal(2.8, 1.05, n0), 0.4, 8.6)   # class 0 (low x)
        x1 = np.clip(rng.normal(6.3, 1.05, n1), 0.4, 8.6)   # class 1 (high x)
        xs = np.concatenate([x0, x1])
        ys = np.concatenate([np.zeros(n0), np.ones(n1)])
        y0_jit = rng.uniform(0.02, 0.08, n0)                 # tiny y-jitter so
        y1_jit = rng.uniform(0.92, 0.98, n1)                 # dots are visible

        N_STEPS = 18
        LR = 0.6
        mu, sd = xs.mean(), xs.std()
        zs = (xs - mu) / sd
        wz, bz = 0.22, 0.0          # start: an almost-flat sigmoid near 0.5

        def to_data_space(wz_, bz_):
            return wz_ / sd, bz_ - wz_ * mu / sd

        def bce(w, b):
            p = np.clip(self.sigmoid(w * xs + b), 1e-7, 1 - 1e-7)
            return float(-np.mean(ys * np.log(p) + (1 - ys) * np.log(1 - p)))

        path = [to_data_space(wz, bz)]
        for _ in range(N_STEPS):
            p = self.sigmoid(wz * zs + bz)
            wz -= LR * np.mean((p - ys) * zs)
            bz -= LR * np.mean(p - ys)
            path.append(to_data_space(wz, bz))
        losses = [bce(w, b) for w, b in path]
        w_fit, b_fit = path[-1]
        x_star = -b_fit / w_fit                              # boundary, p = 0.5

        # =====================================================================
        # SECTION 1: Title band (gradient pink→purple, no underline)
        # =====================================================================
        title = Tex("Logistic Regression", font_size=74)
        title.set_color_by_gradient(self.COL_TITLE_A, self.COL_TITLE_B)
        if title.width > 8.4:
            title.scale_to_fit_width(8.4)
        subtitle = Tex(r"\textit{classifying with the sigmoid}",
                       color=self.COL_SUB, font_size=34)
        title.to_edge(UP, buff=0.6)
        subtitle.next_to(title, DOWN, buff=0.25)

        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.3, rate_func=smooth)
        self.play(FadeIn(subtitle, shift=DOWN * 0.2), run_time=0.9)
        self.wait(0.3)

        # =====================================================================
        # SECTION 2: Model + sigmoid equations
        # =====================================================================
        model_eq = MathTex(r"p", r"=", r"\sigma(", r"w", r"x", r"+", r"b", r")",
                           font_size=40, color=WHITE)
        model_eq[0].set_color(self.COL_DONE)
        model_eq[3].set_color(self.COL_TITLE_A)
        model_eq[6].set_color(self.COL_C1)
        model_eq.next_to(subtitle, DOWN, buff=0.38)

        sig_eq = MathTex(r"\sigma(z) = \frac{1}{1 + e^{-z}}",
                         font_size=30, color=WHITE)
        sig_eq[0][0].set_color(self.COL_DONE)
        sig_eq.next_to(model_eq, DOWN, buff=0.26)

        # binary cross-entropy: the loss L that gradient descent minimises
        bce_eq = MathTex(
            r"L = -\frac{1}{N}\sum_{i=1}^{N}\big[",
            r"y_i \log(p_i) + (1 - y_i)\log(1 - p_i)",
            r"\big]",
            font_size=28, color=WHITE,
        )
        bce_eq[0][0].set_color(self.COL_CURVE)
        if bce_eq.width > 8.3:
            bce_eq.scale_to_fit_width(8.3)
        bce_eq.next_to(sig_eq, DOWN, buff=0.28)

        self.play(Write(model_eq), run_time=1.0)
        self.play(Write(sig_eq), run_time=1.0)
        self.play(Write(bce_eq), run_time=1.4)
        self.wait(0.4)

        # =====================================================================
        # SECTION 3: Axes + 1D classification data
        # =====================================================================
        axes = Axes(
            x_range=[0, 9, 1], y_range=[0, 1, 0.5],
            x_length=7.4, y_length=4.3,
            axis_config={"color": GREY_B, "stroke_width": 1.5,
                         "include_tip": True, "tip_length": 0.15},
            y_axis_config={"decimal_number_config": {"num_decimal_places": 1}},
        )
        axes.move_to(np.array([0.0, -0.15, 0.0]))
        axes.add_coordinates(
            np.arange(0, 10, 3),
            np.array([0.0, 0.5, 1.0]),
        )
        x_lbl = Tex("x", font_size=30, color=GREY_A).next_to(axes.x_axis.get_end(), DR, buff=0.12)
        y_lbl = MathTex("p", font_size=32, color=GREY_A).next_to(axes.y_axis.get_end(), UL, buff=0.0)

        half_line = DashedLine(axes.c2p(0, 0.5), axes.c2p(9, 0.5),
                               color=GREY_D, stroke_width=2, dash_length=0.1)
        half_lbl = MathTex("p = 0.5", font_size=24, color=GREY_B)
        half_lbl.next_to(axes.c2p(9, 0.5), UP, buff=0.08).shift(LEFT * 0.55)

        dots0 = VGroup(*[Dot(axes.c2p(x, j), radius=0.075, color=self.COL_C0)
                         for x, j in zip(x0, y0_jit)])
        dots1 = VGroup(*[Dot(axes.c2p(x, j), radius=0.075, color=self.COL_C1)
                         for x, j in zip(x1, y1_jit)])

        self.play(Create(axes), FadeIn(x_lbl), FadeIn(y_lbl), run_time=1.2)
        self.play(Create(half_line), FadeIn(half_lbl), run_time=0.6)
        self.play(
            LaggedStart(*[FadeIn(d, scale=0.4) for d in (*dots0, *dots1)],
                        lag_ratio=0.06),
            run_time=1.5,
        )
        self.wait(0.4)

        # =====================================================================
        # SECTION 4: Starting sigmoid + moving decision boundary
        # =====================================================================
        w_t = ValueTracker(path[0][0])
        b_t = ValueTracker(path[0][1])

        curve = always_redraw(lambda: axes.plot(
            lambda x: self.sigmoid(w_t.get_value() * x + b_t.get_value()),
            x_range=[0, 9, 0.05], color=self.COL_CURVE, stroke_width=5,
        ))

        def boundary_x():
            w = w_t.get_value()
            return float(np.clip(-b_t.get_value() / w if abs(w) > 1e-4 else 9, 0, 9))

        boundary = always_redraw(lambda: DashedLine(
            axes.c2p(boundary_x(), 0), axes.c2p(boundary_x(), 1),
            color=self.COL_BOUND, stroke_width=3, dash_length=0.09,
        ))

        self.play(Create(curve), run_time=1.0)
        self.play(Create(boundary), run_time=0.7)
        self.wait(0.4)

        # =====================================================================
        # SECTION 5: Update rule + HUD (bottom band)
        # =====================================================================
        update_rule = MathTex(
            r"\begin{bmatrix} w \\ b \end{bmatrix}_{t+1}",
            r"=",
            r"\begin{bmatrix} w \\ b \end{bmatrix}_{t}",
            r"-",
            r"\alpha",
            r"\begin{bmatrix} \dfrac{\partial L}{\partial w} \\[2.6ex]"
            r" \dfrac{\partial L}{\partial b} \end{bmatrix}",
            font_size=30, color=WHITE,
        )
        update_rule[0].set_color(self.COL_TITLE_B)
        update_rule[4].set_color(YELLOW)
        update_rule[5].set_color(self.COL_CURVE)
        update_rule.move_to(np.array([0.0, -4.7, 0.0]))

        update_box = SurroundingRectangle(
            update_rule, color=self.COL_TITLE_B, fill_color=self.COL_EQ_BOX,
            fill_opacity=0.78, buff=0.25, corner_radius=0.15, stroke_width=1.5,
        )
        loss_note = MathTex(r"L = \text{cross-entropy}", font_size=26, color=GREY_A)
        loss_note.next_to(update_box, DOWN, buff=0.28)

        step_label = Tex("Step:", font_size=32, color=GREY_A)
        step_num = Integer(0, font_size=32, color=GREY_A)
        step_hud = VGroup(step_label, step_num).arrange(RIGHT, buff=0.15)
        step_hud.move_to(np.array([-1.6, -6.6, 0.0]))

        val_label = MathTex(r"L =", font_size=32, color=GREY_A)
        val_num = DecimalNumber(losses[0], num_decimal_places=3,
                                font_size=32, color=GREY_A)
        val_hud = VGroup(val_label, val_num).arrange(RIGHT, buff=0.15)
        val_hud.move_to(np.array([1.6, -6.6, 0.0]))

        self.play(FadeIn(update_box, shift=UP * 0.3), Write(update_rule), run_time=1.4)
        self.play(FadeIn(loss_note), FadeIn(step_hud), FadeIn(val_hud), run_time=0.6)
        self.wait(0.5)

        # =====================================================================
        # SECTION 6: Descent — the sigmoid sharpens to fit
        # =====================================================================
        for k in range(1, N_STEPS + 1):
            w_k, b_k = path[k]
            self.play(
                w_t.animate.set_value(w_k),
                b_t.animate.set_value(b_k),
                ChangeDecimalToValue(step_num, k),
                ChangeDecimalToValue(val_num, losses[k]),
                run_time=0.36, rate_func=smooth,
            )

        # =====================================================================
        # SECTION 7: Convergence — freeze curve, shade decision regions
        # =====================================================================
        curve.clear_updaters()
        boundary.clear_updaters()
        final_curve = axes.plot(
            lambda x: self.sigmoid(w_fit * x + b_fit),
            x_range=[0, 9, 0.05], color=self.COL_CURVE, stroke_width=5,
        )
        self.remove(curve)
        self.add(final_curve)

        def region(x_lo, x_hi, color):
            poly = Polygon(
                axes.c2p(x_lo, 0), axes.c2p(x_hi, 0),
                axes.c2p(x_hi, 1), axes.c2p(x_lo, 1),
                stroke_width=0, fill_color=color, fill_opacity=0.10,
            )
            poly.set_z_index(-2)
            return poly

        reg0 = region(0, x_star, self.COL_C0)
        reg1 = region(x_star, 9, self.COL_C1)

        self.play(final_curve.animate.set_color(self.COL_DONE),
                  FadeIn(reg0), FadeIn(reg1), run_time=0.8)
        self.play(
            Flash(axes.c2p(x_star, 0.5), color=self.COL_DONE,
                  line_length=0.3, num_lines=12, flash_radius=0.6),
            run_time=0.8,
        )

        done_label = Tex("Model Trained", font_size=36, color=self.COL_DONE)
        done_label.move_to(np.array([0.0, -7.4, 0.0]))
        bx_label = MathTex(rf"\text{{boundary: }} x = {x_star:.2f}",
                           font_size=30, color=self.COL_BOUND)
        bx_label.move_to(axes.c2p(2.4, 0.86))

        self.play(FadeIn(done_label, shift=UP * 0.2),
                  FadeIn(bx_label, shift=DOWN * 0.2), run_time=1.0)
        self.wait(2.4)

        # =====================================================================
        # SECTION 8: Fade out
        # =====================================================================
        everything = VGroup(
            title, subtitle, model_eq, sig_eq,
            axes, x_lbl, y_lbl, half_line, half_lbl, dots0, dots1,
            final_curve, boundary, reg0, reg1, bx_label,
            update_box, update_rule, loss_note, step_hud, val_hud, done_label,
        )
        self.play(FadeOut(everything, shift=DOWN * 0.3), run_time=1.4, rate_func=smooth)
        self.wait(0.4)
