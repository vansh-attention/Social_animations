"""
Attention — the mechanism inside every Transformer (and ChatGPT).
Six tokens attend to each other: glowing arcs show one token's attention
weights, then the full softmax(QKᵀ) matrix rises as a 3D bar city that the
camera orbits while it morphs between two heads.

Vertical 1080 x 1920 Instagram Reel layout (ThreeDScene):
  - top band    : gradient title + Attention(Q,K,V) equation + token pills
  - arc band    : attention arcs from the focus token (2D, fixed in frame)
  - middle band : 3D attention-matrix bar city (camera swoop + orbit)
  - bottom band : softmax weight formula + head / focus HUD
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


class AttentionReel(ThreeDScene):
    """Self-attention over 'The cat sat on the mat': real softmax weights,
    a dependency-arc view for the focus token, and the full matrix as an
    orbiting 3D bar city morphing between two engineered heads."""

    # ── Colour palette ────────────────────────────────────────────────────────
    COL_TITLE_A = "#E879F9"   # fuchsia (gradient start)
    COL_TITLE_B = "#22D3EE"   # cyan    (gradient end)
    COL_SUB     = "#B0B8D0"   # soft grey-blue
    COL_BAR_LO  = "#312E81"   # low attention weight (indigo)
    COL_BAR_HI  = "#F0ABFC"   # high attention weight (light fuchsia)
    COL_DONE    = "#00FF88"   # finale green
    COL_EQ_BOX  = "#10102A"   # dark panel behind equations
    TOKEN_COLS  = ["#60A5FA", "#F472B6", "#FBBF24",
                   "#34D399", "#A78BFA", "#FB7185"]

    WORDS = ["The", "cat", "sat", "on", "the", "mat"]
    FOCUS = 2                 # "sat"

    GRID = 0.7                # bar-city grid spacing
    BAR_W = 0.34              # bar footprint
    H_SCALE = 2.4             # bar height per unit weight

    @staticmethod
    def softmax_rows(m):
        e = np.exp(m - m.max(axis=1, keepdims=True))
        return e / e.sum(axis=1, keepdims=True)

    def construct(self):
        n = len(self.WORDS)

        # =====================================================================
        # Attention weights: two engineered heads, real softmax
        # =====================================================================
        rng = np.random.default_rng(4)
        base = rng.normal(0.0, 0.35, (n, n))

        s1 = base.copy()                       # head 1: look at previous token
        s1[0, 0] += 2.4
        for i in range(1, n):
            s1[i, i - 1] += 2.6
        A1 = self.softmax_rows(s1)

        s2 = base.copy() + np.eye(n) * 0.8     # head 2: syntax links
        for i, j, w in [(2, 1, 2.8), (2, 5, 2.0), (1, 0, 1.8), (0, 1, 1.8),
                        (5, 4, 2.4), (4, 5, 1.8), (3, 5, 2.2)]:
            s2[i, j] += w
        A2 = self.softmax_rows(s2)

        # =====================================================================
        # SECTION 1: Title band (fixed in frame)
        # =====================================================================
        title = Tex("Attention", font_size=80)
        title.set_color_by_gradient(self.COL_TITLE_A, self.COL_TITLE_B)
        subtitle = Tex(r"\textit{the mechanism inside ChatGPT}",
                       color=self.COL_SUB, font_size=34)
        title.to_edge(UP, buff=0.55)
        subtitle.next_to(title, DOWN, buff=0.22)

        attn_eq = MathTex(
            r"\mathrm{Attention}(Q, K, V)", r"=",
            r"\mathrm{softmax}\!\left(\frac{QK^{\top}}{\sqrt{d_k}}\right)", r"V",
            font_size=30, color=WHITE,
        )
        attn_eq[0].set_color(self.COL_TITLE_A)
        attn_eq[3].set_color(self.COL_TITLE_B)
        attn_eq.next_to(subtitle, DOWN, buff=0.32)

        self.add_fixed_in_frame_mobjects(title, subtitle, attn_eq)
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.2, rate_func=smooth)
        self.play(FadeIn(subtitle, shift=DOWN * 0.2), run_time=0.8)
        self.play(Write(attn_eq), run_time=1.4)
        self.wait(0.3)

        # =====================================================================
        # SECTION 2: Token pills (fixed in frame)
        # =====================================================================
        pills = VGroup()
        for w, c in zip(self.WORDS, self.TOKEN_COLS):
            txt = Tex(w, font_size=30, color=WHITE)
            box = RoundedRectangle(
                width=txt.width + 0.38, height=0.6, corner_radius=0.16,
                fill_color=self.COL_EQ_BOX, fill_opacity=0.92,
                stroke_color=c, stroke_width=2.2,
            )
            txt.move_to(box.get_center())
            pills.add(VGroup(box, txt))
        pills.arrange(RIGHT, buff=0.22)
        pills.move_to(np.array([0.0, 3.95, 0.0]))

        def caption(tex_str, color=None):
            c = Tex(tex_str, font_size=31, color=color or self.COL_SUB)
            if c.width > 8.3:
                c.scale_to_fit_width(8.3)
            c.move_to(np.array([0.0, -3.55, 0.0]))
            return c

        cap1 = caption(r"Six tokens enter the layer")
        self.add_fixed_in_frame_mobjects(pills, cap1)
        cap1.set_opacity(0.0)
        self.play(
            LaggedStart(*[FadeIn(p, shift=DOWN * 0.2, scale=0.8) for p in pills],
                        lag_ratio=0.12),
            cap1.animate.set_opacity(1.0),
            run_time=1.4,
        )
        self.wait(0.5)

        # =====================================================================
        # SECTION 3: The focus token attends — weighted arcs
        # =====================================================================
        focus_pill = pills[self.FOCUS]
        w_row = A2[self.FOCUS]

        arcs = VGroup()
        for j in range(n):
            if j == self.FOCUS:
                continue
            a, b = focus_pill[0].get_bottom(), pills[j][0].get_bottom()
            sgn = 1 if b[0] > a[0] else -1
            arc = ArcBetweenPoints(a, b, angle=sgn * 1.05)
            arc.set_stroke(self.TOKEN_COLS[j],
                           width=1.5 + 11.0 * w_row[j],
                           opacity=0.35 + 0.6 * float(w_row[j] / w_row.max()))
            arcs.add(arc)

        # weight labels on the two strongest links
        top2 = [j for j in np.argsort(w_row)[::-1] if j != self.FOCUS][:2]
        wlabels = VGroup()
        for j in top2:
            lbl = Tex(f"{w_row[j]:.2f}", font_size=24, color=self.TOKEN_COLS[j])
            arc_for_j = arcs[j if j < self.FOCUS else j - 1]
            lbl.next_to(arc_for_j.point_from_proportion(0.5), DOWN, buff=0.08)
            wlabels.add(lbl)

        cap2 = caption(r"``sat'' looks at every other token --- "
                       r"softmax decides how much", self.COL_SUB)
        self.add_fixed_in_frame_mobjects(arcs, wlabels, cap2)
        arcs.set_opacity(0.0)
        for m in (*wlabels, cap2):
            m.set_opacity(0.0)

        self.play(Indicate(focus_pill, color=self.TOKEN_COLS[self.FOCUS],
                           scale_factor=1.12), run_time=0.7)
        self.play(
            *[arcs[k].animate.set_stroke(opacity=0.35 + 0.6 * float(
                w_row[j] / w_row.max()))
              for k, j in enumerate([j for j in range(n) if j != self.FOCUS])],
            *[l.animate.set_opacity(1.0) for l in wlabels],
            cap1.animate.set_opacity(0.0),
            cap2.animate.set_opacity(1.0),
            run_time=1.5,
        )
        self.remove(cap1)
        self.wait(1.0)

        # =====================================================================
        # SECTION 4: The full matrix as a 3D bar city
        # =====================================================================
        self.set_camera_orientation(
            phi=14 * DEGREES, theta=-90 * DEGREES, zoom=0.8,
            frame_center=np.array([0.0, 0.0, 0.95]),
        )

        def grid_pos(i, j):
            return np.array([(j - (n - 1) / 2) * self.GRID,
                             ((n - 1) / 2 - i) * self.GRID, 0.0])

        def make_bar(i, j, w):
            h = max(float(w) * self.H_SCALE, 0.02)
            bar = Prism(dimensions=[self.BAR_W, self.BAR_W, h])
            col = interpolate_color(ManimColor(self.COL_BAR_LO),
                                    ManimColor(self.COL_BAR_HI),
                                    float(w) ** 0.7)
            bar.set_fill(col, opacity=1.0)
            bar.set_stroke("#0F0A1E", width=0.6, opacity=0.9)
            bar.move_to(grid_pos(i, j) + np.array([0, 0, h / 2]))
            return bar

        floor = VGroup()
        for i in range(n):
            for j in range(n):
                tile = Square(side_length=self.GRID * 0.92,
                              stroke_color="#334155", stroke_width=0.8,
                              fill_opacity=0.0)
                tile.move_to(grid_pos(i, j))
                floor.add(tile)

        strips = VGroup()
        for k in range(n):   # key axis (columns, front edge) + query axis (left)
            sk = Rectangle(width=self.GRID * 0.9, height=0.13,
                           fill_color=self.TOKEN_COLS[k], fill_opacity=0.95,
                           stroke_width=0)
            sk.move_to(grid_pos(n - 1, k) + np.array([0.0, -0.52, 0.01]))
            sq = Rectangle(width=0.13, height=self.GRID * 0.9,
                           fill_color=self.TOKEN_COLS[k], fill_opacity=0.95,
                           stroke_width=0)
            sq.move_to(grid_pos(k, 0) + np.array([-0.52, 0.0, 0.01]))
            strips.add(sk, sq)

        bars = [[make_bar(i, j, 0.008 / self.H_SCALE) for j in range(n)]
                for i in range(n)]
        bar_group = VGroup(*[b for row in bars for b in row])

        cap3 = caption(r"The whole matrix at once: $\mathrm{softmax}(QK^{\top})$",
                       self.COL_TITLE_B)
        self.add_fixed_in_frame_mobjects(cap3)
        cap3.set_opacity(0.0)

        self.add(floor, strips, bar_group)
        rise = [Transform(bars[i][j], make_bar(i, j, A1[i, j]))
                for i in range(n) for j in range(n)]
        self.move_camera(
            phi=62 * DEGREES, theta=-42 * DEGREES, zoom=0.78,
            frame_center=np.array([0.0, 0.0, 0.95]),
            added_anims=[
                LaggedStart(*rise, lag_ratio=0.02),
                arcs.animate.set_opacity(0.0),
                *[l.animate.set_opacity(0.0) for l in wlabels],
                cap2.animate.set_opacity(0.0),
                cap3.animate.set_opacity(1.0),
            ],
            run_time=3.0,
        )
        self.remove(cap2, *wlabels)
        self.wait(0.5)

        # =====================================================================
        # SECTION 5: HUD + orbit + morph to head 2
        # =====================================================================
        alpha_eq = MathTex(
            r"\alpha_{ij}", r"=",
            r"\mathrm{softmax}_j\!\left(\frac{q_i \cdot k_j}{\sqrt{d_k}}\right)",
            font_size=30, color=WHITE,
        )
        alpha_eq[0].set_color(self.COL_TITLE_A)
        alpha_eq.move_to(np.array([0.0, -4.95, 0.0]))
        alpha_box = SurroundingRectangle(
            alpha_eq, color=self.COL_TITLE_A, fill_color=self.COL_EQ_BOX,
            fill_opacity=0.78, buff=0.26, corner_radius=0.15, stroke_width=1.5,
        )
        note = Tex(r"row $i$: how much token $i$ attends to each token $j$",
                   font_size=25, color=GREY_A)
        note.next_to(alpha_box, DOWN, buff=0.26)

        head_label = Tex("Head:", font_size=32, color=GREY_A)
        head_num = Integer(1, font_size=32, color=GREY_A)
        head_hud = VGroup(head_label, head_num).arrange(RIGHT, buff=0.15)
        head_hud.move_to(np.array([-1.6, -6.75, 0.0]))
        focus_hud = Tex(r"Focus: ``sat''", font_size=32, color=GREY_A)
        focus_hud.move_to(np.array([1.6, -6.75, 0.0]))

        self.add_fixed_in_frame_mobjects(alpha_box, alpha_eq, note,
                                         head_hud, focus_hud)
        self.play(FadeIn(alpha_box, shift=UP * 0.3), Write(alpha_eq),
                  FadeIn(note), FadeIn(head_hud), FadeIn(focus_hud),
                  run_time=1.3)
        self.wait(0.4)

        self.begin_ambient_camera_rotation(rate=0.09)
        self.wait(1.6)

        # morph the city into head 2 — different head, different relations
        head_num.set_value(2)
        self.camera.add_fixed_in_frame_mobjects(head_num)   # re-pin (3D gotcha)
        cap4 = caption(r"Another head learns different relations",
                       self.COL_TITLE_A)
        self.add_fixed_in_frame_mobjects(cap4)
        cap4.set_opacity(0.0)
        self.play(
            *[Transform(bars[i][j], make_bar(i, j, A2[i, j]))
              for i in range(n) for j in range(n)],
            cap3.animate.set_opacity(0.0),
            cap4.animate.set_opacity(1.0),
            run_time=1.8,
        )
        self.remove(cap3)
        self.wait(3.2)
        self.stop_ambient_camera_rotation()
        self.wait(0.3)

        # =====================================================================
        # SECTION 6: Finale — the weighted blend
        # =====================================================================
        out_eq = MathTex(
            r"z_{\text{sat}}", r"=", r"\sum_j \alpha_{\text{sat},\,j}\, v_j",
            font_size=32, color=WHITE,
        )
        out_eq[0].set_color(self.COL_DONE)
        out_eq.move_to(np.array([0.0, -3.55, 0.0]))

        self.add_fixed_in_frame_mobjects(out_eq)
        out_eq.set_opacity(0.0)
        self.play(
            cap4.animate.set_opacity(0.0),
            out_eq.animate.set_opacity(1.0),
            arcs.animate.set_opacity(0.7),
            focus_pill[0].animate.set_stroke(self.COL_DONE, width=3),
            run_time=1.0,
        )
        self.remove(cap4)
        self.play(Flash(focus_pill.get_center(), color=self.COL_DONE,
                        line_length=0.28, num_lines=12, flash_radius=0.7),
                  run_time=0.8)

        done_label = Tex("Attention is all you need.", font_size=36,
                         color=self.COL_DONE)
        done_label.move_to(np.array([0.0, -7.5, 0.0]))
        self.add_fixed_in_frame_mobjects(done_label)
        done_label.set_opacity(0.0)
        self.play(done_label.animate.set_opacity(1.0), run_time=0.9)
        self.wait(2.2)

        # =====================================================================
        # SECTION 7: Fade out
        # =====================================================================
        all_3d = VGroup(bar_group, floor, strips)
        all_2d = VGroup(title, subtitle, attn_eq, pills, arcs, out_eq,
                        alpha_box, alpha_eq, note, head_hud, focus_hud,
                        done_label)
        self.play(FadeOut(all_3d, shift=IN * 0.4),
                  FadeOut(all_2d, shift=DOWN * 0.3),
                  run_time=1.5, rate_func=smooth)
        self.wait(0.4)
