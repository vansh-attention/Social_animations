"""
A* Pathfinding — the shortest path, found smart.
A search frontier floods across a walled grid, expanding toward the goal by
f(n) = g(n) + h(n) (cost-so-far + Manhattan estimate). Once the goal is
reached, the optimal path snaps green from start to goal.

Vertical 1080 x 1920 Instagram Reel layout:
  - top band    : gradient title + f = g + h equation
  - middle band : grid maze, exploration flood, then the green shortest path
  - bottom band : the priority rule + live explored / path-length HUD

Built with the manim-explainer-reel skill; every number is the real A* trace.
"""

from manim import *
import numpy as np
import heapq

# ── Portrait 1080 × 1920 (Reels format) ─────────────────────────────────────
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 30
config.background_color = "#000000"
config.disable_caching = True


class AStarPathfindingReel(Scene):
    """A* on a 13x15 grid (seed 2, pre-screened): 101 cells explored, a
    length-28 winding shortest path. The flood is colored by exploration
    order; the path snaps green — the payoff."""

    COLS, ROWS = 13, 15
    START, GOAL = (1, 1), (11, 13)

    # ── Palette (fresh gradient: amber -> red) ────────────────────────────────
    COL_TITLE_A = "#F59E0B"   # amber
    COL_TITLE_B = "#EF4444"   # red
    COL_SUB     = "#B0B8D0"
    COL_WALL    = "#1E293B"   # obstacle
    COL_FREE    = "#0B1220"   # unexplored cell
    COL_GRID    = "#243049"   # faint cell stroke
    COL_EXP_LO  = "#312E81"   # explored near start (indigo)
    COL_EXP_HI  = "#38BDF8"   # explored near frontier (cyan)
    COL_START   = "#34D399"   # start marker
    COL_GOAL    = "#FBBF24"   # goal marker
    COL_DONE    = "#00FF88"   # the shortest path / payoff green
    COL_EQ_BOX  = "#10102A"

    S = 0.44                  # cell spacing
    SIDE = 0.40               # cell square side

    def astar(self, walls):
        def h(a):
            return abs(a[0] - self.GOAL[0]) + abs(a[1] - self.GOAL[1])
        g = {self.START: 0}
        came, pq, order, closed = {}, [(h(self.START), self.START)], [], set()
        while pq:
            _, u = heapq.heappop(pq)
            if u in closed:
                continue
            closed.add(u)
            order.append(u)
            if u == self.GOAL:
                break
            for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                v = (u[0] + dc, u[1] + dr)
                if not (0 <= v[0] < self.COLS and 0 <= v[1] < self.ROWS) or v in walls:
                    continue
                ng = g[u] + 1
                if v not in g or ng < g[v]:
                    g[v] = ng
                    came[v] = u
                    heapq.heappush(pq, (ng + h(v), v))
        path = [self.GOAL]
        while path[-1] != self.START:
            path.append(came[path[-1]])
        return order, path[::-1]

    def cell_pos(self, c, r):
        cx = (c - (self.COLS - 1) / 2) * self.S
        cy = (r - (self.ROWS - 1) / 2) * self.S + 0.55
        return np.array([cx, cy, 0.0])

    def construct(self):
        # =====================================================================
        # Real A* trace (seed 2 pre-screened)
        # =====================================================================
        rng = np.random.default_rng(2)
        walls = set()
        for c in range(self.COLS):
            for r in range(self.ROWS):
                if (c, r) in (self.START, self.GOAL):
                    continue
                if rng.random() < 0.28:
                    walls.add((c, r))
        order, path = self.astar(walls)
        path_set = set(path)

        # =====================================================================
        # SECTION 1: Title band
        # =====================================================================
        title = Tex("A* Pathfinding", font_size=76)
        title.set_color_by_gradient(self.COL_TITLE_A, self.COL_TITLE_B)
        if title.width > 8.4:
            title.scale_to_fit_width(8.4)
        subtitle = Tex(r"\textit{the shortest path, found smart}",
                       color=self.COL_SUB, font_size=34)
        title.to_edge(UP, buff=0.6)
        subtitle.next_to(title, DOWN, buff=0.24)
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.2, rate_func=smooth)
        self.play(FadeIn(subtitle, shift=DOWN * 0.2), run_time=0.8)

        f_eq = MathTex(r"f(n)", r"=", r"g(n)", r"+", r"h(n)",
                       font_size=40, color=WHITE)
        f_eq[0].set_color(self.COL_TITLE_A)
        f_eq[2].set_color(self.COL_EXP_HI)
        f_eq[4].set_color(self.COL_GOAL)
        f_eq.next_to(subtitle, DOWN, buff=0.34)
        self.play(Write(f_eq), run_time=1.2)
        self.wait(0.3)

        # =====================================================================
        # SECTION 2: The grid
        # =====================================================================
        cells = {}
        grid = VGroup()
        for c in range(self.COLS):
            for r in range(self.ROWS):
                sq = Square(side_length=self.SIDE, stroke_color=self.COL_GRID,
                            stroke_width=1.0,
                            fill_color=self.COL_WALL if (c, r) in walls else self.COL_FREE,
                            fill_opacity=1.0)
                sq.move_to(self.cell_pos(c, r))
                cells[(c, r)] = sq
                grid.add(sq)

        def marker(cell, color, label):
            sq = cells[cell]
            sq.set_fill(color, opacity=1.0).set_stroke(WHITE, width=2)
            t = Tex(label, font_size=26, color=BLACK).move_to(sq.get_center())
            return t

        self.play(FadeIn(grid, lag_ratio=0.002), run_time=1.4)
        s_lbl = marker(self.START, self.COL_START, "S")
        g_lbl = marker(self.GOAL, self.COL_GOAL, "G")
        s_lbl.set_z_index(5); g_lbl.set_z_index(5)
        self.play(FadeIn(s_lbl), FadeIn(g_lbl), run_time=0.6)
        self.wait(0.3)

        # =====================================================================
        # SECTION 3: Rule box + HUD (bottom band)
        # =====================================================================
        rule = MathTex(r"\text{expand the } n \text{ with smallest } f(n)",
                       font_size=30, color=WHITE)
        rule.move_to(np.array([0.0, -4.9, 0.0]))
        rule_box = SurroundingRectangle(rule, color=self.COL_TITLE_A,
                                        fill_color=self.COL_EQ_BOX, fill_opacity=0.8,
                                        buff=0.26, corner_radius=0.15, stroke_width=1.5)
        note = MathTex(r"g:\text{ cost so far}\quad h:\text{ Manhattan estimate}",
                       font_size=25, color=GREY_A)
        note.next_to(rule_box, DOWN, buff=0.26)

        exp_num = Integer(0, font_size=32, color=GREY_A)
        exp_hud = VGroup(Tex("Explored:", font_size=32, color=GREY_A), exp_num
                         ).arrange(RIGHT, buff=0.15).move_to([-1.55, -6.65, 0])
        path_num = Integer(0, font_size=32, color=GREY_A)
        path_hud = VGroup(Tex("Path:", font_size=32, color=GREY_A), path_num
                          ).arrange(RIGHT, buff=0.15).move_to([1.75, -6.65, 0])
        self.play(FadeIn(rule_box, shift=UP * 0.3), Write(rule),
                  FadeIn(note), FadeIn(exp_hud), FadeIn(path_hud), run_time=1.3)

        def caption(tex_str, color=None):
            c = Tex(tex_str, font_size=31, color=color or self.COL_SUB)
            if c.width > 8.3:
                c.scale_to_fit_width(8.3)
            return c.move_to(np.array([0.0, -3.35, 0.0]))

        cap = caption(r"Flood outward, guided toward the goal", self.COL_EXP_HI)
        self.play(FadeIn(cap), run_time=0.4)

        # =====================================================================
        # SECTION 4: The exploration flood (real A* order, colored by distance)
        # =====================================================================
        explored = [u for u in order if u not in (self.START, self.GOAL)]
        flood = []
        for i, u in enumerate(explored):
            frac = i / max(len(explored) - 1, 1)
            col = interpolate_color(ManimColor(self.COL_EXP_LO),
                                    ManimColor(self.COL_EXP_HI), frac)
            flood.append(cells[u].animate.set_fill(col, opacity=1.0))
        self.play(LaggedStart(*flood, lag_ratio=0.7 / len(flood)),
                  ChangeDecimalToValue(exp_num, len(order)),
                  run_time=3.6)
        self.wait(0.4)

        # =====================================================================
        # SECTION 5: The shortest path snaps green (payoff)
        # =====================================================================
        cap2 = caption(r"Goal reached --- backtrack the shortest path",
                       self.COL_DONE)
        self.play(ReplacementTransform(cap, cap2), run_time=0.5)

        inner = [u for u in path if u not in (self.START, self.GOAL)]
        snap = [cells[u].animate.set_fill(self.COL_DONE, opacity=1.0) for u in inner]
        self.play(LaggedStart(*snap, lag_ratio=0.5 / len(snap)),
                  ChangeDecimalToValue(path_num, len(path) - 1),
                  run_time=1.6)
        self.play(Flash(cells[self.GOAL].get_center(), color=self.COL_DONE,
                        line_length=0.3, num_lines=14, flash_radius=0.6), run_time=0.8)

        done = Tex("Shortest Path Found", font_size=36, color=self.COL_DONE
                   ).move_to([0.0, -7.45, 0.0])
        self.play(FadeIn(done, shift=UP * 0.2), run_time=0.9)
        self.wait(2.3)

        # =====================================================================
        # SECTION 6: Fade out
        # =====================================================================
        self.play(FadeOut(VGroup(title, subtitle, f_eq, grid, s_lbl, g_lbl, cap2,
                                 rule_box, rule, note, exp_hud, path_hud, done),
                          shift=DOWN * 0.3), run_time=1.4, rate_func=smooth)
        self.wait(0.4)
