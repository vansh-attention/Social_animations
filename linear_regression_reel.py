"""
Linear regression fitting itself to noisy data, step by step.
Vertical 1080 x 1920 Instagram Reel layout:
  - top band    : gradient-yellow title + model / loss equations
  - middle band : scatter plot, descending fit line with live residuals
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


class LinearRegressionReel(Scene):
    """
    Fits y = w x + b to noisy points by gradient descent on the MSE.
    The descent runs in standardized-x space so both parameters converge
    in ~16 visible steps, but everything displayed is in data space.
    """

    # ── Colour palette ────────────────────────────────────────────────────────
    COL_TITLE_A  = "#FFE259"   # gradient yellow (light)
    COL_TITLE_B  = "#FFA751"   # gradient yellow (deep)
    COL_ACCENT   = "#58C4DD"   # 3B1B teal accents
    COL_SUBTITLE = "#B0B8D0"   # soft grey-blue
    COL_POINT    = "#58C4DD"   # data points
    COL_LINE     = "#FF4444"   # fit line while descending
    COL_DONE     = "#00FF88"   # converged line
    COL_RESID    = "#FFB347"   # residual dashes
    COL_EQ_BOX   = "#10102A"   # dark panel behind equations

    def construct(self):
        # =====================================================================
        # Data + gradient descent path (precomputed)
        # =====================================================================
        rng = np.random.default_rng(7)
        n_pts = 14
        xs = np.sort(rng.uniform(0.6, 9.4, n_pts))
        ys = np.clip(0.72 * xs + 1.3 + rng.normal(0.0, 0.55, n_pts), 0.4, 9.6)

        N_STEPS = 16
        LR = 0.12
        w_start, b_start = -0.35, 7.6

        # descend in standardized-x space (well-conditioned), display in data space
        mu, sd = xs.mean(), xs.std()
        zs = (xs - mu) / sd
        wz, bz = w_start * sd, w_start * mu + b_start

        def to_data_space(wz_, bz_):
            return wz_ / sd, bz_ - wz_ * mu / sd

        path = [(w_start, b_start)]
        for _ in range(N_STEPS):
            err = wz * zs + bz - ys
            wz -= LR * 2.0 * np.mean(err * zs)
            bz -= LR * 2.0 * np.mean(err)
            path.append(to_data_space(wz, bz))
        losses = [float(np.mean((w * xs + b - ys) ** 2)) for w, b in path]
        w_fit, b_fit = path[-1]

        # =====================================================================
        # SECTION 1: Title band (gradient yellow, no divider)
        # =====================================================================
        title = Tex("Linear Regression", font_size=78)
        title.set_color_by_gradient(self.COL_TITLE_A, self.COL_TITLE_B)
        subtitle = Tex(r"\textit{fitting the best line through data}",
                       color=self.COL_SUBTITLE, font_size=34)

        title.to_edge(UP, buff=0.6)
        subtitle.next_to(title, DOWN, buff=0.25)

        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.3, rate_func=smooth)
        self.play(FadeIn(subtitle, shift=DOWN * 0.2), run_time=0.9)
        self.wait(0.4)

        # =====================================================================
        # SECTION 2: Model + loss equations
        # =====================================================================
        model_eq = MathTex(r"\hat{y}", r"=", r"w", r"\,x", r"+", r"b",
                           font_size=42, color=WHITE)
        model_eq[0].set_color(self.COL_ACCENT)
        model_eq[2].set_color(self.COL_TITLE_A)
        model_eq[5].set_color(self.COL_RESID)
        model_eq.next_to(subtitle, DOWN, buff=0.55)

        loss_eq = MathTex(
            r"L(w, b) = \frac{1}{n}\sum_{i=1}^{n}\left(y_i - \hat{y}_i\right)^{2}",
            font_size=30, color=WHITE,
        )
        loss_eq[0][0:6].set_color(self.COL_ACCENT)
        loss_eq.next_to(model_eq, DOWN, buff=0.35)

        self.play(Write(model_eq), run_time=1.1)
        self.play(Write(loss_eq), run_time=1.4)
        self.wait(0.4)

        # =====================================================================
        # SECTION 3: Scatter plot (middle band)
        # =====================================================================
        axes = Axes(
            x_range=[0, 10, 2],
            y_range=[0, 10, 2],
            x_length=7.4,
            y_length=6.0,
            axis_config={
                "color": GREY_B,
                "stroke_width": 1.5,
                "include_tip": True,
                "tip_length": 0.15,
            },
        )
        axes.move_to(np.array([0.0, 0.7, 0.0]))
        x_lbl = Tex("x", font_size=30, color=GREY_A)
        x_lbl.next_to(axes.x_axis.get_end(), DR, buff=0.15)
        y_lbl = Tex("y", font_size=30, color=GREY_A)
        y_lbl.next_to(axes.y_axis.get_end(), UL, buff=0.15)

        dots = VGroup(*[
            Dot(axes.c2p(x, y), radius=0.075, color=self.COL_POINT)
            for x, y in zip(xs, ys)
        ])

        self.play(Create(axes), FadeIn(x_lbl), FadeIn(y_lbl), run_time=1.2)
        self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in dots],
                              lag_ratio=0.08), run_time=1.4)
        self.wait(0.4)

        # =====================================================================
        # SECTION 4: Starting line + residuals
        # =====================================================================
        w_t = ValueTracker(w_start)
        b_t = ValueTracker(b_start)

        def line_pts():
            w, b = w_t.get_value(), b_t.get_value()
            return axes.c2p(0.2, w * 0.2 + b), axes.c2p(9.8, w * 9.8 + b)

        fit_line = always_redraw(
            lambda: Line(*line_pts(), color=self.COL_LINE, stroke_width=4)
        )

        def make_resid(xi, yi):
            def build():
                yhat = w_t.get_value() * xi + b_t.get_value()
                if abs(yhat - yi) < 1e-3:           # DashedLine needs length > 0
                    yhat = yi + 1e-3
                return DashedLine(
                    axes.c2p(xi, yi), axes.c2p(xi, yhat),
                    color=self.COL_RESID, stroke_width=2,
                    stroke_opacity=0.75, dash_length=0.08,
                )
            return always_redraw(build)

        residuals = VGroup(*[make_resid(x, y) for x, y in zip(xs, ys)])

        first_line = Line(*line_pts(), color=self.COL_LINE, stroke_width=4)
        self.play(Create(first_line), run_time=1.0)
        self.remove(first_line)
        self.add(fit_line)
        self.play(FadeIn(residuals), run_time=0.8)
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
            font_size=30,
            color=WHITE,
        )
        update_rule[0].set_color(self.COL_ACCENT)
        update_rule[4].set_color(YELLOW)
        update_rule[5].set_color(self.COL_RESID)
        update_rule.move_to(np.array([0.0, -4.7, 0.0]))

        update_box = SurroundingRectangle(
            update_rule,
            color=self.COL_ACCENT,
            fill_color=self.COL_EQ_BOX,
            fill_opacity=0.75,
            buff=0.25,
            corner_radius=0.15,
            stroke_width=1.5,
        )

        lr_label = MathTex(rf"\alpha = {LR}", font_size=28, color=GREY_A)
        lr_label.next_to(update_box, DOWN, buff=0.3)

        step_label = Tex("Step:", font_size=32, color=GREY_A)
        step_num = Integer(0, font_size=32, color=GREY_A)
        step_hud = VGroup(step_label, step_num).arrange(RIGHT, buff=0.15)
        step_hud.move_to(np.array([-1.6, -6.55, 0.0]))

        val_label = MathTex(r"L =", font_size=32, color=GREY_A)
        val_num = DecimalNumber(losses[0], num_decimal_places=3,
                                font_size=32, color=GREY_A)
        val_hud = VGroup(val_label, val_num).arrange(RIGHT, buff=0.15)
        val_hud.move_to(np.array([1.6, -6.55, 0.0]))

        self.play(FadeIn(update_box, shift=UP * 0.3), Write(update_rule), run_time=1.4)
        self.play(FadeIn(lr_label), FadeIn(step_hud), FadeIn(val_hud), run_time=0.6)
        self.wait(0.5)

        # =====================================================================
        # SECTION 6: Descent — the line fits itself
        # =====================================================================
        for k in range(1, N_STEPS + 1):
            w_k, b_k = path[k]
            self.play(
                w_t.animate.set_value(w_k),
                b_t.animate.set_value(b_k),
                ChangeDecimalToValue(step_num, k),
                ChangeDecimalToValue(val_num, losses[k]),
                run_time=0.4,
                rate_func=smooth,
            )

        # =====================================================================
        # SECTION 7: Convergence
        # =====================================================================
        residuals.clear_updaters()
        for r in residuals:
            r.clear_updaters()
        final_line = Line(*line_pts(), color=self.COL_LINE, stroke_width=4)
        self.remove(fit_line)
        self.add(final_line)

        self.play(final_line.animate.set_color(self.COL_DONE), run_time=0.6)
        self.play(
            Flash(axes.c2p(5.0, w_fit * 5.0 + b_fit), color=self.COL_DONE,
                  line_length=0.3, num_lines=12, flash_radius=0.6),
            run_time=0.8,
        )

        fit_eq = MathTex(
            rf"\hat{{y}} = {w_fit:.2f}\,x + {b_fit:.2f}",
            font_size=34, color=self.COL_DONE,
        )
        fit_eq.move_to(axes.c2p(2.9, 8.6))

        done_label = Tex("Best Fit Found", font_size=36, color=self.COL_DONE)
        done_label.move_to(np.array([0.0, -7.35, 0.0]))

        self.play(FadeIn(fit_eq, shift=DOWN * 0.2),
                  FadeIn(done_label, shift=UP * 0.2), run_time=1.0)
        self.wait(2.4)

        # =====================================================================
        # SECTION 8: Fade out
        # =====================================================================
        everything = VGroup(
            title, subtitle, model_eq, loss_eq,
            axes, x_lbl, y_lbl, dots, residuals, final_line, fit_eq,
            update_box, update_rule, lr_label, step_hud, val_hud, done_label,
        )
        self.play(FadeOut(everything, shift=DOWN * 0.3), run_time=1.4, rate_func=smooth)
        self.wait(0.4)
