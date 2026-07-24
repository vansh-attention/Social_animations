"""
Attention, told the 3Blue1Brown way: "a fluffy blue creature".
Adjectives update the noun. The noun's query asks "any adjectives in front
of me?", matching keys answer via dot products, softmax(QKᵀ) forms the
attention pattern (a rising 3D bar city), and finally the value vectors
physically MOVE the word's embedding in meaning-space: E' = E + Δ.

Vertical 1080 x 1920 Instagram Reel layout (ThreeDScene):
  - top band    : gradient title + Attention(Q,K,V) equation + token pills
  - arc band    : query/key arcs with real softmax weights
  - middle band : 3D attention-pattern bar city → embedding-update vector plane
  - bottom band : E' = E + Σ αv update rule + HUD
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


class AttentionQKVReel(ThreeDScene):
    """Q→K→attention-pattern→V story on 'a fluffy blue creature': real
    softmax weights, an orbiting 3D pattern grid, and the embedding of
    'creature' visibly moving toward 'fluffy blue creature' in vector space."""

    # ── Colour palette ────────────────────────────────────────────────────────
    COL_TITLE_A = "#E879F9"   # fuchsia (gradient start)
    COL_TITLE_B = "#22D3EE"   # cyan    (gradient end)
    COL_SUB     = "#B0B8D0"   # soft grey-blue
    COL_BAR_LO  = "#312E81"   # low attention weight (indigo)
    COL_BAR_HI  = "#F0ABFC"   # high attention weight (light fuchsia)
    COL_DONE    = "#00FF88"   # updated embedding / finale green
    COL_EQ_BOX  = "#10102A"   # dark panel behind equations
    TOKEN_COLS  = ["#94A3B8", "#22D3EE", "#60A5FA", "#FBBF24"]

    WORDS = ["a", "fluffy", "blue", "creature"]
    FOCUS = 3                 # "creature"

    GRID = 0.85               # bar-city grid spacing
    BAR_W = 0.42              # bar footprint
    H_SCALE = 2.6             # bar height per unit weight

    @staticmethod
    def softmax_rows(m):
        e = np.exp(m - m.max(axis=1, keepdims=True))
        return e / e.sum(axis=1, keepdims=True)

    def construct(self):
        n = len(self.WORDS)

        # =====================================================================
        # Attention pattern: engineered scores, real softmax
        # (adjectives update the noun; the determiner points at it too)
        # =====================================================================
        rng = np.random.default_rng(6)
        s = rng.normal(0.0, 0.3, (n, n))
        s[3, 1] += 2.6   # creature → fluffy
        s[3, 2] += 2.45  # creature → blue
        s[3, 3] += 0.6
        s[1, 3] += 1.8   # fluffy → creature
        s[1, 1] += 1.5
        s[2, 3] += 1.9   # blue → creature
        s[2, 2] += 1.4
        s[0, 3] += 2.2   # a → creature
        A = self.softmax_rows(s)
        w_row = A[self.FOCUS]

        # =====================================================================
        # SECTION 1: Title band (fixed in frame)
        # =====================================================================
        title = Tex("Attention", font_size=80)
        title.set_color_by_gradient(self.COL_TITLE_A, self.COL_TITLE_B)
        subtitle = Tex(r"\textit{how words update each other's meaning}",
                       color=self.COL_SUB, font_size=33)
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
        self.play(Write(attn_eq), run_time=1.3)
        self.wait(0.3)

        # =====================================================================
        # SECTION 2: Token pills + embedding arrows
        # =====================================================================
        pills = VGroup()
        for w, c in zip(self.WORDS, self.TOKEN_COLS):
            txt = Tex(w, font_size=36, color=WHITE)
            box = RoundedRectangle(
                width=txt.width + 0.44, height=0.66, corner_radius=0.17,
                fill_color=self.COL_EQ_BOX, fill_opacity=0.92,
                stroke_color=c, stroke_width=2.2,
            )
            txt.move_to(box.get_center())
            pills.add(VGroup(box, txt))
        pills.arrange(RIGHT, buff=0.3)
        pills.move_to(np.array([0.0, 4.45, 0.0]))

        # each word starts as a little meaning-vector
        emb_dirs = [(0.32, 0.18), (-0.25, 0.42), (0.12, 0.48), (0.45, 0.1)]
        emb_arrows = VGroup()
        for p, c, (dx, dy) in zip(pills, self.TOKEN_COLS, emb_dirs):
            start = p.get_bottom() + DOWN * 0.18
            emb_arrows.add(Arrow(start, start + np.array([dx, dy, 0]) * 0.9,
                                 buff=0, color=c, stroke_width=3.5,
                                 max_tip_length_to_length_ratio=0.3))

        def caption(tex_str, color=None):
            c = Tex(tex_str, font_size=31, color=color or self.COL_SUB)
            if c.width > 8.3:
                c.scale_to_fit_width(8.3)
            c.move_to(np.array([0.0, -3.55, 0.0]))
            return c

        cap1 = caption(r"Every word starts as a vector --- its meaning")
        self.add_fixed_in_frame_mobjects(pills, emb_arrows, cap1)
        cap1.set_opacity(0.0)
        emb_arrows.set_opacity(0.0)
        self.play(
            LaggedStart(*[FadeIn(p, shift=DOWN * 0.2, scale=0.8) for p in pills],
                        lag_ratio=0.14),
            run_time=1.2,
        )
        self.play(emb_arrows.animate.set_opacity(1.0),
                  cap1.animate.set_opacity(1.0), run_time=0.9)
        self.wait(0.8)

        # =====================================================================
        # SECTION 3: The query — "creature" asks
        # =====================================================================
        focus_pill = pills[self.FOCUS]
        cap2 = caption(r"``creature'' sends a \textbf{query}: "
                       r"any adjectives in front of me?", self.TOKEN_COLS[3])
        self.add_fixed_in_frame_mobjects(cap2)
        cap2.set_opacity(0.0)
        self.play(
            Indicate(focus_pill, color=self.TOKEN_COLS[3], scale_factor=1.12),
            cap1.animate.set_opacity(0.0),
            cap2.animate.set_opacity(1.0),
            run_time=1.0,
        )
        self.remove(cap1)
        self.wait(0.7)

        # =====================================================================
        # SECTION 4: Keys answer — weighted arcs
        # =====================================================================
        arcs = VGroup()
        arc_of = {}
        for j in range(n):
            if j == self.FOCUS:
                continue
            a, b = focus_pill[0].get_bottom(), pills[j][0].get_bottom()
            sgn = 1 if b[0] > a[0] else -1
            arc = ArcBetweenPoints(a, b, angle=sgn * 1.0)
            arc.set_stroke(self.TOKEN_COLS[j],
                           width=1.5 + 12.0 * w_row[j],
                           opacity=0.35 + 0.6 * float(w_row[j] / w_row.max()))
            arc_of[j] = arc
            arcs.add(arc)

        wlabels = VGroup()
        for j in (1, 2):                     # fluffy, blue
            lbl = Tex(f"{w_row[j]:.2f}", font_size=25, color=self.TOKEN_COLS[j])
            lbl.next_to(arc_of[j].point_from_proportion(0.5), DOWN, buff=0.08)
            wlabels.add(lbl)

        cap3 = caption(r"\textbf{Keys} that match answer loudest --- "
                       r"dot products, then softmax", self.COL_SUB)
        self.add_fixed_in_frame_mobjects(arcs, wlabels, cap3)
        arcs.set_opacity(0.0)
        for m in (*wlabels, cap3):
            m.set_opacity(0.0)

        self.play(
            *[arc_of[j].animate.set_stroke(opacity=0.35 + 0.6 * float(
                w_row[j] / w_row.max())) for j in arc_of],
            *[l.animate.set_opacity(1.0) for l in wlabels],
            emb_arrows.animate.set_opacity(0.0),
            cap2.animate.set_opacity(0.0),
            cap3.animate.set_opacity(1.0),
            run_time=1.5,
        )
        self.remove(cap2)
        self.wait(1.0)

        # =====================================================================
        # SECTION 5: The attention pattern — 3D bar city
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

        floor, strips = VGroup(), VGroup()
        for i in range(n):
            for j in range(n):
                tile = Square(side_length=self.GRID * 0.92,
                              stroke_color="#334155", stroke_width=0.8,
                              fill_opacity=0.0)
                tile.move_to(grid_pos(i, j))
                floor.add(tile)
        for k in range(n):
            sk = Rectangle(width=self.GRID * 0.9, height=0.14,
                           fill_color=self.TOKEN_COLS[k], fill_opacity=0.95,
                           stroke_width=0)
            sk.move_to(grid_pos(n - 1, k) + np.array([0.0, -0.62, 0.01]))
            sq = Rectangle(width=0.14, height=self.GRID * 0.9,
                           fill_color=self.TOKEN_COLS[k], fill_opacity=0.95,
                           stroke_width=0)
            sq.move_to(grid_pos(k, 0) + np.array([-0.62, 0.0, 0.01]))
            strips.add(sk, sq)

        bars = [[make_bar(i, j, 0.008 / self.H_SCALE) for j in range(n)]
                for i in range(n)]
        bar_group = VGroup(*[b for row in bars for b in row])

        cap4 = caption(r"The \textbf{attention pattern}: "
                       r"$\mathrm{softmax}(QK^{\top}/\sqrt{d_k})$",
                       self.COL_TITLE_B)
        self.add_fixed_in_frame_mobjects(cap4)
        cap4.set_opacity(0.0)

        self.add(floor, strips, bar_group)
        rise = [Transform(bars[i][j], make_bar(i, j, A[i, j]))
                for i in range(n) for j in range(n)]
        self.move_camera(
            phi=62 * DEGREES, theta=-42 * DEGREES, zoom=0.78,
            frame_center=np.array([0.0, 0.0, 0.95]),
            added_anims=[
                LaggedStart(*rise, lag_ratio=0.03),
                arcs.animate.set_opacity(0.0),
                *[l.animate.set_opacity(0.0) for l in wlabels],
                cap3.animate.set_opacity(0.0),
                cap4.animate.set_opacity(1.0),
            ],
            run_time=3.0,
        )
        self.remove(cap3, *wlabels)

        # bottom band: the update rule
        upd_eq = MathTex(
            r"E'_{i}", r"=", r"E_{i}", r"+",
            r"\sum_j \alpha_{ij}\, v_j",
            font_size=32, color=WHITE,
        )
        upd_eq[0].set_color(self.COL_DONE)
        upd_eq[4].set_color(self.COL_TITLE_A)
        upd_eq.move_to(np.array([0.0, -4.95, 0.0]))
        upd_box = SurroundingRectangle(
            upd_eq, color=self.COL_TITLE_A, fill_color=self.COL_EQ_BOX,
            fill_opacity=0.78, buff=0.26, corner_radius=0.15, stroke_width=1.5,
        )
        note = Tex(r"one head --- GPT-3 runs 96 of these in parallel",
                   font_size=25, color=GREY_A)
        note.next_to(upd_box, DOWN, buff=0.26)
        focus_hud = Tex(r"Focus: ``creature''", font_size=30, color=GREY_A)
        focus_hud.move_to(np.array([0.0, -6.75, 0.0]))

        self.add_fixed_in_frame_mobjects(upd_box, upd_eq, note, focus_hud)
        self.play(FadeIn(upd_box, shift=UP * 0.3), Write(upd_eq),
                  FadeIn(note), FadeIn(focus_hud), run_time=1.3)

        self.begin_ambient_camera_rotation(rate=0.09)
        self.wait(3.2)
        self.stop_ambient_camera_rotation()

        # =====================================================================
        # SECTION 6: Values move the meaning — E' = E + Δ in vector space
        # =====================================================================
        cap5 = caption(r"\textbf{Values} then move the meaning: "
                       r"``creature'' drifts toward its adjectives",
                       self.COL_DONE)
        self.add_fixed_in_frame_mobjects(cap5)
        cap5.set_opacity(0.0)
        self.play(
            FadeOut(bar_group, shift=IN * 0.4), FadeOut(floor),
            FadeOut(strips),
            cap4.animate.set_opacity(0.0),
            cap5.animate.set_opacity(1.0),
            run_time=1.2,
        )
        self.remove(cap4)

        # 2D meaning-space panel (fixed in frame)
        O = np.array([-2.3, -1.7, 0.0])
        ax_x = Line(O + LEFT * 0.5, O + RIGHT * 6.2, color="#3F4A5A",
                    stroke_width=1.6)
        ax_y = Line(O + DOWN * 0.5, O + UP * 4.1, color="#3F4A5A",
                    stroke_width=1.6)

        vE = np.array([3.3, 0.5, 0.0])
        d1 = np.array([0.85, 1.45, 0.0])      # α · v_fluffy
        d2 = np.array([1.25, 0.85, 0.0])      # α · v_blue

        arr_E = Arrow(O, O + vE, buff=0, color=self.TOKEN_COLS[3],
                      stroke_width=5, max_tip_length_to_length_ratio=0.09)
        lbl_E = MathTex(r"E_{\text{creature}}", font_size=28,
                        color=self.TOKEN_COLS[3])
        lbl_E.next_to(O + vE, DOWN, buff=0.12)

        arr_d1 = Arrow(O + vE, O + vE + d1, buff=0, color=self.TOKEN_COLS[1],
                       stroke_width=4.5, max_tip_length_to_length_ratio=0.16)
        lbl_d1 = MathTex(r"\alpha\,v_{\text{fluffy}}", font_size=26,
                         color=self.TOKEN_COLS[1])
        lbl_d1.next_to(arr_d1.get_center(), RIGHT, buff=0.1)

        arr_d2 = Arrow(O + vE + d1, O + vE + d1 + d2, buff=0,
                       color=self.TOKEN_COLS[2], stroke_width=4.5,
                       max_tip_length_to_length_ratio=0.16)
        lbl_d2 = MathTex(r"\alpha\,v_{\text{blue}}", font_size=26,
                         color=self.TOKEN_COLS[2])
        lbl_d2.next_to(arr_d2.get_center(), DR, buff=0.16)

        arr_En = Arrow(O, O + vE + d1 + d2, buff=0, color=self.COL_DONE,
                       stroke_width=6, max_tip_length_to_length_ratio=0.08)
        lbl_En = MathTex(r"E'_{\text{creature}}", font_size=30,
                         color=self.COL_DONE)
        lbl_En.move_to(O + (vE + d1 + d2) * 0.55 + UP * 0.45 + LEFT * 0.3)

        region = Tex(r"\textit{a fluffy blue creature}", font_size=27,
                     color=self.COL_SUB)
        region.next_to(O + vE + d1 + d2, UP, buff=0.18)
        region.shift(LEFT * 0.4)

        panel = VGroup(ax_x, ax_y, arr_E, lbl_E, arr_d1, lbl_d1,
                       arr_d2, lbl_d2, arr_En, lbl_En, region)
        self.add_fixed_in_frame_mobjects(panel)
        panel.set_opacity(0.0)

        self.play(ax_x.animate.set_opacity(1.0), ax_y.animate.set_opacity(1.0),
                  arr_E.animate.set_opacity(1.0), lbl_E.animate.set_opacity(1.0),
                  run_time=1.0)
        # set_stroke only — set_opacity would switch on the arcs' white fill
        self.play(arr_d1.animate.set_opacity(1.0),
                  lbl_d1.animate.set_opacity(1.0),
                  arc_of[1].animate.set_stroke(opacity=0.9), run_time=0.9)
        self.play(arr_d2.animate.set_opacity(1.0),
                  lbl_d2.animate.set_opacity(1.0),
                  arc_of[2].animate.set_stroke(opacity=0.9), run_time=0.9)
        self.play(arr_En.animate.set_opacity(1.0),
                  lbl_En.animate.set_opacity(1.0),
                  region.animate.set_opacity(1.0),
                  focus_pill[0].animate.set_stroke(self.COL_DONE, width=3),
                  run_time=1.2)
        self.play(Flash(O + vE + d1 + d2, color=self.COL_DONE,
                        line_length=0.28, num_lines=12, flash_radius=0.6),
                  run_time=0.8)
        self.wait(1.2)

        # =====================================================================
        # SECTION 7: Finale
        # =====================================================================
        done_label = Tex("Attention is all you need.", font_size=36,
                         color=self.COL_DONE)
        done_label.move_to(np.array([0.0, -7.5, 0.0]))
        self.add_fixed_in_frame_mobjects(done_label)
        done_label.set_opacity(0.0)
        self.play(done_label.animate.set_opacity(1.0), run_time=0.9)
        self.wait(2.2)

        # =====================================================================
        # SECTION 8: Fade out
        # =====================================================================
        all_2d = VGroup(title, subtitle, attn_eq, pills, emb_arrows, arcs,
                        panel, cap5, upd_box, upd_eq, note, focus_hud,
                        done_label)
        self.play(FadeOut(all_2d, shift=DOWN * 0.3), run_time=1.5,
                  rate_func=smooth)
        self.wait(0.4)
