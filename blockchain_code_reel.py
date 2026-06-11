"""
"Build a Blockchain in Python" — code-typing explainer.
Vertical 1080 x 1920 Instagram Reel layout:
  - top band    : title + divider
  - step header : "Step k — ..." caption that morphs between sections
  - middle band : code window where each snippet types itself out
  - bottom band : one-line takeaway caption per step
  - finale      : linked-blocks diagram + chain.is_valid() -> True
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


class BlockchainCodeReel(Scene):
    """Types out a minimal working blockchain (~40 lines of Python), section
    by section, then ends with a linked-blocks diagram and a validity check."""

    # ── Colour palette ───────────────────────────────────────────────────────
    COL_TITLE    = "#58C4DD"   # 3B1B teal
    COL_SUBTITLE = "#B0B8D0"   # soft grey-blue
    COL_PANEL    = "#0D1117"   # GitHub-dark editor background
    COL_ACCENT   = "#FFB347"   # warm accent (arrows, highlights)
    COL_OK       = "#00FF88"   # success green
    COL_BOX      = "#10102A"   # dark panel for diagram blocks

    CODE_W = 8.3               # max width of the code window
    CODE_H = 6.6               # max height of the code window
    CODE_Y = 0.5               # vertical centre of the code band

    # ── Code snippets (one file, continuing line numbers) ────────────────────
    SNIPPETS = [
        (
            "Step 1 — The Block",
            "blockchain.py",
            1,
            '''import hashlib, json, time

class Block:
    def __init__(self, index, data, prev_hash):
        self.index     = index
        self.timestamp = time.time()
        self.data      = data
        self.prev_hash = prev_hash
        self.nonce     = 0
        self.hash      = self.compute_hash()''',
            r"A block is just data\\plus the previous block's hash",
        ),
        (
            "Step 2 — The Fingerprint",
            "blockchain.py",
            12,
            '''    def compute_hash(self):
        payload = json.dumps({
            "index":     self.index,
            "timestamp": self.timestamp,
            "data":      self.data,
            "prev_hash": self.prev_hash,
            "nonce":     self.nonce,
        }, sort_keys=True)
        return hashlib.sha256(
            payload.encode()
        ).hexdigest()''',
            r"SHA-256 crushes the whole block\\into one 64-character fingerprint",
        ),
        (
            "Step 3 — Chaining Blocks",
            "blockchain.py",
            24,
            '''class Blockchain:
    difficulty = 4

    def __init__(self):
        genesis = Block(0, "genesis", "0" * 64)
        self.chain = [genesis]

    def add_block(self, data):
        block = Block(
            index=len(self.chain),
            data=data,
            prev_hash=self.chain[-1].hash,
        )
        self.proof_of_work(block)
        self.chain.append(block)''',
            r"Every block stores the hash of the\\one before it --- that's the chain",
        ),
        (
            "Step 4 — Proof of Work",
            "blockchain.py",
            40,
            '''    def proof_of_work(self, block):
        target = "0" * self.difficulty
        while not block.hash.startswith(target):
            block.nonce += 1
            block.hash = block.compute_hash()
        return block.nonce''',
            r"Mining: bump the nonce until\\the hash starts with 0000",
        ),
        (
            "Step 5 — Validating the Chain",
            "blockchain.py",
            47,
            '''    def is_valid(self):
        for prev, curr in zip(self.chain,
                              self.chain[1:]):
            if curr.prev_hash != prev.hash:
                return False
            if curr.hash != curr.compute_hash():
                return False
        return True''',
            r"Change a single byte and\\every later hash breaks",
        ),
        (
            "Run It",
            "demo.py",
            1,
            '''chain = Blockchain()

chain.add_block({"to": "Bob",   "amount": 5})
chain.add_block({"to": "Carol", "amount": 2})

print(chain.chain[-1].hash[:12])  # 0000f3a91c2b
print(chain.is_valid())           # True''',
            r"Two mined blocks, a valid chain ---\\a blockchain in $\sim$40 lines of Python",
        ),
    ]

    # ── Helpers ──────────────────────────────────────────────────────────────
    def make_code(self, source, first_line):
        code = Code(
            code_string=source,
            language="python",
            formatter_style="github-dark",
            add_line_numbers=True,
            line_numbers_from=first_line,
            background="window",
            background_config={
                "fill_color": self.COL_PANEL,
                "fill_opacity": 1.0,
                "stroke_color": self.COL_TITLE,
                "stroke_width": 1.2,
            },
            paragraph_config={"font": "Menlo", "font_size": 24},
        )
        if code.width > self.CODE_W:
            code.scale_to_fit_width(self.CODE_W)
        if code.height > self.CODE_H:
            code.scale_to_fit_height(self.CODE_H)
        code.move_to(np.array([0.0, self.CODE_Y, 0.0]))
        return code

    def file_tab(self, name, panel):
        tab = Text(name, font="Menlo", font_size=17, color=GREY_B)
        tab.move_to(panel.get_corner(UL) + RIGHT * (1.1 + tab.width / 2) + DOWN * 0.3)
        return tab

    def caption_for(self, tex_str):
        cap = Tex(tex_str, font_size=30, color=self.COL_SUBTITLE)
        cap.move_to(np.array([0.0, -4.55, 0.0]))
        return cap

    def type_lines(self, code):
        """Typewriter effect: reveal each line's characters left to right."""
        anims = []
        for line in code.code_lines:
            n = len(line.submobjects)
            if n == 0:
                continue
            anims.append(
                ShowIncreasingSubsets(line, run_time=max(0.15, 0.014 * n),
                                      rate_func=linear)
            )
        self.play(
            FadeIn(code.line_numbers, run_time=0.4),
            LaggedStart(*anims, lag_ratio=0.7),
        )
        self.add(code.code_lines, code.line_numbers)

    # ── Scene ─────────────────────────────────────────────────────────────────
    def construct(self):
        # ── Title band ────────────────────────────────────────────────────────
        title = Tex("Build a Blockchain", color=self.COL_TITLE, font_size=68)
        subtitle = Tex(r"\textit{from scratch, in Python}",
                       color=self.COL_SUBTITLE, font_size=34)
        divider = Line(LEFT * 2.6, RIGHT * 2.6, color=self.COL_TITLE, stroke_width=2)

        title.to_edge(UP, buff=0.6)
        subtitle.next_to(title, DOWN, buff=0.25)
        divider.next_to(subtitle, DOWN, buff=0.25)

        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.2, rate_func=smooth)
        self.play(FadeIn(subtitle, shift=DOWN * 0.2), GrowFromCenter(divider), run_time=0.9)
        self.wait(0.4)

        # ── Code sections ─────────────────────────────────────────────────────
        panel = tab = header = caption = code = None
        for step_name, file_name, first_line, source, cap_text in self.SNIPPETS:
            new_code = self.make_code(source, first_line)
            new_header = Tex(step_name, color=WHITE, font_size=40)
            new_header.next_to(divider, DOWN, buff=0.5)
            new_tab = self.file_tab(file_name, new_code.background)
            new_caption = self.caption_for(cap_text)

            if panel is None:
                self.play(
                    FadeIn(new_header, shift=DOWN * 0.2),
                    DrawBorderThenFill(new_code.background),
                    FadeIn(new_tab),
                    run_time=1.1,
                )
            else:
                self.play(
                    FadeOut(code.code_lines, run_time=0.4),
                    FadeOut(code.line_numbers, run_time=0.4),
                    FadeOut(caption, run_time=0.4),
                    ReplacementTransform(header, new_header),
                    ReplacementTransform(panel, new_code.background),
                    ReplacementTransform(tab, new_tab),
                    run_time=0.7,
                )
            panel, tab, header, code = new_code.background, new_tab, new_header, new_code

            self.type_lines(new_code)
            caption = new_caption
            self.play(FadeIn(caption, shift=UP * 0.15), run_time=0.5)
            self.wait(1.4)

        # ── Finale: linked blocks diagram ─────────────────────────────────────
        final_header = Tex("The Chain", color=WHITE, font_size=40)
        final_header.next_to(divider, DOWN, buff=0.5)
        self.play(
            FadeOut(code.code_lines), FadeOut(code.line_numbers),
            FadeOut(panel), FadeOut(tab), FadeOut(caption),
            ReplacementTransform(header, final_header),
            run_time=0.8,
        )

        block_specs = [
            ("Block 0", "genesis", "8f3c2e9b…", GREY_A),
            ("Block 1", "Bob +5", "0000a1d4…", self.COL_OK),
            ("Block 2", "Carol +2", "0000f3a9…", self.COL_OK),
        ]
        blocks = VGroup()
        for name, data, hash_str, hash_col in block_specs:
            box = RoundedRectangle(
                width=2.45, height=1.7, corner_radius=0.12,
                stroke_color=self.COL_TITLE, stroke_width=1.5,
                fill_color=self.COL_BOX, fill_opacity=0.9,
            )
            lbl = Tex(name, font_size=28, color=WHITE)
            dat = Text(data, font="Menlo", font_size=15, color=self.COL_SUBTITLE)
            hsh = Text(hash_str, font="Menlo", font_size=15, color=hash_col)
            content = VGroup(lbl, dat, hsh).arrange(DOWN, buff=0.18)
            content.move_to(box.get_center())
            blocks.add(VGroup(box, content))
        blocks.arrange(RIGHT, buff=0.65)
        blocks.move_to(np.array([0.0, 0.8, 0.0]))

        arrows = VGroup()
        for i in (1, 2):
            arr = Arrow(
                start=blocks[i].get_left(), end=blocks[i - 1].get_right(),
                buff=0.06, color=self.COL_ACCENT, stroke_width=3.5,
                max_tip_length_to_length_ratio=0.35,
            )
            prev_lbl = Text("prev\nhash", font="Menlo", font_size=13,
                            line_spacing=0.7, color=self.COL_ACCENT)
            prev_lbl.next_to(arr, UP, buff=0.12)
            arrows.add(VGroup(arr, prev_lbl))

        diagram_cap = Tex(
            r"each block points at the previous hash ---\\tamper anywhere and the links shatter",
            font_size=30, color=self.COL_SUBTITLE,
        )
        diagram_cap.move_to(np.array([0.0, -1.2, 0.0]))

        self.play(LaggedStartMap(FadeIn, blocks, shift=UP * 0.25, lag_ratio=0.25), run_time=1.3)
        # explicit GrowArrow per arrow: LaggedStartMap unpacks each submobject
        # into positional args, which feeds the arrow tip in as point_color
        self.play(LaggedStart(GrowArrow(arrows[0][0]), GrowArrow(arrows[1][0]), lag_ratio=0.4),
                  FadeIn(arrows[0][1]), FadeIn(arrows[1][1]), run_time=1.0)
        self.play(FadeIn(diagram_cap, shift=UP * 0.15), run_time=0.6)
        self.wait(0.8)

        verdict = Text("chain.is_valid()  →  True ✓",
                       font="Menlo", font_size=30, color=self.COL_OK)
        verdict.move_to(np.array([0.0, -3.2, 0.0]))
        verdict_box = SurroundingRectangle(
            verdict, color=self.COL_OK, fill_color=self.COL_BOX,
            fill_opacity=0.6, buff=0.3, corner_radius=0.15, stroke_width=1.5,
        )
        self.play(FadeIn(verdict_box, shift=UP * 0.2), Write(verdict), run_time=1.1)
        self.play(Flash(verdict_box.get_corner(UR), color=self.COL_OK,
                        line_length=0.25, num_lines=10, flash_radius=0.45), run_time=0.7)
        self.wait(2.0)

        # ── Fade out ──────────────────────────────────────────────────────────
        everything = VGroup(
            title, subtitle, divider, final_header,
            blocks, arrows, diagram_cap, verdict, verdict_box,
        )
        self.play(FadeOut(everything, shift=DOWN * 0.3), run_time=1.3, rate_func=smooth)
        self.wait(0.4)
