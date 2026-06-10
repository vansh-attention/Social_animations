"""
Gradient descent on a non-convex "rippled bowl" loss surface.
Vertical 1080 x 1920 Instagram Reel layout:
  - top band    : 2D title + loss equation (fixed in frame)
  - middle band : rotating 3D surface with descending ball
  - bottom band : 2D update rule + live step / loss HUD (fixed in frame)
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
# always render fresh — stale cached partial movies can splice old (buggy)
# HUD segments into the final video
config.disable_caching = True


class RippleDescentReel(ThreeDScene):
    """
    Gradient descent over L(w, b) = 0.4(w² + b²) − 1.2·cos(1.5w)·cos(1.5b) + 1.2 —
    a bowl with ripples, so the ball visibly slows on a plateau before
    dropping into the global minimum.
    """

    # ── Colour palette ────────────────────────────────────────────────────────
    COL_TITLE     = "#58C4DD"   # 3B1B teal
    COL_SUBTITLE  = "#B0B8D0"   # soft grey-blue
    COL_BALL      = "#FF4444"   # red descent ball
    COL_BALL_DONE = "#00FF88"   # green at convergence
    COL_TRAIL     = "#FFB347"   # warm trail
    COL_GRAD      = "#7CFC00"   # gradient-step arrows
    COL_EQ_BOX    = "#10102A"   # dark panel behind equations
    COL_WIRE      = "#80FFE0"   # surface wireframe

    # ── Loss surface and its analytic gradient ────────────────────────────────
    @staticmethod
    def loss(w, b):
        return 0.4 * (w * w + b * b) - 1.2 * np.cos(1.5 * w) * np.cos(1.5 * b) + 1.2

    @staticmethod
    def grad(w, b):
        dw = 0.8 * w + 1.8 * np.sin(1.5 * w) * np.cos(1.5 * b)
        db = 0.8 * b + 1.8 * np.cos(1.5 * w) * np.sin(1.5 * b)
        return dw, db

    def gd_path(self, w0, b0, lr, n):
        pts = [(w0, b0)]
        for _ in range(n):
            w, b = pts[-1]
            dw, db = self.grad(w, b)
            pts.append((w - lr * dw, b - lr * db))
        return pts

    # ── Scene ─────────────────────────────────────────────────────────────────
    def construct(self):
        N_STEPS = 24
        LR = 0.12
        START_W, START_B = 2.4, -2.0
        path = self.gd_path(START_W, START_B, LR, N_STEPS)

        # =====================================================================
        # SECTION 1: Title band (2D, top of the vertical frame)
        # =====================================================================
        title = Tex(
            "Gradient Descent",
            color=self.COL_TITLE,
            font_size=78,
        )
        subtitle = Tex(
            r"\textit{Fundamental Base of AI}",
            color=self.COL_SUBTITLE,
            font_size=34,
        )
        divider = Line(LEFT * 2.6, RIGHT * 2.6, color=self.COL_TITLE, stroke_width=2)

        title.to_edge(UP, buff=0.6)
        subtitle.next_to(title, DOWN, buff=0.25)
        divider.next_to(subtitle, DOWN, buff=0.25)

        self.add_fixed_in_frame_mobjects(title, subtitle, divider)
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.4, rate_func=smooth)
        self.play(FadeIn(subtitle, shift=DOWN * 0.2), GrowFromCenter(divider), run_time=1.0)
        self.wait(0.5)

        # =====================================================================
        # SECTION 2: Loss equation (2D, just under the title band)
        # =====================================================================
        loss_eq = MathTex(
            r"L(w, b) = 0.4\,(w^{2} + b^{2}) - 1.2\cos(1.5w)\cos(1.5b) + 1.2",
            font_size=30,
            color=WHITE,
        )
        loss_eq[0][0:6].set_color(self.COL_TITLE)
        loss_eq.next_to(divider, DOWN, buff=0.45)

        self.add_fixed_in_frame_mobjects(loss_eq)
        self.play(Write(loss_eq), run_time=1.6)
        self.wait(0.5)

        # =====================================================================
        # SECTION 3: 3D surface (middle band)
        # =====================================================================
        # frame_center (not a mobject shift) keeps the surface on the camera's
        # rotation axis, so it stays centred while the camera orbits.
        self.set_camera_orientation(
            phi=66 * DEGREES,
            theta=-50 * DEGREES,
            zoom=0.8,
            frame_center=np.array([0.0, 0.0, 1.1]),
        )

        axes = ThreeDAxes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            z_range=[0, 6, 2],
            x_length=6.8,
            y_length=6.8,
            z_length=4.2,
            axis_config={
                "color": GREY_B,
                "stroke_width": 1.5,
                "include_tip": True,
                "tip_length": 0.15,
            },
        )
        w_lbl = axes.get_x_axis_label(Tex("w", font_size=34), edge=RIGHT, direction=RIGHT)
        b_lbl = axes.get_y_axis_label(Tex("b", font_size=34), edge=UP, direction=UP)
        l_lbl = Tex("L", font_size=34, color=WHITE).next_to(axes.z_axis.get_end(), UP, buff=0.15)

        surface = Surface(
            lambda u, v: axes.c2p(u, v, self.loss(u, v)),
            u_range=[-2.6, 2.6],
            v_range=[-2.6, 2.6],
            resolution=(36, 36),
            fill_opacity=0.86,
            stroke_color=self.COL_WIRE,
            stroke_width=0.3,
            stroke_opacity=0.35,
        )
        surface.set_fill_by_value(
            axes=axes,
            colorscale=[
                ManimColor("#12005E"),
                ManimColor("#1565C0"),
                ManimColor("#26A69A"),
                ManimColor("#FFB300"),
                ManimColor("#E53935"),
            ],
            axis=2,
        )

        self.play(Create(axes), run_time=1.4)
        self.add(w_lbl, b_lbl, l_lbl)
        self.play(Create(surface), run_time=2.6, rate_func=smooth)
        self.wait(0.5)

        # =====================================================================
        # SECTION 4: Update rule + HUD (2D, bottom band)
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
        update_rule[0].set_color(self.COL_TITLE)
        update_rule[4].set_color(YELLOW)
        update_rule[5].set_color(self.COL_TRAIL)
        update_rule.move_to(np.array([0, -5.4, 0]))

        update_box = SurroundingRectangle(
            update_rule,
            color=self.COL_TITLE,
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
        step_hud.move_to(np.array([-1.6, -7.2, 0]))

        val_label = MathTex(r"L =", font_size=32, color=GREY_A)
        val_num = DecimalNumber(
            self.loss(START_W, START_B),
            num_decimal_places=3,
            font_size=32,
            color=GREY_A,
        )
        val_hud = VGroup(val_label, val_num).arrange(RIGHT, buff=0.15)
        val_hud.move_to(np.array([1.6, -7.2, 0]))

        self.add_fixed_in_frame_mobjects(update_box, update_rule, lr_label, step_hud, val_hud)
        self.play(FadeIn(update_box, shift=UP * 0.3), Write(update_rule), run_time=1.5)
        self.play(FadeIn(lr_label), FadeIn(step_hud), FadeIn(val_hud), run_time=0.7)
        self.wait(0.6)

        # =====================================================================
        # SECTION 5: Descent with ambient rotation
        # =====================================================================
        path_3d = [axes.c2p(w, b, self.loss(w, b)) for w, b in path]

        ball = Sphere(radius=0.13, resolution=(12, 12))
        ball.set_color(self.COL_BALL)
        ball.set_opacity(1.0)
        ball.move_to(path_3d[0])

        self.play(FadeIn(ball, scale=0.4), run_time=0.7)
        self.wait(0.4)

        self.begin_ambient_camera_rotation(rate=0.07)

        trail = VGroup()
        for i in range(N_STEPS):
            z_nxt = self.loss(*path[i + 1])

            ghost = Dot3D(path_3d[i], radius=0.05, color=self.COL_TRAIL)
            ghost.set_opacity(0.6)
            trail.add(ghost)
            self.add(ghost)

            arrow = Arrow3D(
                start=path_3d[i],
                end=path_3d[i + 1],
                color=self.COL_GRAD,
                thickness=0.012,
                base_radius=0.03,
            )

            # set_value regenerates the digit submobjects, which drops their
            # fixed-in-frame status in ThreeDScene — re-register them each step.
            step_num.set_value(i + 1)
            val_num.set_value(z_nxt)
            step_num.next_to(step_label, RIGHT, buff=0.15)
            val_num.next_to(val_label, RIGHT, buff=0.15)
            # camera method only: scene.add_fixed_in_frame_mobjects would also
            # self.add() them as top-level mobjects, drawing them twice.
            self.camera.add_fixed_in_frame_mobjects(step_num, val_num)

            self.play(
                Create(arrow),
                ball.animate.move_to(path_3d[i + 1]),
                run_time=0.45,
                rate_func=smooth,
            )
            self.remove(arrow)

        # =====================================================================
        # SECTION 6: Convergence
        # =====================================================================
        self.play(ball.animate.set_color(self.COL_BALL_DONE), run_time=0.5)
        self.play(
            Flash(ball, color=self.COL_BALL_DONE, line_length=0.3,
                  num_lines=12, flash_radius=0.5),
            run_time=0.8,
        )

        min_label = Tex(
            "Global Minimum Reached",
            font_size=36,
            color=self.COL_BALL_DONE,
        )
        min_label.move_to(np.array([0.0, -7.7, 0]))
        self.add_fixed_in_frame_mobjects(min_label)
        self.play(FadeIn(min_label, shift=UP * 0.2), run_time=1.0)

        # Slow rotation to showcase the rippled surface
        self.wait(4.0)
        self.stop_ambient_camera_rotation()
        self.wait(0.4)

        # =====================================================================
        # SECTION 7: Fade out
        # =====================================================================
        all_3d = VGroup(axes, surface, ball, trail, w_lbl, b_lbl, l_lbl)
        all_2d = VGroup(
            title, subtitle, divider, loss_eq,
            update_box, update_rule, lr_label,
            step_hud, val_hud, min_label,
        )
        self.play(
            FadeOut(all_3d, shift=IN * 0.5),
            FadeOut(all_2d, shift=DOWN * 0.3),
            run_time=1.5,
            rate_func=smooth,
        )
        self.wait(0.5)
