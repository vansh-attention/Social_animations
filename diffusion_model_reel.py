"""
Diffusion models — how AI paints from pure noise.
Forward process: a pixel-art heart drowns in Gaussian noise, step by step
(real cosine noise schedule). Reverse process: starting from fresh static,
the denoising trajectory walks back until the heart re-emerges.

Vertical 1080 x 1920 Instagram Reel layout:
  - top band    : gradient title + forward-process equation
  - middle band : 16x16 pixel image cycling through real x_t samples
  - bottom band : reverse-step equation + live t / alpha-bar HUD
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


class DiffusionModelReel(Scene):
    """DDPM in miniature: x_t = sqrt(abar_t) x_0 + sqrt(1-abar_t) eps on a
    16x16 heart, cosine schedule, forward then reverse — every frame is a
    real sample from the marginal at its displayed t."""

    # ── Colour palette ────────────────────────────────────────────────────────
    COL_TITLE_A = "#38BDF8"   # sky   (gradient start)
    COL_TITLE_B = "#F472B6"   # pink  (gradient end)
    COL_SUB     = "#B0B8D0"   # soft grey-blue
    COL_PIX_BG  = "#0C0C16"   # dark pixel (value 0)
    COL_PIX_ON  = "#FB7185"   # heart pixel (value 1)
    COL_NET     = "#38BDF8"   # the denoising network eps_theta
    COL_DONE    = "#00FF88"   # finale green
    COL_EQ_BOX  = "#10102A"   # dark panel behind equations

    N = 16                    # pixel grid size
    T = 1000                  # diffusion steps (displayed)
    PIX = 0.28                # pixel spacing (square side 0.26)

    @staticmethod
    def alpha_bar(t, T):
        return float(np.cos(((t / T) + 0.008) / 1.008 * np.pi / 2) ** 2)

    def construct(self):
        # =====================================================================
        # The image + every displayed diffusion state (precomputed, real)
        # =====================================================================
        N, T = self.N, self.T
        ys_idx, xs_idx = np.mgrid[0:N, 0:N]
        hx = (xs_idx - (N - 1) / 2) / (N / 3.9)
        hy = ((N - 1) / 2 - ys_idx) / (N / 3.9) + 0.1
        x0 = (((hx ** 2 + hy ** 2 - 1) ** 3 - hx ** 2 * hy ** 3) <= 0).astype(float)

        rng = np.random.default_rng(9)
        eps_fwd = rng.normal(0, 1, (N, N))          # one fixed forward path

        fwd_ts = [0, 200, 400, 600, 800, 1000]
        rev_ts = [1000, 900, 800, 700, 600, 500, 400, 300, 200, 100, 0]

        def sample(t, eps):
            ab = self.alpha_bar(t, T)
            return np.sqrt(ab) * x0 + np.sqrt(1 - ab) * eps

        fwd_states = [(t, sample(t, eps_fwd)) for t in fwd_ts]
        rev_states = []
        for t in rev_ts:
            eps = rng.normal(0, 1, (N, N)) if t > 0 else np.zeros((N, N))
            rev_states.append((t, sample(t, eps)))

        c_lo, c_hi = ManimColor(self.COL_PIX_BG), ManimColor(self.COL_PIX_ON)

        def val_color(v):
            return interpolate_color(c_lo, c_hi, float(np.clip(v, 0.0, 1.0)))

        # =====================================================================
        # SECTION 1: Title band
        # =====================================================================
        title = Tex("Diffusion Models", font_size=76)
        title.set_color_by_gradient(self.COL_TITLE_A, self.COL_TITLE_B)
        if title.width > 8.4:
            title.scale_to_fit_width(8.4)
        subtitle = Tex(r"\textit{how AI paints from pure noise}",
                       color=self.COL_SUB, font_size=34)
        title.to_edge(UP, buff=0.6)
        subtitle.next_to(title, DOWN, buff=0.24)

        fwd_eq = MathTex(
            r"x_t", r"=", r"\sqrt{\bar\alpha_t}\,", r"x_0", r"+",
            r"\sqrt{1-\bar\alpha_t}\,", r"\varepsilon",
            font_size=34, color=WHITE,
        )
        fwd_eq[3].set_color(self.COL_PIX_ON)
        fwd_eq[6].set_color(GREY_A)
        fwd_eq.next_to(subtitle, DOWN, buff=0.36)

        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.2, rate_func=smooth)
        self.play(FadeIn(subtitle, shift=DOWN * 0.2), run_time=0.8)
        self.play(Write(fwd_eq), run_time=1.2)
        self.wait(0.3)

        # =====================================================================
        # SECTION 2: The pixel image
        # =====================================================================
        origin = np.array([-(N - 1) / 2 * self.PIX, 0.55 + (N - 1) / 2 * self.PIX, 0])
        rows = VGroup()
        squares = [[None] * N for _ in range(N)]
        for i in range(N):
            row = VGroup()
            for j in range(N):
                sq = Square(side_length=0.26, stroke_width=0,
                            fill_color=val_color(x0[i, j]), fill_opacity=1.0)
                sq.move_to(origin + np.array([j * self.PIX, -i * self.PIX, 0]))
                squares[i][j] = sq
                row.add(sq)
            rows.add(row)

        def caption(tex_str, color=None):
            c = Tex(tex_str, font_size=31, color=color or self.COL_SUB)
            if c.width > 8.3:
                c.scale_to_fit_width(8.3)
            c.move_to(np.array([0.0, -3.35, 0.0]))
            return c

        cap = caption(r"Start with an image")
        self.play(
            LaggedStart(*[FadeIn(r, shift=DOWN * 0.08) for r in rows],
                        lag_ratio=0.05),
            FadeIn(cap),
            run_time=1.3,
        )
        self.wait(0.6)

        # =====================================================================
        # SECTION 3: HUD + reverse-equation box (bottom band)
        # =====================================================================
        rev_eq = MathTex(
            r"x_{t-1}", r"=", r"\tfrac{1}{\sqrt{\alpha_t}}\!\left(",
            r"x_t", r"-", r"\tfrac{\beta_t}{\sqrt{1-\bar\alpha_t}}\,",
            r"\varepsilon_\theta(x_t, t)", r"\right)",
            font_size=30, color=WHITE,
        )
        rev_eq[6].set_color(self.COL_NET)
        rev_eq.move_to(np.array([0.0, -4.85, 0.0]))
        rev_box = SurroundingRectangle(
            rev_eq, color=self.COL_TITLE_B, fill_color=self.COL_EQ_BOX,
            fill_opacity=0.78, buff=0.26, corner_radius=0.15, stroke_width=1.5,
        )
        note = Tex(r"$\varepsilon_\theta$: a network trained to spot the noise",
                   font_size=25, color=GREY_A)
        note.next_to(rev_box, DOWN, buff=0.26)

        t_label = MathTex(r"t =", font_size=32, color=GREY_A)
        t_num = Integer(0, font_size=32, color=GREY_A)
        t_hud = VGroup(t_label, t_num).arrange(RIGHT, buff=0.15)
        t_hud.move_to(np.array([-1.7, -6.65, 0.0]))

        ab_label = MathTex(r"\bar\alpha_t =", font_size=32, color=GREY_A)
        ab_num = DecimalNumber(1.0, num_decimal_places=2,
                               font_size=32, color=GREY_A)
        ab_hud = VGroup(ab_label, ab_num).arrange(RIGHT, buff=0.15)
        ab_hud.move_to(np.array([1.7, -6.65, 0.0]))

        self.play(FadeIn(rev_box, shift=UP * 0.3), Write(rev_eq),
                  FadeIn(note), FadeIn(t_hud), FadeIn(ab_hud), run_time=1.4)
        self.wait(0.4)

        # helper: morph every pixel to a new state in one play
        def step_to(state_t, state_x, extra=(), run_time=0.5):
            anims = [squares[i][j].animate.set_fill(val_color(state_x[i, j]))
                     for i in range(N) for j in range(N)]
            anims += [ChangeDecimalToValue(t_num, state_t),
                      ChangeDecimalToValue(ab_num, self.alpha_bar(state_t, T))]
            anims += list(extra)
            self.play(*anims, run_time=run_time, rate_func=smooth)

        # =====================================================================
        # SECTION 4: Forward — drown it in noise
        # =====================================================================
        cap2 = caption(r"\textbf{Forward}: drown it in noise, step by step")
        self.play(ReplacementTransform(cap, cap2), run_time=0.5)
        cap = cap2

        for t, xt in fwd_states[1:]:
            step_to(t, xt, run_time=0.55)
            self.wait(0.12)
        self.wait(0.8)

        # =====================================================================
        # SECTION 5: Reverse — the network denoises
        # =====================================================================
        cap3 = caption(r"\textbf{Reverse}: predict the noise, subtract it, repeat",
                       self.COL_NET)
        self.play(ReplacementTransform(cap, cap3), run_time=0.6)
        cap = cap3
        self.wait(0.3)

        for k, (t, xt) in enumerate(rev_states[1:]):
            step_to(t, xt, run_time=0.42 if t > 0 else 0.8)
        self.wait(0.5)

        # =====================================================================
        # SECTION 6: Finale
        # =====================================================================
        frame = SurroundingRectangle(
            rows, color=self.COL_DONE, buff=0.18,
            corner_radius=0.12, stroke_width=2.5,
        )
        cap4 = caption(r"From pure noise --- structure", self.COL_DONE)
        self.play(Create(frame), ReplacementTransform(cap, cap4), run_time=0.9)
        cap = cap4
        self.play(Flash(rows.get_center(), color=self.COL_DONE,
                        line_length=0.35, num_lines=14, flash_radius=2.9),
                  run_time=0.9)

        done_label = Tex("This is how AI paints.", font_size=36,
                         color=self.COL_DONE)
        done_label.move_to(np.array([0.0, -7.45, 0.0]))
        self.play(FadeIn(done_label, shift=UP * 0.2), run_time=0.9)
        self.wait(2.3)

        # =====================================================================
        # SECTION 7: Fade out
        # =====================================================================
        everything = VGroup(
            title, subtitle, fwd_eq, rows, frame, cap,
            rev_box, rev_eq, note, t_hud, ab_hud, done_label,
        )
        self.play(FadeOut(everything, shift=DOWN * 0.3), run_time=1.4,
                  rate_func=smooth)
        self.wait(0.4)
