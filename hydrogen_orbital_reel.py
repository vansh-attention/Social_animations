"""
Hydrogen orbital — the shape of an electron (3p_z, n=3, l=1, m=0).
Inspired by the glowing woven-streamline look of physics-viz reels: the
electron cloud is drawn as hundreds of cyan->magenta spiral streamlines
spun around the z-axis, over a faint field of equation "code rain".

Vertical 1080 x 1920 Instagram Reel layout (ThreeDScene):
  - top band    : gradient title + real psi_nlm wavefunction + quantum numbers
  - middle band : rotating 3D orbital woven from spiral streamlines
  - bottom band : probability density |psi|^2 + normalization integral
Lobe proportions follow the true 3p radial node: inner peak ~3a0,
outer peak ~12a0 (ratio 4:1).
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


class HydrogenOrbitalReel(ThreeDScene):
    """The 3p_z hydrogen orbital as woven spiral streamlines: an outer
    dumbbell and a smaller inner dumbbell (the 3p radial node), cyan->magenta,
    with a faint glow halo and equation code-rain backdrop."""

    # ── Colour palette ────────────────────────────────────────────────────────
    COL_TITLE_A = "#22D3EE"   # cyan   (gradient start)
    COL_TITLE_B = "#E879F9"   # magenta (gradient end)
    COL_SUB     = "#9FB3C8"   # cool grey
    COL_TOP     = "#E879F9"   # streamline top-lobe hue (magenta)
    COL_MID     = "#818CF8"   # streamline mid hue (indigo)
    COL_BOT     = "#22D3EE"   # streamline bottom-lobe hue (cyan)
    COL_GLOW    = "#5B4B8A"   # soft halo
    COL_RAIN    = "#2B3A55"   # faint code-rain text
    COL_EQ_BOX  = "#0A0F1E"   # near-black panel behind equations
    COL_ACCENT  = "#5EEAD4"   # teal equation accents (physics-viz vibe)

    A_OUT   = 2.6             # outer-lobe pole distance
    A_IN    = 0.62           # inner-lobe pole distance (real 4:1 node ratio)
    N_OUT   = 22             # outer streamlines
    N_IN    = 11             # inner streamlines
    TURNS_O = 3.5
    TURNS_I = 2.5

    # ── Streamline geometry ───────────────────────────────────────────────────
    def spiral_points(self, A, turns, phi0, n_pts=140):
        t = np.linspace(0, 1, n_pts)
        th = np.pi * t
        ph = 2 * np.pi * turns * t + phi0
        r = A * np.abs(np.cos(th))
        s = r * np.sin(th)
        return np.stack([s * np.cos(ph), s * np.sin(ph), r * np.cos(th)], axis=1)

    def make_streamline(self, A, turns, phi0):
        pts = self.spiral_points(A, turns, phi0)
        # list-color stroke = true per-point gradient along the curve
        # (set_color_by_gradient collapses to one color on a single VMobject)
        glow = VMobject().set_points_smoothly([*pts])
        glow.set_stroke(color=[self.COL_TOP, self.COL_BOT], width=9, opacity=0.14)
        core = VMobject().set_points_smoothly([*pts])
        core.set_stroke(color=[self.COL_TOP, self.COL_MID, self.COL_BOT],
                        width=2.2, opacity=0.95)
        return glow, core

    def construct(self):
        # =====================================================================
        # SECTION 1: Title band (fixed in frame)
        # =====================================================================
        title = Tex("Hydrogen Orbital", font_size=68)
        title.set_color_by_gradient(self.COL_TITLE_A, self.COL_TITLE_B)
        ver = MathTex(r"v1.0", font_size=34, color=self.COL_SUB)
        ver.next_to(title, RIGHT, buff=0.2).align_to(title, DOWN)
        titleblock = VGroup(title, ver)
        if titleblock.width > 8.5:
            titleblock.scale_to_fit_width(8.5)
        titleblock.to_edge(UP, buff=0.55)
        subtitle = Tex(r"\textit{the shape of an electron}",
                       color=self.COL_SUB, font_size=33)
        subtitle.next_to(titleblock, DOWN, buff=0.2)

        self.add_fixed_in_frame_mobjects(title, ver, subtitle)
        self.play(FadeIn(title, shift=DOWN * 0.3), FadeIn(ver, shift=DOWN * 0.3),
                  run_time=1.2, rate_func=smooth)
        self.play(FadeIn(subtitle, shift=DOWN * 0.2), run_time=0.8)

        # wavefunction + quantum numbers
        psi_eq = MathTex(
            r"\psi_{n\ell m}(r,\theta,\phi) = N_{n\ell}\,e^{-\rho/2}\,"
            r"\rho^{\ell}\,L_{n-\ell-1}^{\,2\ell+1}(\rho)\,Y_{\ell}^{m}(\theta,\phi)",
            font_size=30, color=WHITE,
        )
        psi_eq[0][0:4].set_color(self.COL_ACCENT)
        if psi_eq.width > 8.4:
            psi_eq.scale_to_fit_width(8.4)
        psi_eq.next_to(subtitle, DOWN, buff=0.34)
        rho_eq = MathTex(r"\rho = \frac{2Zr}{n a_0}", font_size=28, color=self.COL_SUB)
        rho_eq.next_to(psi_eq, DOWN, buff=0.24)
        qnums = MathTex(r"n=3,\quad \ell=1,\quad m=0",
                        font_size=32, color=self.COL_TITLE_B)
        qnums.next_to(rho_eq, DOWN, buff=0.24)

        self.add_fixed_in_frame_mobjects(psi_eq, rho_eq, qnums)
        self.play(Write(psi_eq), run_time=1.5)
        self.play(FadeIn(rho_eq), FadeIn(qnums, shift=UP * 0.1), run_time=0.8)
        self.wait(0.3)

        # =====================================================================
        # SECTION 2: Code-rain backdrop (faint, fixed in frame, behind all)
        # =====================================================================
        frags = [
            r"\psi", r"|\psi|^2", r"\hbar", r"e^{-\rho/2}", r"Y_\ell^m",
            r"\nabla^2", r"E_n", r"L^{2\ell+1}", r"\rho^\ell", r"\cos\theta",
            r"n{=}3", r"\ell{=}1", r"a_0", r"\int|\psi|^2", r"P_\ell^m",
            r"\Delta E", r"2s{+}1", r"\theta,\phi", r"Z/n",
        ]
        rng = np.random.default_rng(21)
        rain = VGroup()
        for _ in range(34):
            f = frags[rng.integers(len(frags))]
            m = MathTex(f, font_size=float(rng.uniform(17, 24)), color=self.COL_RAIN)
            m.move_to([float(rng.uniform(-4.2, 4.2)),
                       float(rng.uniform(-7.3, 3.0)), 0.0])
            m.set_opacity(float(rng.uniform(0.18, 0.42)))
            rain.add(m)
        rain.set_z_index(-10)
        self.add_fixed_in_frame_mobjects(rain)
        self.play(LaggedStart(*[FadeIn(m) for m in rain], lag_ratio=0.02),
                  run_time=1.0)

        # =====================================================================
        # SECTION 3: Build the orbital (streamlines woven in 3D)
        # =====================================================================
        self.set_camera_orientation(
            phi=68 * DEGREES, theta=-58 * DEGREES, zoom=0.72,
            frame_center=np.array([0.0, 0.0, 0.35]),
        )

        # faint coordinate axes through the cloud
        axes3 = VGroup()
        for vec in ([0, 0, 3.6], [3.4, 0, 0], [0, 3.4, 0]):
            v = np.array(vec, float)
            axes3.add(Line(-v, v, stroke_color="#2C3550", stroke_width=1.2)
                      .set_opacity(0.5))
        self.add(axes3)

        glows, cores = VGroup(), VGroup()
        for i in range(self.N_OUT):
            g, c = self.make_streamline(self.A_OUT, self.TURNS_O,
                                        2 * np.pi * i / self.N_OUT)
            glows.add(g); cores.add(c)
        for i in range(self.N_IN):
            g, c = self.make_streamline(self.A_IN, self.TURNS_I,
                                        2 * np.pi * i / self.N_IN + 0.3)
            glows.add(g); cores.add(c)

        def caption(tex_str, color=None):
            c = Tex(tex_str, font_size=31, color=color or self.COL_SUB)
            if c.width > 8.3:
                c.scale_to_fit_width(8.3)
            c.move_to(np.array([0.0, -3.75, 0.0]))
            return c

        cap = caption(r"An electron isn't a dot --- it's a standing wave")
        self.add_fixed_in_frame_mobjects(cap)
        cap.set_opacity(0.0)
        glows.set_stroke(opacity=0.0)
        self.add(glows)
        self.play(
            glows.animate.set_stroke(opacity=0.14),
            LaggedStart(*[Create(c) for c in cores], lag_ratio=0.04),
            cap.animate.set_opacity(1.0),
            run_time=3.0,
        )
        self.wait(0.4)

        # =====================================================================
        # SECTION 4: Probability density box (bottom band, fixed in frame)
        # =====================================================================
        dens_eq = MathTex(r"\rho_{n\ell m}(r,\theta,\phi)", r"=",
                          r"\lvert \psi_{n\ell m} \rvert^{2}",
                          font_size=34, color=WHITE)
        dens_eq[0].set_color(self.COL_ACCENT)
        dens_eq.move_to(np.array([0.0, -4.95, 0.0]))
        dens_box = SurroundingRectangle(
            dens_eq, color=self.COL_TITLE_B, fill_color=self.COL_EQ_BOX,
            fill_opacity=0.82, buff=0.26, corner_radius=0.15, stroke_width=1.5,
        )
        norm_eq = MathTex(
            r"\int_0^\infty\!\!\int_0^\pi\!\!\int_0^{2\pi}"
            r"\lvert\psi\rvert^2\, r^2\sin\theta\,dr\,d\theta\,d\phi = 1",
            font_size=26, color=self.COL_SUB,
        )
        if norm_eq.width > 8.2:
            norm_eq.scale_to_fit_width(8.2)
        norm_eq.next_to(dens_box, DOWN, buff=0.26)

        cap2 = caption(r"$|\psi|^2$: where the electron is likely to be",
                       self.COL_ACCENT)
        self.add_fixed_in_frame_mobjects(dens_box, dens_eq, norm_eq, cap2)
        cap2.set_opacity(0.0)
        self.play(FadeIn(dens_box, shift=UP * 0.3), Write(dens_eq), run_time=1.2)
        self.play(FadeIn(norm_eq),
                  cap.animate.set_opacity(0.0), cap2.animate.set_opacity(1.0),
                  run_time=0.7)
        self.remove(cap)

        # =====================================================================
        # SECTION 5: Orbit + reveal the two lobes
        # =====================================================================
        cap3 = caption(r"$n{=}3,\ \ell{=}1,\ m{=}0$ --- the \textbf{3p} orbital, "
                       r"two lobes split by a node", self.COL_TITLE_B)
        self.add_fixed_in_frame_mobjects(cap3)
        cap3.set_opacity(0.0)

        self.begin_ambient_camera_rotation(rate=0.11)
        self.play(cap2.animate.set_opacity(0.0), cap3.animate.set_opacity(1.0),
                  run_time=0.7)
        self.remove(cap2)
        self.wait(5.0)
        self.stop_ambient_camera_rotation()

        # =====================================================================
        # SECTION 6: Finale — a bright pulse through the cloud
        # =====================================================================
        cap4 = caption(r"The shape of an electron.", self.COL_TITLE_A)
        self.add_fixed_in_frame_mobjects(cap4)
        cap4.set_opacity(0.0)
        self.play(
            cores.animate.set_stroke(width=3.4),
            glows.animate.set_stroke(opacity=0.28, width=12),
            cap3.animate.set_opacity(0.0),
            cap4.animate.set_opacity(1.0),
            run_time=0.9,
        )
        self.remove(cap3)
        self.play(cores.animate.set_stroke(width=2.2),
                  glows.animate.set_stroke(opacity=0.14, width=9),
                  run_time=0.9)
        self.wait(2.0)

        # =====================================================================
        # SECTION 7: Fade out
        # =====================================================================
        all_3d = VGroup(glows, cores, axes3)
        all_2d = VGroup(title, ver, subtitle, psi_eq, rho_eq, qnums, rain,
                        dens_box, dens_eq, norm_eq, cap4)
        self.play(FadeOut(all_3d, shift=IN * 0.4),
                  FadeOut(all_2d, shift=DOWN * 0.3),
                  run_time=1.5, rate_func=smooth)
        self.wait(0.4)
