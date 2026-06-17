"""
Support Vector Machines — the kernel trick, in 3D.
Two classes that no straight line can separate in 2D are lifted onto a
paraboloid z = x² + y², where a single flat hyperplane separates them.
Projected back down, that plane becomes a circular decision boundary.

Vertical 1080 x 1920 Instagram Reel layout:
  - top band    : gradient title + feature-map equation (fixed in frame)
  - middle band : rotating 3D lift + separating hyperplane
  - bottom band : decision-function box + morphing caption (fixed in frame)
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


class SVMKernelReel(ThreeDScene):
    """Kernel-trick SVM: φ(x,y) = (x, y, x²+y²) lifts tangled 2D classes into
    3D where they are linearly separable by a plane."""

    # ── Colour palette ────────────────────────────────────────────────────────
    COL_TITLE_A = "#5EEAD4"   # teal  (gradient start)
    COL_TITLE_B = "#818CF8"   # indigo (gradient end)
    COL_SUB     = "#B0B8D0"   # soft grey-blue
    COL_IN      = "#58C4DD"   # inner class  (label -1)
    COL_OUT     = "#FF6B6B"   # outer class  (label +1)
    COL_SV      = "#FFD93D"   # support vectors
    COL_PLANE   = "#C9B6FF"   # separating hyperplane
    COL_PARAB   = "#2E5A88"   # paraboloid surface
    COL_EQ_BOX  = "#10102A"   # dark panel behind equations

    K = 0.55                  # vertical lift scale

    def lift(self, x, y):
        return self.K * (x * x + y * y)

    # ── Scene ─────────────────────────────────────────────────────────────────
    def construct(self):
        # =====================================================================
        # Data: inner blob (class -1) wrapped by an outer ring (class +1)
        # =====================================================================
        rng = np.random.default_rng(42)
        n_in, n_out = 14, 18

        th_in = rng.uniform(0, 2 * np.pi, n_in)
        r_in = rng.uniform(0.15, 0.95, n_in)
        in_xy = np.c_[r_in * np.cos(th_in), r_in * np.sin(th_in)]

        th_out = rng.uniform(0, 2 * np.pi, n_out)
        r_out = rng.uniform(1.7, 2.45, n_out)
        out_xy = np.c_[r_out * np.cos(th_out), r_out * np.sin(th_out)]

        all_xy = np.vstack([in_xy, out_xy])
        all_z = self.lift(all_xy[:, 0], all_xy[:, 1])
        z_in_max = self.lift(in_xy[:, 0], in_xy[:, 1]).max()
        z_out_min = self.lift(out_xy[:, 0], out_xy[:, 1]).min()
        threshold = 0.5 * (z_in_max + z_out_min)
        margin = 0.5 * (z_out_min - z_in_max)
        bound_r = np.sqrt(threshold / self.K)          # 2D decision-circle radius
        sv_idx = np.argsort(np.abs(all_z - threshold))[:3]

        # =====================================================================
        # SECTION 1: Title band (gradient, no underline)
        # =====================================================================
        title = Tex("Support Vector Machines", font_size=58)
        title.set_color_by_gradient(self.COL_TITLE_A, self.COL_TITLE_B)
        if title.width > 8.4:
            title.scale_to_fit_width(8.4)
        subtitle = Tex(r"\textit{the kernel trick, visualised}",
                       color=self.COL_SUB, font_size=34)
        title.to_edge(UP, buff=0.7)
        subtitle.next_to(title, DOWN, buff=0.25)

        self.add_fixed_in_frame_mobjects(title, subtitle)
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.3, rate_func=smooth)
        self.play(FadeIn(subtitle, shift=DOWN * 0.2), run_time=0.9)
        self.wait(0.3)

        # feature-map equation (revealed once we lift)
        phi_eq = MathTex(r"\phi(x, y) = \left(x,\; y,\; x^{2}+y^{2}\right)",
                         font_size=34, color=WHITE)
        phi_eq[0][0].set_color(self.COL_TITLE_A)
        phi_eq.next_to(subtitle, DOWN, buff=0.4)

        # =====================================================================
        # SECTION 2: Bottom band — decision function box + caption
        # =====================================================================
        dec_eq = MathTex(
            r"f(\mathbf{x}) = \operatorname{sign}\!\big(",
            r"\mathbf{w}^{\top}\phi(\mathbf{x}) + b",
            r"\big)",
            font_size=34, color=WHITE,
        )
        dec_eq[1].set_color(self.COL_PLANE)
        dec_eq.move_to(np.array([0.0, -5.5, 0.0]))
        dec_box = SurroundingRectangle(
            dec_eq, color=self.COL_TITLE_B, fill_color=self.COL_EQ_BOX,
            fill_opacity=0.78, buff=0.28, corner_radius=0.15, stroke_width=1.5,
        )

        def caption(tex_str, color=None):
            c = Tex(tex_str, font_size=32, color=color or self.COL_SUB)
            c.move_to(np.array([0.0, -7.0, 0.0]))
            return c

        cap = caption(r"Two classes --- no straight line can separate them")

        # =====================================================================
        # SECTION 3: 3D axes + flat 2D data (near top-down view)
        # =====================================================================
        self.set_camera_orientation(
            phi=10 * DEGREES, theta=-90 * DEGREES, zoom=0.95,
            frame_center=np.array([0.0, 0.0, 0.55]),
        )

        axes = ThreeDAxes(
            x_range=[-3, 3, 1], y_range=[-3, 3, 1], z_range=[0, 4, 1],
            x_length=5.4, y_length=5.4, z_length=3.4,
            axis_config={"color": GREY_B, "stroke_width": 1.3,
                         "include_tip": True, "tip_length": 0.13},
        )

        in_dots = VGroup(*[Dot3D(axes.c2p(x, y, 0), radius=0.075, color=self.COL_IN)
                           for x, y in in_xy])
        out_dots = VGroup(*[Dot3D(axes.c2p(x, y, 0), radius=0.075, color=self.COL_OUT)
                            for x, y in out_xy])
        dots = list(in_dots) + list(out_dots)

        # a single failing separator drawn flat in the z=0 plane
        fail_line = Line(axes.c2p(-2.7, 1.6, 0), axes.c2p(2.7, -1.6, 0),
                         color=GREY_A, stroke_width=2.5)

        self.play(Create(axes), run_time=1.2)
        self.play(
            LaggedStart(*[FadeIn(d, scale=0.4) for d in dots], lag_ratio=0.04),
            run_time=1.6,
        )
        self.add_fixed_in_frame_mobjects(cap)
        self.play(Create(fail_line), FadeIn(cap), run_time=1.0)
        self.wait(1.2)

        # =====================================================================
        # SECTION 4: The lift — points rise onto the paraboloid
        # =====================================================================
        paraboloid = Surface(
            lambda u, v: axes.c2p(u, v, self.lift(u, v)),
            u_range=[-2.55, 2.55], v_range=[-2.55, 2.55],
            resolution=(26, 26), fill_opacity=0.18,
            stroke_color=self.COL_PARAB, stroke_width=0.6, stroke_opacity=0.4,
        )
        paraboloid.set_fill(self.COL_PARAB, opacity=0.18)

        lift_anims = [d.animate.move_to(axes.c2p(x, y, self.lift(x, y)))
                      for d, (x, y) in zip(dots, all_xy)]

        cap2 = caption(r"Lift each point up by $z = x^{2}+y^{2}$")
        self.add_fixed_in_frame_mobjects(phi_eq, cap2)
        phi_eq.set_opacity(0.0)
        cap2.set_opacity(0.0)

        self.move_camera(
            phi=62 * DEGREES, theta=-50 * DEGREES, zoom=0.82,
            frame_center=np.array([0.0, 0.0, 0.95]),
            added_anims=[
                FadeOut(fail_line),
                *lift_anims,
                FadeIn(paraboloid),
                phi_eq.animate.set_opacity(1.0),
                cap.animate.set_opacity(0.0),
                cap2.animate.set_opacity(1.0),
            ],
            run_time=3.2,
        )
        self.remove(cap, fail_line)
        self.wait(0.6)

        # =====================================================================
        # SECTION 5: Separating hyperplane rises into the gap
        # =====================================================================
        z_shift = axes.c2p(0, 0, threshold) - axes.c2p(0, 0, 0)

        def flat_plane(opacity, color):
            p = Surface(
                lambda u, v: axes.c2p(u, v, 0),
                u_range=[-2.7, 2.7], v_range=[-2.7, 2.7],
                resolution=(12, 12), fill_opacity=opacity,
                stroke_width=0,
            )
            p.set_fill(color, opacity=opacity)
            return p

        plane = flat_plane(0.42, self.COL_PLANE)
        plane.set_z_index(-1)

        cap3 = caption(r"In 3D, one flat plane separates them",
                       color=self.COL_PLANE)
        self.add(plane)
        # register the decision box as fixed-in-frame so the camera tilt
        # doesn't rotate it; FadeIn/Write below animate it up from invisible
        self.add_fixed_in_frame_mobjects(dec_box, dec_eq, cap3)
        cap3.set_opacity(0.0)
        self.play(
            plane.animate.shift(z_shift),
            cap2.animate.set_opacity(0.0),
            cap3.animate.set_opacity(1.0),
            FadeIn(dec_box, shift=UP * 0.3), Write(dec_eq),
            run_time=2.0, rate_func=smooth,
        )
        self.remove(cap2)
        self.wait(0.6)

        # =====================================================================
        # SECTION 6: Support vectors + margin
        # =====================================================================
        margin_top = flat_plane(0.12, WHITE).shift(
            axes.c2p(0, 0, threshold + margin) - axes.c2p(0, 0, 0))
        margin_bot = flat_plane(0.12, WHITE).shift(
            axes.c2p(0, 0, threshold - margin) - axes.c2p(0, 0, 0))

        sv_rings, sv_lines = VGroup(), VGroup()
        for i in sv_idx:
            x, y = all_xy[i]
            z = all_z[i]
            dots[i].set_color(self.COL_SV)
            sv_lines.add(DashedLine(
                axes.c2p(x, y, z), axes.c2p(x, y, threshold),
                color=self.COL_SV, stroke_width=2.5, dash_length=0.07))

        cap4 = caption(r"3 support vectors set the maximal margin",
                       color=self.COL_SV)
        self.add_fixed_in_frame_mobjects(cap4)
        cap4.set_opacity(0.0)
        self.play(
            *[dots[i].animate.scale(1.6) for i in sv_idx],
            FadeIn(margin_top), FadeIn(margin_bot), Create(sv_lines),
            cap3.animate.set_opacity(0.0),
            cap4.animate.set_opacity(1.0),
            run_time=1.6,
        )
        self.remove(cap3)
        self.wait(0.6)

        # showcase rotation
        self.begin_ambient_camera_rotation(rate=0.10)
        self.wait(4.0)
        self.stop_ambient_camera_rotation()

        # =====================================================================
        # SECTION 7: Bring the boundary back to 2D — a circle
        # =====================================================================
        boundary = ParametricFunction(
            lambda t: axes.c2p(bound_r * np.cos(t), bound_r * np.sin(t), 0),
            t_range=[0, 2 * np.pi], color=self.COL_SV, stroke_width=5,
        )
        cap5 = caption(r"Back in 2D, the boundary is a circle",
                       color=self.COL_SV)
        self.add_fixed_in_frame_mobjects(cap5)
        cap5.set_opacity(0.0)
        self.move_camera(
            phi=16 * DEGREES, theta=-90 * DEGREES, zoom=0.95,
            frame_center=np.array([0.0, 0.0, 0.55]),
            added_anims=[
                FadeOut(plane), FadeOut(margin_top), FadeOut(margin_bot),
                FadeOut(sv_lines), FadeOut(paraboloid),
                *[d.animate.move_to(axes.c2p(x, y, 0))
                  for d, (x, y) in zip(dots, all_xy)],
                cap4.animate.set_opacity(0.0),
            ],
            run_time=3.0,
        )
        self.remove(cap4)
        self.play(Create(boundary), FadeIn(cap5), run_time=1.4)
        self.wait(2.2)

        # =====================================================================
        # SECTION 8: Fade out
        # =====================================================================
        self.play(
            FadeOut(VGroup(axes, in_dots, out_dots, boundary), shift=IN * 0.4),
            FadeOut(VGroup(title, subtitle, phi_eq, dec_box, dec_eq, cap5),
                    shift=DOWN * 0.3),
            run_time=1.5, rate_func=smooth,
        )
        self.wait(0.4)
