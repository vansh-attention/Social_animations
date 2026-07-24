"""
Monte Carlo in trading — the 3D equity surface.
1,000 simulated futures of a strategy, each 500 trades, stacked into a surface:
  x = trade number, y = simulation (sorted by outcome), z = account equity.
A breakeven 'waterline' plane marks $10,000; anything below it is a drawdown
valley. Best / worst / median paths are drawn as bright ridge lines.

Vertical 1080 x 1920 Instagram Reel layout (ThreeDScene):
  - top band    : gradient title + equity-recursion equation (fixed in frame)
  - middle band : rotating 3D equity surface
  - bottom band : legend + stat HUD (fixed in frame)
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


class MonteCarloTradingReel(ThreeDScene):
    """A Monte Carlo equity surface: 1,000 random-walk equity curves with a
    small positive edge, sorted by final equity into a smooth mountain fan."""

    # ── Colour palette ────────────────────────────────────────────────────────
    COL_TITLE_A = "#34D399"   # emerald (gradient start)
    COL_TITLE_B = "#22D3EE"   # cyan    (gradient end)
    COL_SUB     = "#B0B8D0"   # soft grey-blue
    COL_BEST    = "#00FF88"   # best-case ridge
    COL_WORST   = "#FF5555"   # worst-case ridge
    COL_MEDIAN  = "#FFD93D"   # median ridge
    COL_WATER   = "#3B82F6"   # breakeven waterline plane
    COL_EQ_BOX  = "#10102A"   # dark panel behind equations

    E0    = 10000.0
    NSIM  = 1000
    T     = 500
    NROWS = 44          # surface rows (sub-sampled simulations)
    NCOLS = 56          # surface columns (sub-sampled trades)

    def construct(self):
        # =====================================================================
        # Simulate 1,000 equity curves (precomputed)
        # =====================================================================
        rng = np.random.default_rng(11)
        steps = np.where(rng.random((self.NSIM, self.T)) < 0.51, 105.0, -100.0)
        eq = np.hstack([np.full((self.NSIM, 1), self.E0),
                        self.E0 + np.cumsum(steps, axis=1)])       # (NSIM, T+1)
        eq = eq[np.argsort(eq[:, -1])]                             # sort by final
        final = eq[:, -1]

        p_profit = 100 * np.mean(final > self.E0)
        med_ret = 100 * (np.median(final) / self.E0 - 1)
        best_ret = 100 * (final.max() / self.E0 - 1)
        worst_ret = 100 * (final.min() / self.E0 - 1)

        z_lo, z_hi = 2000.0, 20500.0

        # sub-sampled grid for the surface
        row_idx = np.linspace(0, self.NSIM - 1, self.NROWS).astype(int)
        col_idx = np.linspace(0, self.T, self.NCOLS).astype(int)
        Zgrid = eq[np.ix_(row_idx, col_idx)]                      # (NROWS, NCOLS)

        def Zfun(trade, rowf):
            """Bilinear equity lookup: trade∈[0,T], rowf∈[0,NROWS-1]."""
            cf = np.clip(trade / self.T * (self.NCOLS - 1), 0, self.NCOLS - 1)
            i0 = int(np.floor(cf)); i1 = min(i0 + 1, self.NCOLS - 1); tx = cf - i0
            j0 = int(np.floor(rowf)); j1 = min(j0 + 1, self.NROWS - 1); ty = rowf - j0
            top = Zgrid[j0, i0] * (1 - tx) + Zgrid[j0, i1] * tx
            bot = Zgrid[j1, i0] * (1 - tx) + Zgrid[j1, i1] * tx
            return top * (1 - ty) + bot * ty

        # =====================================================================
        # SECTION 1: Title band (fixed in frame)
        # =====================================================================
        title = Tex("Monte Carlo in Trading", font_size=62)
        title.set_color_by_gradient(self.COL_TITLE_A, self.COL_TITLE_B)
        if title.width > 8.4:
            title.scale_to_fit_width(8.4)
        subtitle = Tex(r"\textit{1,000 possible futures of one strategy}",
                       color=self.COL_SUB, font_size=32)
        title.to_edge(UP, buff=0.6)
        subtitle.next_to(title, DOWN, buff=0.22)

        eq_rule = MathTex(
            r"E_{t}", r"=", r"E_{t-1} + \mathrm{pnl}_{t}", r",\quad",
            r"\mathbb{E}[\mathrm{pnl}] > 0",
            font_size=30, color=WHITE,
        )
        eq_rule[0].set_color(self.COL_TITLE_A)
        eq_rule[4].set_color(self.COL_MEDIAN)
        eq_rule.next_to(subtitle, DOWN, buff=0.3)

        self.add_fixed_in_frame_mobjects(title, subtitle, eq_rule)
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.3, rate_func=smooth)
        self.play(FadeIn(subtitle, shift=DOWN * 0.2), run_time=0.8)
        self.play(Write(eq_rule), run_time=1.2)
        self.wait(0.3)

        # =====================================================================
        # SECTION 2: 3D axes (middle band)
        # =====================================================================
        self.set_camera_orientation(
            phi=64 * DEGREES, theta=-48 * DEGREES, zoom=0.78,
            frame_center=np.array([0.0, 0.0, 1.0]),
        )
        axes = ThreeDAxes(
            x_range=[0, self.T, 100], y_range=[0, self.NSIM, 250],
            z_range=[z_lo, z_hi, 5000],
            x_length=6.0, y_length=6.0, z_length=4.0,
            axis_config={"color": GREY_B, "stroke_width": 1.4,
                         "include_tip": True, "tip_length": 0.13},
        )

        x_lbl = axes.get_x_axis_label(Tex("Trades", font_size=28), edge=RIGHT, direction=RIGHT)
        y_lbl = axes.get_y_axis_label(Tex("Sim \\#", font_size=28), edge=UP, direction=UP)
        z_lbl = Tex("Equity", font_size=28, color=WHITE).next_to(axes.z_axis.get_end(), UP, buff=0.12)

        self.play(Create(axes), run_time=1.3)
        self.add(x_lbl, y_lbl)
        self.add_fixed_orientation_mobjects(z_lbl)
        self.wait(0.2)

        # =====================================================================
        # SECTION 3: One future first, then all of them
        # =====================================================================
        def path_line(rank, color, width=3.5, z_bump=90):
            row = eq[rank]
            pts = [axes.c2p(col_idx[k], rank / (self.NSIM - 1) * self.NSIM,
                            row[col_idx[k]] + z_bump)
                   for k in range(self.NCOLS)]
            ln = VMobject().set_points_as_corners(pts)
            ln.set_stroke(color, width=width)
            ln.set_z_index(6)
            return ln

        def caption(tex_str, color):
            c = Tex(tex_str, font_size=32, color=color)
            c.move_to(np.array([0.0, -3.15, 0.0]))
            return c

        median_line = path_line(self.NSIM // 2, self.COL_MEDIAN, width=4)
        cap1 = caption(r"One possible future$\ldots$", self.COL_MEDIAN)
        self.add_fixed_in_frame_mobjects(cap1)
        cap1.set_opacity(0.0)
        self.play(Create(median_line), cap1.animate.set_opacity(1.0), run_time=1.8)
        self.wait(0.4)

        # the full surface: 1,000 futures at once
        surface = Surface(
            lambda u, v: axes.c2p(u, v / (self.NROWS - 1) * self.NSIM, Zfun(u, v)),
            u_range=[0, self.T], v_range=[0, self.NROWS - 1],
            resolution=(self.NCOLS, self.NROWS),
            fill_opacity=0.88, stroke_color="#0B3D2E",
            stroke_width=0.4, stroke_opacity=0.35,
        )
        surface.set_fill_by_value(
            axes=axes,
            colorscale=[ManimColor("#7F1D1D"), ManimColor("#EF4444"),
                        ManimColor("#F59E0B"), ManimColor("#FDE047"),
                        ManimColor("#22C55E"), ManimColor("#10B981")],
            axis=2,
        )

        # breakeven "waterline" plane at E0
        z_shift = axes.c2p(0, 0, self.E0) - axes.c2p(0, 0, z_lo)
        water = Surface(
            lambda u, v: axes.c2p(u, v, z_lo),
            u_range=[0, self.T], v_range=[0, self.NSIM],
            resolution=(2, 2), fill_opacity=0.16, stroke_width=0,
        )
        water.set_fill(self.COL_WATER, opacity=0.16)
        water.shift(z_shift)
        water.set_z_index(-1)

        best_line = path_line(self.NSIM - 1, self.COL_BEST, width=4)
        worst_line = path_line(0, self.COL_WORST, width=4)

        cap2 = caption(r"$\ldots$but there are 1,000", self.COL_TITLE_B)
        self.add_fixed_in_frame_mobjects(cap2)
        cap2.set_opacity(0.0)
        self.play(
            Create(surface),
            FadeIn(water),
            cap1.animate.set_opacity(0.0),
            cap2.animate.set_opacity(1.0),
            run_time=2.6, rate_func=smooth,
        )
        self.remove(cap1)
        self.play(Create(best_line), Create(worst_line), run_time=1.2)
        self.wait(0.4)

        # =====================================================================
        # SECTION 4: Legend + stat HUD (bottom band, fixed in frame)
        # =====================================================================
        def legend_row(color, label):
            dot = Dot(radius=0.09, color=color)
            txt = Tex(label, font_size=26, color=WHITE)
            return VGroup(dot, txt).arrange(RIGHT, buff=0.14)

        legend = VGroup(
            legend_row(self.COL_BEST, rf"Best  +{best_ret:.0f}\%"),
            legend_row(self.COL_MEDIAN, rf"Median  +{med_ret:.0f}\%"),
            legend_row(self.COL_WORST, rf"Worst  {worst_ret:.0f}\%"),
        ).arrange(RIGHT, buff=0.5)
        legend.move_to(np.array([0.0, -4.35, 0.0]))

        stat_box = SurroundingRectangle(
            legend, color=self.COL_TITLE_B, fill_color=self.COL_EQ_BOX,
            fill_opacity=0.75, buff=0.25, corner_radius=0.15, stroke_width=1.5,
        )
        note = Tex(r"1,000 Monte Carlo runs $\;\cdot\;$ 500 trades each",
                   font_size=26, color=GREY_A)
        note.next_to(stat_box, DOWN, buff=0.28)

        pp_label = Tex("P(profit):", font_size=32, color=GREY_A)
        pp_num = Integer(0, font_size=32, color=self.COL_BEST, unit=r"\%")
        pp_hud = VGroup(pp_label, pp_num).arrange(RIGHT, buff=0.18)
        pp_hud.move_to(np.array([0.0, -6.7, 0.0]))

        self.add_fixed_in_frame_mobjects(stat_box, legend, note, pp_hud)
        self.play(FadeIn(stat_box, shift=UP * 0.3), FadeIn(legend), run_time=1.0)
        self.play(FadeIn(note), FadeIn(pp_hud), run_time=0.5)
        self.play(ChangeDecimalToValue(pp_num, int(round(p_profit))), run_time=1.0)
        # ChangeDecimalToValue regenerates the digits, dropping their
        # fixed-in-frame status — re-pin so the ambient rotation below can't
        # carry the number off-screen with the 3D world.
        self.camera.add_fixed_in_frame_mobjects(pp_num)
        self.wait(0.3)

        # =====================================================================
        # SECTION 5: Showcase rotation
        # =====================================================================
        cap3 = caption(r"Outcomes fan out as trades accumulate", self.COL_SUB)
        self.add_fixed_in_frame_mobjects(cap3)
        cap3.set_opacity(0.0)
        self.play(cap2.animate.set_opacity(0.0), cap3.animate.set_opacity(1.0),
                  run_time=0.6)
        self.remove(cap2)

        self.begin_ambient_camera_rotation(rate=0.10)
        self.wait(6.0)
        self.stop_ambient_camera_rotation()
        self.wait(0.3)

        # =====================================================================
        # SECTION 6: Fade out
        # =====================================================================
        all_3d = VGroup(axes, surface, water, best_line, worst_line,
                        median_line, x_lbl, y_lbl, z_lbl)
        all_2d = VGroup(title, subtitle, eq_rule, cap3,
                        stat_box, legend, note, pp_hud)
        self.play(FadeOut(all_3d, shift=IN * 0.4),
                  FadeOut(all_2d, shift=DOWN * 0.3),
                  run_time=1.5, rate_func=smooth)
        self.wait(0.4)
