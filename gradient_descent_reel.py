from manim import *
import numpy as np

# ── Portrait 1080 × 1920 (Reels format) ─────────────────────────────────────
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 30
config.background_color = "#000000"  # Pure black background


class GradientDescentReel(ThreeDScene):
    """
    3Blue1Brown-style vertical reel explaining gradient descent
    with a 3D paraboloid surface, smooth descent animation, and 2D equations.
    """

    # ── Colour palette ────────────────────────────────────────────────────────
    COL_TITLE      = "#58C4DD"      # Cyan heading
    COL_SUBTITLE   = "#B0B8D0"      # Soft grey-blue
    COL_ACCENT     = "#58C4DD"      # 3B1B teal
    COL_BALL       = "#FF4444"      # Red descent ball
    COL_BALL_DONE  = "#00FF88"      # Green when converged
    COL_TRAIL      = "#FF8844"      # Warm trail dots
    COL_EQ_BOX     = "#1A1A3A"      # Dark box behind equations
    COL_WIREFRAME  = "#80FFE0"

    # ── Loss function ─────────────────────────────────────────────────────────
    @staticmethod
    def loss(x, y):
        return x ** 2 + y ** 2

    # ── Gradient descent path ─────────────────────────────────────────────────
    @staticmethod
    def gd_path(x0, y0, lr, n):
        pts = [(x0, y0)]
        for _ in range(n):
            x, y = pts[-1]
            pts.append((x - lr * 2 * x, y - lr * 2 * y))
        return pts

    # ── Build scene ───────────────────────────────────────────────────────────
    def construct(self):
        # Parameters
        N_STEPS = 15
        LR = 0.18
        START_X, START_Y = 2.2, 1.8
        path = self.gd_path(START_X, START_Y, LR, N_STEPS)

        # =====================================================================
        # SECTION 1:  Title card
        # =====================================================================
        title = Text(
            "Gradient Descent",
            font="CMU Serif",
            weight=BOLD,
            color=self.COL_TITLE,
            font_size=60,
        )
        subtitle = Text(
            "Finding the minimum of a function",
            font="CMU Serif",
            color=self.COL_SUBTITLE,
            font_size=28,
            slant=ITALIC,
        )
        deco_line = Line(LEFT * 2.5, RIGHT * 2.5, color=self.COL_ACCENT, stroke_width=2)

        title.to_edge(UP, buff=0.65)
        subtitle.next_to(title, DOWN, buff=0.25)
        deco_line.next_to(subtitle, DOWN, buff=0.25)

        self.add_fixed_in_frame_mobjects(title, subtitle, deco_line)

        # Smooth title entrance (not rushed)
        self.play(
            FadeIn(title, shift=DOWN * 0.3),
            run_time=1.5,
            rate_func=smooth,
        )
        self.play(
            FadeIn(subtitle, shift=DOWN * 0.2),
            GrowFromCenter(deco_line),
            run_time=1.2,
        )
        self.wait(0.6)

        # =====================================================================
        # SECTION 2:  Loss function equation (2D overlay)
        # =====================================================================
        loss_label = Tex(r"Loss surface:", font_size=32, color=self.COL_SUBTITLE)
        loss_eq = MathTex(
            r"L(w, b) = w^{2} + b^{2}",
            font_size=44,
            color=WHITE,
        )
        loss_eq[0][0:6].set_color(self.COL_ACCENT)

        eq_group_top = VGroup(loss_label, loss_eq).arrange(DOWN, buff=0.2)
        eq_group_top.next_to(deco_line, DOWN, buff=0.5)

        self.add_fixed_in_frame_mobjects(loss_label, loss_eq)
        self.play(
            FadeIn(loss_label, shift=RIGHT * 0.3),
            run_time=0.8,
        )
        self.play(Write(loss_eq), run_time=1.5)
        self.wait(0.6)

        # =====================================================================
        # SECTION 3:  3D surface (centred in frame, shifted right+down)
        # =====================================================================
        self.set_camera_orientation(
            phi=68 * DEGREES,
            theta=-45 * DEGREES,
            zoom=0.78,
        )

        axes = ThreeDAxes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            z_range=[0, 10, 2],
            x_length=6.5,
            y_length=6.5,
            z_length=4.5,
            axis_config={
                "color": GREY_B,
                "stroke_width": 1.5,
                "include_tip": True,
                "tip_length": 0.15,
            },
        )
        # Shift graph right and down to centre it in the vertical frame
        axes.shift(DOWN * 1.5 + RIGHT * 0.5)

        # Axis labels
        x_lbl = axes.get_x_axis_label(Tex("w", font_size=34), edge=RIGHT, direction=RIGHT)
        y_lbl = axes.get_y_axis_label(Tex("b", font_size=34), edge=UP, direction=UP)
        z_lbl = Tex("L", font_size=34, color=WHITE).next_to(axes.z_axis.get_end(), UP, buff=0.15)

        surface = Surface(
            lambda u, v: axes.c2p(u, v, self.loss(u, v)),
            u_range=[-2.5, 2.5],
            v_range=[-2.5, 2.5],
            resolution=(32, 32),
            fill_opacity=0.88,
            stroke_color=self.COL_WIREFRAME,
            stroke_width=0.3,
            stroke_opacity=0.35,
        )
        surface.set_fill_by_value(
            axes=axes,
            colorscale=[
                ManimColor("#0A2463"),
                ManimColor("#1E6091"),
                ManimColor("#FB8B24"),
                ManimColor("#E01E37"),
            ],
            axis=2,
        )

        # Animate 3D build (smooth, not rushed)
        self.play(Create(axes), run_time=1.5)
        self.add(x_lbl, y_lbl, z_lbl)
        self.play(Create(surface), run_time=2.5, rate_func=smooth)
        self.wait(0.6)

        # =====================================================================
        # SECTION 4:  Update rule equation (2D, bottom area)
        # =====================================================================
        update_rule = MathTex(
            r"\vec{w}_{t+1}",
            r"=",
            r"\vec{w}_{t}",
            r"-",
            r"\alpha",
            r"\nabla L(\vec{w}_{t})",
            font_size=40,
            color=WHITE,
        )
        update_rule[0].set_color(self.COL_ACCENT)
        update_rule[4].set_color(YELLOW)
        update_rule[5].set_color("#FF8844")

        lr_label = MathTex(
            r"\alpha = " + str(LR),
            font_size=30,
            color=GREY_A,
        )

        step_text = Text("Step: 0", font_size=32, color=GREY_A)
        val_text = MathTex(
            r"L = {:.3f}".format(self.loss(START_X, START_Y)),
            font_size=30,
            color=GREY_A,
        )

        update_rule.move_to(np.array([0, -5.6, 0]))

        update_box = SurroundingRectangle(
            update_rule,
            color=self.COL_ACCENT,
            fill_color=self.COL_EQ_BOX,
            fill_opacity=0.7,
            buff=0.25,
            corner_radius=0.15,
            stroke_width=1.5,
        )

        lr_label.next_to(update_box, DOWN, buff=0.35)
        step_text.move_to(np.array([-1.5, -7.0, 0]))
        val_text.move_to(np.array([1.5, -7.0, 0]))

        self.add_fixed_in_frame_mobjects(update_box, update_rule, lr_label, step_text, val_text)
        self.play(
            FadeIn(update_box, shift=UP * 0.3),
            Write(update_rule),
            run_time=1.5,
        )
        self.play(
            FadeIn(lr_label, shift=UP * 0.15),
            FadeIn(step_text),
            FadeIn(val_text),
            run_time=0.8,
        )
        self.wait(0.8)

        # =====================================================================
        # SECTION 5:  Gradient descent with continuous rotation
        # =====================================================================

        path_3d = [axes.c2p(x, y, self.loss(x, y)) for x, y in path]

        ball = Sphere(radius=0.13, resolution=(12, 12))
        ball.set_color(self.COL_BALL)
        ball.set_opacity(1.0)
        ball.move_to(path_3d[0])

        # Start label
        start_lbl = Tex(r"Start", font_size=26, color=self.COL_BALL)
        start_lbl.move_to(np.array([2.5, -3.5, 0]))
        self.add_fixed_in_frame_mobjects(start_lbl)

        self.play(
            FadeIn(ball, scale=0.5),
            FadeIn(start_lbl, shift=LEFT * 0.2),
            run_time=0.8,
        )
        self.wait(0.5)
        self.play(FadeOut(start_lbl), run_time=0.4)

        # ── Start ambient rotation DURING descent ──
        self.begin_ambient_camera_rotation(rate=0.08)

        trail = VGroup()

        # Descent loop – smooth, uniform timing
        for i in range(N_STEPS):
            x_cur, y_cur = path[i]
            x_nxt, y_nxt = path[i + 1]
            z_cur = self.loss(x_cur, y_cur)
            z_nxt = self.loss(x_nxt, y_nxt)

            # Ghost trail dot
            ghost = Dot3D(
                path_3d[i],
                radius=0.055,
                color=self.COL_TRAIL,
            )
            ghost.set_opacity(0.6)
            trail.add(ghost)
            self.add(ghost)

            # Green gradient arrow
            arrow = Arrow3D(
                start=axes.c2p(x_cur, y_cur, z_cur),
                end=axes.c2p(x_nxt, y_nxt, z_nxt),
                color=GREEN_C,
                thickness=0.015,
                base_radius=0.035,
            )

            # New step / loss labels
            new_step = Text(f"Step: {i + 1}", font_size=32, color=GREY_A)
            new_step.move_to(np.array([-1.5, -7.0, 0]))
            new_val = MathTex(
                r"L = {:.3f}".format(z_nxt),
                font_size=30,
                color=GREY_A,
            )
            new_val.move_to(np.array([1.5, -7.0, 0]))
            self.add_fixed_in_frame_mobjects(new_step, new_val)

            # Smooth, uniform speed – single combined animation per step
            self.play(
                Create(arrow),
                ball.animate.move_to(path_3d[i + 1]),
                ReplacementTransform(step_text, new_step),
                ReplacementTransform(val_text, new_val),
                run_time=0.6,
                rate_func=smooth,
            )
            self.remove(arrow)

            step_text = new_step
            val_text = new_val

        # =====================================================================
        # SECTION 6:  Convergence
        # =====================================================================
        self.play(
            ball.animate.set_color(self.COL_BALL_DONE),
            run_time=0.5,
        )
        self.play(
            Flash(ball, color=self.COL_BALL_DONE, line_length=0.3, num_lines=12,
                  flash_radius=0.5),
            run_time=0.8,
        )

        # "Global Minima Achieved" – no checkmark, smaller text
        min_label = Text(
            "Global Minima Achieved",
            font="CMU Serif",
            font_size=28,
            color=self.COL_BALL_DONE,
            weight=BOLD,
        )
        min_label.move_to(np.array([0.0, -7.7, 0]))
        self.add_fixed_in_frame_mobjects(min_label)
        self.play(FadeIn(min_label, shift=UP * 0.2), run_time=1.0)

        # =====================================================================
        # SECTION 7:  Continue slow rotation to showcase surface
        # =====================================================================
        self.wait(4.0)
        self.stop_ambient_camera_rotation()
        self.wait(0.5)

        # =====================================================================
        # SECTION 8:  Elegant fade out
        # =====================================================================
        all_3d = VGroup(axes, surface, ball, trail, x_lbl, y_lbl, z_lbl)
        all_2d = VGroup(
            title, subtitle, deco_line,
            loss_label, loss_eq,
            update_box, update_rule, lr_label,
            step_text, val_text, min_label,
        )

        self.play(
            FadeOut(all_3d, shift=IN * 0.5),
            FadeOut(all_2d, shift=DOWN * 0.3),
            run_time=1.5,
            rate_func=smooth,
        )
        self.wait(0.5)
