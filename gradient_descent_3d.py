from manim import *
import numpy as np

# Portrait dimensions for Instagram Reels
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16
config.background_color = BLACK

class CompactGradientDescent3D(ThreeDScene):
    def construct(self):
        # Camera – classic 3Blue1Brown angle
        self.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES, focal_distance=50)

        # ---------- 1. Compact 3D Graph ----------
        axes = ThreeDAxes(
            x_range=(-2.5, 2.5, 1),
            y_range=(-2.5, 2.5, 1),
            z_range=(0, 12, 3),
            x_length=5,
            y_length=5,
            z_length=4,
        )
        # Loss surface L(w,b) = w² + b²  (paraboloid)
        surface = Surface(
            lambda u, v: np.array([u, v, u**2 + v**2]),
            u_range=[-2.5, 2.5],
            v_range=[-2.5, 2.5],
            resolution=(35, 35),
        )
        surface.set_fill_by_value(axes=axes, colorscale=[BLUE, GREEN, YELLOW, RED])
        surface.set_opacity(0.85)

        # Centre the 3D plot on the screen
        plot_group = VGroup(axes, surface).shift(DOWN * 2)

        # ---------- 2. 2D Heading (top) ----------
        title = Text("Gradient Descent", font="Sans", weight=BOLD, color=WHITE)
        title.scale(1.5).to_edge(UP, buff=0.6)
        title_bg = BackgroundRectangle(title, fill_color=BLACK, fill_opacity=0.7, buff=0.2)
        title_group = VGroup(title_bg, title)

        # Loss function definition (2D, just under the title)
        loss_eq = MathTex(r"L(w,b) = w^2 + b^2", color=WHITE)
        loss_eq.scale(0.9).next_to(title, DOWN, buff=0.15)

        # ---------- 3. 2D Gradient update rule (bottom) ----------
        update_eq = MathTex(
            r"\mathbf{w}_{t+1} = \mathbf{w}_t - \eta \nabla L(\mathbf{w}_t)",
            color=WHITE
        )
        update_eq.scale(0.8).to_edge(DOWN, buff=1.2)
        update_bg = BackgroundRectangle(update_eq, fill_color=BLACK, fill_opacity=0.7, buff=0.3)
        update_group = VGroup(update_bg, update_eq)

        eta_label = MathTex(r"\eta = 0.1", color=GREY).scale(0.55)
        eta_label.next_to(update_eq, UP, buff=0.08, aligned_edge=RIGHT)

        # ---------- 4. Gradient descent walk ----------
        w, b = -2.0, -2.0              # start slightly inside the visible range
        eta = 0.1
        steps = 20                     # fewer steps because surface is smaller

        point = Sphere(radius=0.12, fill_color=RED, fill_opacity=1, resolution=(10, 10))
        start_pos = axes.c2p(w, b, w**2 + b**2)
        point.move_to(start_pos)

        trail = VGroup()

        # ---- Animate scene build ----
        self.play(FadeIn(plot_group), run_time=1.5)
        self.play(Write(title_group), Write(loss_eq))
        self.wait(0.3)
        self.play(FadeIn(update_group), FadeIn(eta_label))
        self.wait(0.5)

        self.play(FadeIn(point), run_time=0.5)

        for _ in range(steps):
            grad_w, grad_b = 2 * w, 2 * b
            w_next = w - eta * grad_w
            b_next = b - eta * grad_b
            z_next = w_next**2 + b_next**2

            # Green arrow showing the step direction (in 3D space)
            arrow = Arrow3D(
                start=axes.c2p(w, b, w**2 + b**2),
                end=axes.c2p(w_next, b_next, z_next),
                color=GREEN,
                thickness=0.02,
                base_radius=0.04,
            )
            self.play(Create(arrow), run_time=0.12)
            self.wait(0.03)

            # Move the red sphere along the arrow
            self.play(
                point.animate.move_to(axes.c2p(w_next, b_next, z_next)),
                run_time=0.2,
            )
            self.remove(arrow)

            # Leave a small yellow trail dot (3D, but looks fine)
            trail_dot = Dot3D(axes.c2p(w_next, b_next, z_next), radius=0.04, color=YELLOW)
            trail.add(trail_dot)
            self.add(trail_dot)

            w, b = w_next, b_next

        # Mark the minimum
        min_marker = Text("Global Minimum", color=YELLOW, weight=BOLD).scale(0.45)
        min_marker.next_to(point, UP, buff=0.15)    # 2D positioning near the 3D point
        self.play(FadeIn(min_marker), run_time=0.5)

        # ---- Signature 3B1B slow rotation ----
        self.begin_ambient_camera_rotation(rate=0.12)
        self.wait(4)
        self.stop_ambient_camera_rotation()
        self.wait(1)