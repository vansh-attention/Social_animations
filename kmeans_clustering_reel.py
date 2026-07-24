"""
K-means clustering — Lloyd's algorithm, step by step.
Points are repeatedly (1) assigned to the nearest centroid, then (2) each
centroid hops to the mean of its assigned points, until nothing moves.

Vertical 1080 x 1920 Instagram Reel layout:
  - top band    : gradient title + objective (inertia) equation
  - middle band : 2D scatter, recolouring points + migrating centroids
  - bottom band : centroid-update rule + live iteration / inertia HUD
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


class KMeansClusteringReel(Scene):
    """K = 3 Lloyd iterations on three Gaussian blobs, from a deliberately
    lopsided start (all points grabbed by one centroid) to balanced clusters."""

    # ── Colour palette ────────────────────────────────────────────────────────
    COL_TITLE_A = "#2DD4BF"   # teal  (gradient start)
    COL_TITLE_B = "#A3E635"   # lime  (gradient end)
    COL_SUB     = "#B0B8D0"   # soft grey-blue
    COL_UNASS   = "#9AA0A8"   # unassigned points (grey)
    COL_DONE    = "#00FF88"   # convergence green
    COL_EQ_BOX  = "#10102A"   # dark panel behind equations
    CLUSTER     = ["#60A5FA", "#FF6B6B", "#C084FC"]   # blue / coral / purple

    K = 3

    def construct(self):
        # =====================================================================
        # Data + Lloyd's-algorithm trace (precomputed)
        # =====================================================================
        rng = np.random.default_rng(2)
        centers = np.array([(-1.9, 1.5), (2.0, 1.7), (0.2, -1.9)])
        pts = np.vstack([c + rng.normal(0, 0.55, (14, 2)) for c in centers])

        cent = np.array([(-2.6, -2.2), (2.6, -2.4), (0.0, 2.7)], float)
        cent_hist = [cent.copy()]
        label_hist, inertia_hist = [], []
        for _ in range(9):
            d = np.linalg.norm(pts[:, None, :] - cent[None, :, :], axis=2)
            labels = d.argmin(1)
            inertia_hist.append(float((d.min(1) ** 2).sum()))
            label_hist.append(labels)
            new_cent = np.array([
                pts[labels == k].mean(0) if (labels == k).any() else cent[k]
                for k in range(self.K)
            ])
            moved = np.linalg.norm(new_cent - cent)
            cent = new_cent
            cent_hist.append(cent.copy())
            if moved < 0.05:
                break
        n_iter = len(label_hist)

        # =====================================================================
        # SECTION 1: Title band (gradient teal→lime, no underline)
        # =====================================================================
        title = Tex("K-Means Clustering", font_size=74)
        title.set_color_by_gradient(self.COL_TITLE_A, self.COL_TITLE_B)
        if title.width > 8.4:
            title.scale_to_fit_width(8.4)
        subtitle = Tex(r"\textit{grouping data without labels}",
                       color=self.COL_SUB, font_size=34)
        title.to_edge(UP, buff=0.6)
        subtitle.next_to(title, DOWN, buff=0.25)

        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.3, rate_func=smooth)
        self.play(FadeIn(subtitle, shift=DOWN * 0.2), run_time=0.9)
        self.wait(0.3)

        # objective: within-cluster sum of squares (inertia)
        obj_eq = MathTex(
            r"J = \sum_{k=1}^{K}\;\sum_{\mathbf{x}\in C_k}",
            r"\lVert \mathbf{x} - \boldsymbol{\mu}_k \rVert^{2}",
            font_size=34, color=WHITE,
        )
        obj_eq[0][0].set_color(self.COL_TITLE_B)
        obj_eq.next_to(subtitle, DOWN, buff=0.42)
        self.play(Write(obj_eq), run_time=1.5)
        self.wait(0.3)

        # =====================================================================
        # SECTION 2: Scatter plane + data (middle band)
        # =====================================================================
        plane = NumberPlane(
            x_range=[-4, 4, 1], y_range=[-4, 4, 1],
            x_length=6.2, y_length=6.2,
            background_line_style={"stroke_color": "#2A3340",
                                   "stroke_width": 1, "stroke_opacity": 0.6},
            axis_config={"stroke_color": GREY_D, "stroke_width": 1.5},
        )
        plane.move_to(np.array([0.0, 0.45, 0.0]))

        dots = VGroup(*[Dot(plane.c2p(x, y), radius=0.072, color=self.COL_UNASS,
                            fill_opacity=0.95)
                        for x, y in pts])

        def make_centroid(pos, color):
            ring = Dot(pos, radius=0.17, color=color).set_stroke(WHITE, width=3)
            core = Dot(pos, radius=0.05, color=WHITE)
            g = VGroup(ring, core)
            g.set_z_index(5)
            return g

        centroids = [make_centroid(plane.c2p(*cent_hist[0][k]), self.CLUSTER[k])
                     for k in range(self.K)]

        self.play(Create(plane), run_time=1.1)
        self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in dots],
                              lag_ratio=0.03), run_time=1.5)
        self.play(LaggedStart(*[GrowFromCenter(c) for c in centroids],
                              lag_ratio=0.2), run_time=1.0)
        self.wait(0.3)

        # =====================================================================
        # SECTION 3: Centroid-update rule + HUD (bottom band)
        # =====================================================================
        update_rule = MathTex(
            r"\boldsymbol{\mu}_k",
            r"=",
            r"\frac{1}{|C_k|}\sum_{\mathbf{x}\in C_k}\mathbf{x}",
            font_size=38, color=WHITE,
        )
        update_rule[0].set_color(self.COL_TITLE_A)
        update_rule.move_to(np.array([0.0, -4.7, 0.0]))

        update_box = SurroundingRectangle(
            update_rule, color=self.COL_TITLE_B, fill_color=self.COL_EQ_BOX,
            fill_opacity=0.78, buff=0.28, corner_radius=0.15, stroke_width=1.5,
        )
        k_note = MathTex(r"K = 3", font_size=28, color=GREY_A)
        k_note.next_to(update_box, DOWN, buff=0.28)

        iter_label = Tex("Iter:", font_size=32, color=GREY_A)
        iter_num = Integer(0, font_size=32, color=GREY_A)
        iter_hud = VGroup(iter_label, iter_num).arrange(RIGHT, buff=0.15)
        iter_hud.move_to(np.array([-1.6, -6.6, 0.0]))

        j_label = MathTex(r"J =", font_size=32, color=GREY_A)
        j_num = DecimalNumber(inertia_hist[0], num_decimal_places=1,
                              font_size=32, color=GREY_A)
        j_hud = VGroup(j_label, j_num).arrange(RIGHT, buff=0.15)
        j_hud.move_to(np.array([1.6, -6.6, 0.0]))

        self.play(FadeIn(update_box, shift=UP * 0.3), Write(update_rule), run_time=1.4)
        self.play(FadeIn(k_note), FadeIn(iter_hud), FadeIn(j_hud), run_time=0.6)
        self.wait(0.5)

        # =====================================================================
        # SECTION 4: Lloyd iterations — assign, then move
        # =====================================================================
        trail = VGroup()
        for it in range(n_iter):
            labels = label_hist[it]

            # — assignment step: recolour each point by its nearest centroid —
            self.play(
                *[dots[i].animate.set_color(self.CLUSTER[labels[i]])
                  for i in range(len(dots))],
                ChangeDecimalToValue(j_num, inertia_hist[it]),
                ChangeDecimalToValue(iter_num, it + 1),
                run_time=0.6, rate_func=smooth,
            )

            # — update step: each centroid hops to its cluster mean —
            moves = []
            for k in range(self.K):
                old = plane.c2p(*cent_hist[it][k])
                new = plane.c2p(*cent_hist[it + 1][k])
                if np.linalg.norm(np.array(new) - np.array(old)) > 1e-3:
                    ghost = Dot(old, radius=0.05, color=self.CLUSTER[k],
                                fill_opacity=0.35)
                    trail.add(ghost)
                    self.add(ghost)
                    moves.append(centroids[k].animate.move_to(new))
            if moves:
                self.play(*moves, run_time=0.7, rate_func=smooth)

        # =====================================================================
        # SECTION 5: Convergence
        # =====================================================================
        self.play(
            *[Flash(c.get_center(), color=self.COL_DONE, line_length=0.25,
                    num_lines=10, flash_radius=0.4) for c in centroids],
            run_time=0.9,
        )
        done_label = Tex("Clusters Converged", font_size=36, color=self.COL_DONE)
        done_label.move_to(np.array([0.0, -7.4, 0.0]))
        self.play(FadeIn(done_label, shift=UP * 0.2), run_time=1.0)
        self.wait(2.4)

        # =====================================================================
        # SECTION 6: Fade out
        # =====================================================================
        everything = VGroup(
            title, subtitle, obj_eq,
            plane, dots, *centroids, trail,
            update_box, update_rule, k_note, iter_hud, j_hud, done_label,
        )
        self.play(FadeOut(everything, shift=DOWN * 0.3), run_time=1.4, rate_func=smooth)
        self.wait(0.4)
