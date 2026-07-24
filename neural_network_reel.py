"""
Neural network — a forward pass, then training by backprop.
A fully-connected 3-5-4-2 net: signal flows left→right and the neurons light
up (forward pass), then error flows right→left (backprop) while the loss
drops and the weights recolour as they learn.

Vertical 1080 x 1920 Instagram Reel layout:
  - top band    : gradient title + forward-propagation equation
  - middle band : the network graph with flowing activations
  - bottom band : weight-update rule + live epoch / loss HUD
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


class NeuralNetworkReel(Scene):
    """Builds a 3-5-4-2 MLP, animates a forward pass (activation wave L→R),
    a backprop wave (R→L), then a short training montage with falling loss."""

    # ── Colour palette ────────────────────────────────────────────────────────
    COL_TITLE_A = "#22D3EE"   # cyan   (gradient start)
    COL_TITLE_B = "#A78BFA"   # violet (gradient end)
    COL_SUB     = "#B0B8D0"   # soft grey-blue
    COL_NEURON  = "#1E293B"   # resting neuron fill
    COL_NRING   = "#64748B"   # neuron outline
    COL_ACT     = "#67E8F9"   # activation / forward signal (cyan)
    COL_BACK    = "#FB7185"   # backprop signal (rose)
    COL_POS     = "#FB923C"   # positive weight (orange)
    COL_NEG     = "#60A5FA"   # negative weight (blue)
    COL_DONE    = "#00FF88"   # trained output (green)
    COL_EQ_BOX  = "#10102A"   # dark panel behind equations

    LAYERS = [3, 5, 4, 2]

    @staticmethod
    def sigmoid(z):
        return 1.0 / (1.0 + np.exp(-z))

    def construct(self):
        # =====================================================================
        # Weights, activations, training loss (precomputed)
        # =====================================================================
        rng = np.random.default_rng(7)
        L = self.LAYERS
        W_init = [rng.normal(0, 1.0, (L[i + 1], L[i])) for i in range(len(L) - 1)]
        W_trn = [w * 0.35 + rng.normal(0, 0.7, w.shape) for w in W_init]
        biases = [rng.normal(0, 0.4, (L[i + 1],)) for i in range(len(L) - 1)]
        wmax = max(np.abs(w).max() for w in W_init + W_trn)

        x_in = rng.uniform(0.35, 1.0, L[0])
        acts = [x_in]
        for i in range(len(L) - 1):
            acts.append(self.sigmoid(W_init[i] @ acts[-1] + biases[i]))

        epochs = [0, 12, 24, 38, 52, 64]
        losses = [1.18, 0.74, 0.46, 0.25, 0.12, 0.05]

        # =====================================================================
        # SECTION 1: Title band (gradient cyan→violet, no underline)
        # =====================================================================
        title = Tex("Neural Networks", font_size=76)
        title.set_color_by_gradient(self.COL_TITLE_A, self.COL_TITLE_B)
        if title.width > 8.4:
            title.scale_to_fit_width(8.4)
        subtitle = Tex(r"\textit{learning by forward pass \& backprop}",
                       color=self.COL_SUB, font_size=33)
        title.to_edge(UP, buff=0.6)
        subtitle.next_to(title, DOWN, buff=0.25)

        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.3, rate_func=smooth)
        self.play(FadeIn(subtitle, shift=DOWN * 0.2), run_time=0.9)
        self.wait(0.3)

        fwd_eq = MathTex(
            r"a^{(l)}", r"=", r"\sigma\!\big(",
            r"W^{(l)} a^{(l-1)} + b^{(l)}", r"\big)",
            font_size=36, color=WHITE,
        )
        fwd_eq[0].set_color(self.COL_ACT)
        fwd_eq[2].set_color(self.COL_TITLE_B)
        fwd_eq[4].set_color(self.COL_TITLE_B)
        fwd_eq.next_to(subtitle, DOWN, buff=0.4)
        self.play(Write(fwd_eq), run_time=1.4)
        self.wait(0.3)

        # =====================================================================
        # SECTION 2: Build the network graph (middle band)
        # =====================================================================
        y0 = 0.7
        xs = np.linspace(-2.7, 2.7, len(L))
        neurons = []
        for li, m in enumerate(L):
            ys = (np.arange(m) - (m - 1) / 2) * 0.92 + y0
            col = VGroup()
            for yy in ys:
                nrn = Circle(radius=0.25, color=self.COL_NRING, stroke_width=2.5,
                             fill_color=self.COL_NEURON, fill_opacity=1.0)
                nrn.move_to(np.array([xs[li], yy, 0.0]))
                col.add(nrn)
            neurons.append(col)

        def edge_style(w):
            norm = w / wmax
            color = self.COL_POS if w >= 0 else self.COL_NEG
            return color, float(np.clip(abs(norm), 0.12, 1.0) * 0.75), 1.0 + 2.2 * abs(norm)

        edges_into = []          # edges_into[l] = VGroup of edges from layer l-1 → l
        edge_meta = []           # parallel list of (mobj, w_init, w_trn) for recolour
        for li in range(1, len(L)):
            grp = VGroup()
            for j in range(L[li]):
                for i in range(L[li - 1]):
                    w = W_init[li - 1][j, i]
                    c, op, wd = edge_style(w)
                    e = Line(neurons[li - 1][i].get_center(),
                             neurons[li][j].get_center(),
                             stroke_color=c, stroke_width=wd, stroke_opacity=op)
                    e.set_z_index(-1)
                    grp.add(e)
                    edge_meta.append((e, W_init[li - 1][j, i], W_trn[li - 1][j, i]))
            edges_into.append(grp)

        # neurons appear layer by layer, then the edges fade in
        for col in neurons:
            self.play(LaggedStart(*[GrowFromCenter(n) for n in col],
                                  lag_ratio=0.12), run_time=0.55)
        self.play(*[FadeIn(g) for g in edges_into], run_time=0.9)
        self.wait(0.3)

        # =====================================================================
        # SECTION 3: Update rule + HUD (bottom band)
        # =====================================================================
        update_rule = MathTex(
            r"W^{(l)}", r"\leftarrow", r"W^{(l)}", r"-", r"\alpha",
            r"\frac{\partial L}{\partial W^{(l)}}",
            font_size=36, color=WHITE,
        )
        update_rule[0].set_color(self.COL_TITLE_A)
        update_rule[4].set_color(YELLOW)
        update_rule[5].set_color(self.COL_BACK)
        update_rule.move_to(np.array([0.0, -4.7, 0.0]))

        update_box = SurroundingRectangle(
            update_rule, color=self.COL_TITLE_B, fill_color=self.COL_EQ_BOX,
            fill_opacity=0.78, buff=0.28, corner_radius=0.15, stroke_width=1.5,
        )
        arch_note = Tex(r"fully connected $\;\cdot\;$ 3 -- 5 -- 4 -- 2",
                        font_size=26, color=GREY_A)
        arch_note.next_to(update_box, DOWN, buff=0.28)

        ep_label = Tex("Epoch:", font_size=32, color=GREY_A)
        ep_num = Integer(0, font_size=32, color=GREY_A)
        ep_hud = VGroup(ep_label, ep_num).arrange(RIGHT, buff=0.15)
        ep_hud.move_to(np.array([-1.55, -6.6, 0.0]))

        loss_label = MathTex(r"L =", font_size=32, color=GREY_A)
        loss_num = DecimalNumber(losses[0], num_decimal_places=3,
                                 font_size=32, color=GREY_A)
        loss_hud = VGroup(loss_label, loss_num).arrange(RIGHT, buff=0.15)
        loss_hud.move_to(np.array([1.65, -6.6, 0.0]))

        self.play(FadeIn(update_box, shift=UP * 0.3), Write(update_rule), run_time=1.4)
        self.play(FadeIn(arch_note), FadeIn(ep_hud), FadeIn(loss_hud), run_time=0.6)
        self.wait(0.4)

        # caption helper
        def caption(tex_str, color):
            c = Tex(tex_str, font_size=32, color=color)
            c.move_to(np.array([0.0, -3.35, 0.0]))
            return c

        # =====================================================================
        # SECTION 4: Forward pass — activation wave L→R
        # =====================================================================
        fwd_cap = caption(r"Forward pass $\rightarrow$", self.COL_ACT)
        self.play(FadeIn(fwd_cap, shift=UP * 0.15), run_time=0.4)

        # light the input layer
        self.play(*[neurons[0][i].animate.set_fill(self.COL_ACT,
                    opacity=float(np.clip(acts[0][i], 0.25, 1.0)))
                    for i in range(L[0])], run_time=0.5)

        for li in range(1, len(L)):
            flashes = [ShowPassingFlash(
                e.copy().set_stroke(self.COL_ACT, width=4.5, opacity=1.0),
                time_width=0.5, run_time=0.9)
                for e in edges_into[li - 1]]
            self.play(LaggedStart(*flashes, lag_ratio=0.015), run_time=0.9)
            self.play(*[neurons[li][j].animate.set_fill(self.COL_ACT,
                        opacity=float(np.clip(acts[li][j], 0.25, 1.0)))
                        for j in range(L[li])], run_time=0.45)
        self.wait(0.5)

        # =====================================================================
        # SECTION 5: Backprop wave R→L + training montage
        # =====================================================================
        back_cap = caption(r"Backpropagation $\leftarrow$", self.COL_BACK)
        self.play(ReplacementTransform(fwd_cap, back_cap), run_time=0.5)

        for li in range(len(L) - 1, 0, -1):
            flashes = [ShowPassingFlash(
                e.copy().reverse_points().set_stroke(self.COL_BACK, width=4.5, opacity=1.0),
                time_width=0.5, run_time=0.8)
                for e in edges_into[li - 1]]
            self.play(LaggedStart(*flashes, lag_ratio=0.015), run_time=0.8)
        self.wait(0.3)

        train_cap = caption(r"Training: weights update each epoch", self.COL_TITLE_B)
        self.play(ReplacementTransform(back_cap, train_cap), run_time=0.5)

        # montage: progressively recolour edges to their trained weights while
        # loss falls and the epoch counter climbs
        n_rounds = len(epochs) - 1
        chunks = np.array_split(np.arange(len(edge_meta)), n_rounds)
        for r in range(n_rounds):
            recolour = []
            for idx in chunks[r]:
                e, _wi, wt = edge_meta[idx]
                c, op, wd = edge_style(wt)
                recolour.append(e.animate.set_stroke(color=c, width=wd, opacity=op))
            quick_flash = [ShowPassingFlash(
                e.copy().set_stroke(self.COL_ACT, width=3.5, opacity=0.9),
                time_width=0.6, run_time=0.7)
                for e in edges_into[r % len(edges_into)]]
            self.play(
                *recolour,
                LaggedStart(*quick_flash, lag_ratio=0.01),
                ChangeDecimalToValue(loss_num, losses[r + 1]),
                ChangeDecimalToValue(ep_num, epochs[r + 1]),
                run_time=0.85,
            )
        self.wait(0.4)

        # =====================================================================
        # SECTION 6: Converged — outputs light up green
        # =====================================================================
        done_cap = caption(r"Network trained", self.COL_DONE)
        self.play(
            ReplacementTransform(train_cap, done_cap),
            *[neurons[-1][j].animate.set_fill(self.COL_DONE, opacity=0.95)
              for j in range(L[-1])],
            *[neurons[-1][j].animate.set_stroke(self.COL_DONE, width=3)
              for j in range(L[-1])],
            run_time=0.8,
        )
        self.play(*[Flash(neurons[-1][j].get_center(), color=self.COL_DONE,
                          line_length=0.25, num_lines=10, flash_radius=0.45)
                    for j in range(L[-1])], run_time=0.9)
        self.wait(2.2)

        # =====================================================================
        # SECTION 7: Fade out
        # =====================================================================
        net = VGroup(*neurons, *edges_into)
        everything = VGroup(
            title, subtitle, fwd_eq, net, done_cap,
            update_box, update_rule, arch_note, ep_hud, loss_hud,
        )
        self.play(FadeOut(everything, shift=DOWN * 0.3), run_time=1.4, rate_func=smooth)
        self.wait(0.4)
