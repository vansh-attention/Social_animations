from manim import *
import numpy as np

# ── Portrait 1080 × 1920, 9 × 16 frame ──────────────────────────────────────
config.pixel_width      = 1080
config.pixel_height     = 1920
config.frame_rate       = 30
config.frame_height     = 16          # → frame_width = 9
config.background_color = "#000000"
# ─────────────────────────────────────────────────────────────────────────────


class GradientDescent3D(ThreeDScene):

    # ── helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _gd_path(x0=2.2, y0=1.8, lr=0.22, n=12):
        pts = [(x0, y0)]
        for _ in range(n):
            x, y = pts[-1]
            pts.append((x - lr * 2 * x, y - lr * 2 * y))
        return pts

    # ── main ──────────────────────────────────────────────────────────────────
    def construct(self):
        N  = 12
        LR = 0.22
        pts = self._gd_path(n=N, lr=LR)

        # ── 3-D axes & surface ────────────────────────────────────────────────
        axes = ThreeDAxes(
            x_range=[-3, 3, 1], y_range=[-3, 3, 1], z_range=[0, 9, 3],
            x_length=7.5, y_length=7.5, z_length=5.0,       # ← bigger
            axis_config={"color": WHITE, "stroke_width": 2,
                         "include_tip": True, "tip_length": 0.2},
        )
        axes.shift(DOWN * 1.3)

        surface = Surface(
            lambda u, v: axes.c2p(u, v, u**2 + v**2),
            u_range=[-2.5, 2.5],
            v_range=[-2.5, 2.5],
            resolution=(28, 28),
            checkerboard_colors=["#005858", "#009080"],
            fill_opacity=0.90,
            stroke_color="#80FFE0",
            stroke_width=0.40,
            stroke_opacity=0.55,
        )

        # Descent path in 3-D scene coords
        path3 = [axes.c2p(x, y, x**2 + y**2) for x, y in pts]

        ball = Dot3D(path3[0], color="#FF3333", radius=0.15)

        # ── Camera position ────────────────────────────────────────────────────
        self.set_camera_orientation(
            phi   = 68 * DEGREES,
            theta = -50 * DEGREES,
            zoom  = 0.82,                                     # ← bigger
        )

        # ── Fixed 2-D overlays ─────────────────────────────────────────────────
        # Title — Tex renders in Computer Modern Roman (matches reference font)
        title = Tex(
            r"\textbf{Gradient Descent}",
            color=WHITE,
            font_size=110,
        )
        title.to_edge(UP, buff=0.45)

        # Formula  (just below title)
        formula = MathTex(
            r"\vec{p}_{n+1} = \vec{p}_n - \alpha \nabla f(\vec{p}_n)",
            font_size=44,
            color=WHITE,
        )
        formula.next_to(title, DOWN, buff=1.8)

        # Step counter block  (y ≈ -5.4 → -7.2)
        step_lbl = Text("Step:", font_size=48, color=WHITE)
        step_lbl.move_to(np.array([-0.4, -5.30, 0]))

        def make_labels(i, x, y):
            f = x**2 + y**2
            n_lbl = Text(f"{i}", font_size=48, color=WHITE)
            n_lbl.next_to(step_lbl, RIGHT, buff=0.2)
            xy_lbl = MathTex(
                rf"x = {x:+.3f},\quad y = {y:+.3f}",
                font_size=48, color=WHITE)
            xy_lbl.move_to(np.array([0.0, -6.10, 0]))
            f_lbl = MathTex(
                rf"f(x,y) = {f:.4f}",
                font_size=48, color=WHITE)
            f_lbl.move_to(np.array([0.0, -6.90, 0]))
            return n_lbl, xy_lbl, f_lbl

        n0, xy0, f0 = make_labels(0, *pts[0])

        # Register all fixed overlays
        self.add_fixed_in_frame_mobjects(title, formula, step_lbl, n0, xy0, f0)

        # ══════════════════════════════════════════════════════════════════════
        # ANIMATION SEQUENCE
        # ══════════════════════════════════════════════════════════════════════

        # 1. Title & formula fade/write in
        self.play(Write(title), run_time=1.0)
        self.play(Write(formula), run_time=0.9)
        self.wait(0.15)

        # 2. Build axes
        self.play(Create(axes), run_time=0.8)

        # 3. Grow the surface
        self.play(Create(surface), run_time=1.8)

        # 4. Appear ball + step labels
        self.play(FadeIn(ball), run_time=0.4)
        self.play(Write(step_lbl), FadeIn(n0), FadeIn(xy0), FadeIn(f0), run_time=0.6)

        # 5. Gradient-descent step loop
        n_lbl, xy_lbl, f_lbl = n0, xy0, f0

        for i in range(N):
            x_new, y_new = pts[i + 1]

            # Ghost trail dot
            ghost = Dot3D(path3[i], color="#FF7777", radius=0.07, fill_opacity=0.55)
            self.add(ghost)

            # New step labels
            nn, nxy, nf = make_labels(i + 1, x_new, y_new)
            self.add_fixed_in_frame_mobjects(nn, nxy, nf)

            self.play(
                ball.animate.move_to(path3[i + 1]),
                FadeOut(n_lbl), FadeOut(xy_lbl), FadeOut(f_lbl),
                FadeIn(nn),     FadeIn(nxy),      FadeIn(nf),
                run_time=0.40,
            )
            n_lbl, xy_lbl, f_lbl = nn, nxy, nf

        # 6. Converged indicator
        self.play(ball.animate.set_color("#00FF88"), run_time=0.5)

        min_txt = Text("✓  Global Minimum", font_size=44, color="#00FF88")
        min_txt.move_to(np.array([0.0, -7.70, 0]))
        self.add_fixed_in_frame_mobjects(min_txt)
        self.play(Write(min_txt), run_time=0.7)

        # 7. Slow ambient rotation to showcase 3-D surface
        self.begin_ambient_camera_rotation(rate=0.07)
        self.wait(3.5)
        self.stop_ambient_camera_rotation()
        self.wait(0.5)