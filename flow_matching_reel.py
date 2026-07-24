"""
Flow Matching — how modern AI turns noise into data.
Time is the vertical axis: a Gaussian noise cloud sits at the bottom (t=0),
a structured ring of data at the top (t=1). Samples ride glowing straight-line
trajectories x_t = (1-t)x_0 + t x_1 up the learned velocity field v_theta,
combing pure noise into structure.

Vertical 1080 x 1920 Instagram Reel layout (ThreeDScene):
  - top band    : gradient title + flow ODE dx/dt = v_theta(x,t)
  - middle band : noise cloud -> glowing flow -> data ring (camera orbits)
  - bottom band : conditional flow-matching loss + live t HUD
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


class FlowMatchingReel(ThreeDScene):
    """Rectified / OT conditional flow matching: N(0,I) at the bottom is
    transported along straight glowing trajectories (z = time) into a data
    ring at the top; a batch of sample dots then rides the flow up."""

    # ── Colour palette ────────────────────────────────────────────────────────
    COL_TITLE_A = "#3B82F6"   # blue  (gradient start — "cold" noise)
    COL_TITLE_B = "#F472B6"   # pink  (gradient end   — "warm" data)
    COL_SUB     = "#9FB3C8"   # cool grey
    COL_NOISE   = "#7DD3FC"   # noise-end streamline / dot (cold blue)
    COL_DATA    = "#F472B6"   # data-end streamline / dot (warm pink)
    COL_MID     = "#818CF8"   # streamline mid (indigo)
    COL_GLOW    = "#3F3A6E"   # soft halo
    COL_FIELD   = "#5EEAD4"   # velocity-field accent (teal)
    COL_RAIN    = "#243049"   # faint code-rain text
    COL_EQ_BOX  = "#0A0F1E"   # near-black panel

    N      = 130              # samples
    H      = 3.9              # vertical extent (t: 0 -> 1 maps to z: -H/2 -> H/2)
    R_RING = 2.15             # data-ring radius

    def construct(self):
        # =====================================================================
        # Source (noise), target (ring), straight-line trajectories (precomputed)
        # =====================================================================
        rng = np.random.default_rng(3)
        N = self.N
        x0 = rng.normal(0, 0.55, (N, 2))                       # noise ~ N(0,I)
        ang = np.arctan2(x0[:, 1], x0[:, 0])                   # radial coupling
        rr = self.R_RING + rng.normal(0, 0.09, N)
        x1 = np.c_[rr * np.cos(ang), rr * np.sin(ang)]         # data ring
        v = x1 - x0                                            # conditional target velocity

        def pos(i, t):
            xy = (1 - t) * x0[i] + t * x1[i]
            return np.array([xy[0], xy[1], (t - 0.5) * self.H])

        # =====================================================================
        # SECTION 1: Title band (fixed in frame)
        # =====================================================================
        title = Tex("Flow Matching", font_size=76)
        title.set_color_by_gradient(self.COL_TITLE_A, self.COL_TITLE_B)
        if title.width > 8.4:
            title.scale_to_fit_width(8.4)
        subtitle = Tex(r"\textit{how AI turns noise into data}",
                       color=self.COL_SUB, font_size=34)
        title.to_edge(UP, buff=0.55)
        subtitle.next_to(title, DOWN, buff=0.22)

        ode_eq = MathTex(r"\frac{dx}{dt}", r"=", r"v_\theta(x, t)",
                         font_size=40, color=WHITE)
        ode_eq[2].set_color(self.COL_FIELD)
        ode_eq.next_to(subtitle, DOWN, buff=0.34)

        # register each fixed-in-frame mobject right before its OWN animation:
        # add_fixed_in_frame_mobjects shows a mobject at full opacity the
        # instant it is called, so adding all three up front makes the subtitle
        # and equation appear before the title has finished fading in.
        self.add_fixed_in_frame_mobjects(title)
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.2, rate_func=smooth)
        self.add_fixed_in_frame_mobjects(subtitle)
        self.play(FadeIn(subtitle, shift=DOWN * 0.2), run_time=0.8)
        self.add_fixed_in_frame_mobjects(ode_eq)
        self.play(Write(ode_eq), run_time=1.1)
        self.wait(0.3)

        # faint code-rain backdrop
        frags = [r"v_\theta", r"x_t", r"\nabla", r"\mathcal{N}(0,I)", r"dx/dt",
                 r"x_1{-}x_0", r"t", r"\int v\,dt", r"p_t(x)", r"\theta"]
        rrng = np.random.default_rng(14)
        rain = VGroup()
        for _ in range(26):
            m = MathTex(frags[rrng.integers(len(frags))],
                        font_size=float(rrng.uniform(17, 23)), color=self.COL_RAIN)
            m.move_to([float(rrng.uniform(-4.2, 4.2)),
                       float(rrng.uniform(-7.2, 2.6)), 0.0])
            m.set_opacity(float(rrng.uniform(0.2, 0.4)))
            rain.add(m)
        rain.set_z_index(-10)
        self.add_fixed_in_frame_mobjects(rain)
        self.play(LaggedStart(*[FadeIn(m) for m in rain], lag_ratio=0.02),
                  run_time=0.9)

        # =====================================================================
        # SECTION 2: The noise cloud at the bottom
        # =====================================================================
        self.set_camera_orientation(
            phi=66 * DEGREES, theta=-52 * DEGREES, zoom=0.78,
            frame_center=np.array([0.0, 0.0, 0.25]),
        )
        # faint vertical time-axis + base/top rings for orientation
        t_axis = Line(np.array([0, 0, -self.H / 2 - 0.3]),
                      np.array([0, 0, self.H / 2 + 0.3]),
                      stroke_color="#2C3550", stroke_width=1.2).set_opacity(0.6)
        self.add(t_axis)

        dots = VGroup(*[
            Dot(point=pos(i, 0.0), radius=0.05, color=self.COL_NOISE,
                fill_opacity=0.95)
            for i in range(N)
        ])

        def caption(tex_str, color=None):
            c = Tex(tex_str, font_size=31, color=color or self.COL_SUB)
            if c.width > 8.3:
                c.scale_to_fit_width(8.3)
            c.move_to(np.array([0.0, -3.75, 0.0]))
            return c

        cap = caption(r"Start with pure noise $\sim \mathcal{N}(0, I)$",
                      self.COL_NOISE)
        self.add_fixed_in_frame_mobjects(cap)
        cap.set_opacity(0.0)
        self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in dots],
                              lag_ratio=0.015),
                  cap.animate.set_opacity(1.0), run_time=1.6)
        self.wait(0.5)

        # =====================================================================
        # SECTION 3: The learned flow — glowing streamlines rise
        # =====================================================================
        glows, cores = VGroup(), VGroup()
        for i in range(N):
            pts = [pos(i, t) for t in np.linspace(0, 1, 14)]
            glow = VMobject().set_points_smoothly(pts)
            glow.set_stroke(color=[self.COL_NOISE, self.COL_DATA],
                            width=7, opacity=0.0)
            core = VMobject().set_points_smoothly(pts)
            core.set_stroke(color=[self.COL_NOISE, self.COL_MID, self.COL_DATA],
                            width=1.9, opacity=0.9)
            glows.add(glow); cores.add(core)

        cap2 = caption(r"A network learns the velocity field $v_\theta(x,t)$",
                       self.COL_FIELD)
        self.add_fixed_in_frame_mobjects(cap2)
        cap2.set_opacity(0.0)
        self.add(glows)
        self.play(
            glows.animate.set_stroke(opacity=0.13),
            LaggedStart(*[Create(c) for c in cores], lag_ratio=0.015),
            cap.animate.set_opacity(0.0),
            cap2.animate.set_opacity(1.0),
            run_time=2.8,
        )
        self.remove(cap)
        self.wait(0.4)

        # =====================================================================
        # SECTION 4: Loss box + t HUD (bottom band, fixed in frame)
        # =====================================================================
        loss_eq = MathTex(
            r"\mathcal{L}", r"=", r"\mathbb{E}\,\big\|\,",
            r"v_\theta(x_t, t)", r"-", r"(x_1 - x_0)", r"\,\big\|^2",
            font_size=30, color=WHITE,
        )
        loss_eq[0].set_color(self.COL_DATA)
        loss_eq[3].set_color(self.COL_FIELD)
        loss_eq.move_to(np.array([0.0, -4.95, 0.0]))
        loss_box = SurroundingRectangle(
            loss_eq, color=self.COL_TITLE_B, fill_color=self.COL_EQ_BOX,
            fill_opacity=0.82, buff=0.26, corner_radius=0.15, stroke_width=1.5,
        )
        note = MathTex(r"x_t = (1-t)\,x_0 + t\,x_1",
                       font_size=26, color=GREY_A)
        note.next_to(loss_box, DOWN, buff=0.26)

        t_label = MathTex(r"t =", font_size=32, color=GREY_A)
        t_num = DecimalNumber(0.0, num_decimal_places=2, font_size=32, color=GREY_A)
        t_hud = VGroup(t_label, t_num).arrange(RIGHT, buff=0.15)
        t_hud.move_to(np.array([0.0, -6.7, 0.0]))

        self.add_fixed_in_frame_mobjects(loss_box, loss_eq, note, t_hud)
        self.play(FadeIn(loss_box, shift=UP * 0.3), Write(loss_eq),
                  FadeIn(note), FadeIn(t_hud), run_time=1.3)
        self.wait(0.3)

        # =====================================================================
        # SECTION 5: Sampling — the noise rides the flow up into data
        # =====================================================================
        cap3 = caption(r"Integrate the ODE: noise flows into data",
                       self.COL_DATA)
        self.add_fixed_in_frame_mobjects(cap3)
        cap3.set_opacity(0.0)

        # Drive t via a tracker + updater that re-pins the number EVERY frame.
        # ChangeDecimalToValue regenerates the digits each frame, dropping the
        # fixed-in-frame pin, so a post-hoc re-pin lets it drift into the 3D
        # world mid-animation; the updater re-pins continuously.
        t_track = ValueTracker(0.0)

        def _pin_t(m):
            m.set_value(t_track.get_value())
            m.next_to(t_label, RIGHT, buff=0.15)
            self.camera.add_fixed_in_frame_mobjects(m)

        t_num.add_updater(_pin_t)

        self.begin_ambient_camera_rotation(rate=0.06)
        self.play(
            LaggedStart(*[dot.animate.move_to(pos(i, 1.0)).set_color(self.COL_DATA)
                          for i, dot in enumerate(dots)], lag_ratio=0.004),
            t_track.animate.set_value(1.0),
            cap2.animate.set_opacity(0.0),
            cap3.animate.set_opacity(1.0),
            run_time=3.2, rate_func=smooth,
        )
        self.remove(cap2)
        t_num.clear_updaters()
        self.camera.add_fixed_in_frame_mobjects(t_num)
        self.wait(0.3)

        # highlight the formed data ring
        cap4 = caption(r"Structured data --- from noise, in one flow",
                       self.COL_TITLE_B)
        self.add_fixed_in_frame_mobjects(cap4)
        cap4.set_opacity(0.0)
        self.play(
            dots.animate.set(width=0.13),
            glows.animate.set_stroke(opacity=0.22),
            cap3.animate.set_opacity(0.0), cap4.animate.set_opacity(1.0),
            run_time=0.9,
        )
        self.remove(cap3)
        self.wait(3.4)
        self.stop_ambient_camera_rotation()

        # =====================================================================
        # SECTION 6: Finale
        # =====================================================================
        done_label = Tex("This is how AI generates.", font_size=36,
                         color=self.COL_TITLE_B)
        done_label.move_to(np.array([0.0, -7.45, 0.0]))
        self.add_fixed_in_frame_mobjects(done_label)
        done_label.set_opacity(0.0)
        self.play(done_label.animate.set_opacity(1.0),
                  cores.animate.set_stroke(width=2.6), run_time=0.9)
        self.wait(2.0)

        # =====================================================================
        # SECTION 7: Fade out
        # =====================================================================
        all_3d = VGroup(glows, cores, dots, t_axis)
        all_2d = VGroup(title, subtitle, ode_eq, rain, loss_box, loss_eq,
                        note, t_hud, cap4, done_label)
        self.play(FadeOut(all_3d, shift=IN * 0.4),
                  FadeOut(all_2d, shift=DOWN * 0.3),
                  run_time=1.5, rate_func=smooth)
        self.wait(0.4)
