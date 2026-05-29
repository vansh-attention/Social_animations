from manim import *
import numpy as np

config.pixel_height = 1920
config.pixel_width = 1080
config.frame_height = 16.0
config.frame_width = 9.0

class FirstPrinciple(Scene):
    def construct(self):
        # 3b1b inspired palette
        self.COLOR_CURVE = TEAL_C
        self.COLOR_SECANT = MAROON_C
        self.COLOR_TANGENT = YELLOW_C
        self.COLOR_DX = ORANGE
        self.COLOR_DY = GREEN_C
        self.COLOR_DERIV = MAROON_C
        self.COLOR_TEXT = WHITE
        
        self.show_first_principle()
        self.wait(1)
        self.clear_screen()
        self.wait(1)
        self.show_sin_example()

    def clear_screen(self):
        mobs = list(self.mobjects)
        if mobs:
            self.play(FadeOut(Group(*mobs)))
        self.clear()

    def show_first_principle(self):
        title = Tex("The Derivative from First Principles", font_size=42, color=self.COLOR_TEXT)
        title.to_edge(UP, buff=0.25)
        self.play(Write(title))
        
        # Graph centered horizontally, placed at the top like the second scene
        axes = Axes(
            x_range=[-0.5, 6, 1],
            y_range=[-0.5, 4, 1],
            x_length=7.5,
            y_length=5.5,
            axis_config={"include_numbers": False, "color": GREY_B},
        ).next_to(title, DOWN, buff=0.6)
        
        def func(x):
            return 0.15 * (x - 1)**2 + 0.5
            
        graph = axes.plot(func, color=self.COLOR_CURVE, x_range=[0, 5.5])
        graph_label = MathTex("f(x)", color=self.COLOR_CURVE, font_size=36).next_to(graph.get_end(), UP)
        
        self.play(Create(axes))
        self.play(Create(graph), Write(graph_label))
        self.wait(1)
        
        # Text is smaller and placed beautifully below the graph
        eq_title = Tex("Slope of secant:", font_size=32)
        
        lhs = MathTex("m =", font_size=36)
        num = MathTex("f(x+h) - f(x)", font_size=36)
        den = MathTex("h", font_size=36)
        frac_line = Line(LEFT, RIGHT, stroke_width=2).match_width(num).scale(1.1)
        frac = VGroup(num, frac_line, den).arrange(DOWN, buff=0.15)
        slope_eq = VGroup(lhs, frac).arrange(RIGHT, buff=0.2)
        
        limit_text = Tex(r"As $h \to 0$:", font_size=32)
        tangent_eq = MathTex(r"f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}", font_size=36)
        
        eq_group1 = VGroup(eq_title, slope_eq).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        eq_group2 = VGroup(limit_text, tangent_eq).arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        
        # Vertical arrangement, centered below the axes for 9:16 layout
        full_eq_group = VGroup(eq_group1, eq_group2).arrange(DOWN, buff=1.0, aligned_edge=LEFT)
        full_eq_group.next_to(axes, DOWN, buff=1.0)
        
        x_val = 1.5
        h_tracker = ValueTracker(3.0)
        
        def get_x(): return x_val
        def get_x_plus_h(): return x_val + h_tracker.get_value()
        def get_p(): return axes.c2p(get_x(), func(get_x()))
        def get_q(): return axes.c2p(get_x_plus_h(), func(get_x_plus_h()))
        
        dot_p = Dot(get_p(), color=self.COLOR_TANGENT, radius=0.08)
        dot_q = always_redraw(lambda: Dot(get_q(), color=self.COLOR_SECANT, radius=0.08))
        
        p_coord = always_redraw(lambda: MathTex(r"(x, f(x))", font_size=22, color=self.COLOR_TANGENT).next_to(dot_p, UL, buff=0.15))
        q_coord = always_redraw(lambda: MathTex(r"(x+h, f(x+h))", font_size=22, color=self.COLOR_SECANT).next_to(dot_q, UL, buff=0.15))
        
        x_line = DashedLine(axes.c2p(get_x(), 0), get_p(), color=GREY, stroke_width=2)
        x_label = MathTex("x", font_size=32).next_to(axes.c2p(get_x(), 0), DOWN)
        
        x_h_line = always_redraw(lambda: DashedLine(
            axes.c2p(get_x_plus_h(), 0), 
            axes.c2p(get_x_plus_h(), func(get_x_plus_h())), 
            color=GREY, stroke_width=2
        ))
        x_h_label = always_redraw(lambda: MathTex("x+h", font_size=32).next_to(axes.c2p(get_x_plus_h(), 0), DOWN))
        
        self.play(FadeIn(dot_p), Write(p_coord), Create(x_line), Write(x_label))
        self.play(FadeIn(dot_q), Write(q_coord), Create(x_h_line), Write(x_h_label))
        self.wait(1)
        
        dx_line = always_redraw(lambda: Line(
            get_p(), 
            axes.c2p(get_x_plus_h(), func(get_x())), 
            color=self.COLOR_DX, stroke_width=4
        ))
        dy_line = always_redraw(lambda: Line(
            axes.c2p(get_x_plus_h(), func(get_x())), 
            get_q(), 
            color=self.COLOR_DY, stroke_width=4
        ))
        
        dx_label = always_redraw(lambda: MathTex("h", color=self.COLOR_DX, font_size=32).next_to(dx_line, DOWN, buff=0.15))
        dy_label = always_redraw(lambda: MathTex("f(x+h) - f(x)", color=self.COLOR_DY, font_size=32).next_to(dy_line, RIGHT, buff=0.15))
        
        self.play(Create(dx_line), Write(dx_label))
        self.play(Create(dy_line), Write(dy_label))
        self.wait(1)
        
        def get_secant_line():
            p = get_p()
            q = get_q()
            vec = q - p
            norm = np.linalg.norm(vec)
            if norm < 1e-6:
                slope = 0.3 * (get_x() - 1)
                p1 = axes.c2p(get_x(), func(get_x()))
                p2 = axes.c2p(get_x() + 1, func(get_x()) + slope)
                vec = p2 - p1
                norm = np.linalg.norm(vec)
            if norm < 1e-6:
                direction = RIGHT
            else:
                direction = vec / norm
            
            # Ensure line always touches both points by centering at midpoint
            length = max(5.0, norm + 1.5)
            midpoint = (p + q) / 2
            return Line(midpoint - direction*(length/2), midpoint + direction*(length/2), color=self.COLOR_SECANT, stroke_width=3)
            
        secant_line = always_redraw(get_secant_line)
        self.play(Create(secant_line))
        self.wait(1)
        
        self.play(Write(eq_title))
        
        # Write "m =" and fraction line
        self.play(Write(lhs), Create(frac_line))
        self.wait(0.5)
        
        # Highlight y-coordinates and dy, then write numerator
        self.play(
            Indicate(q_coord, color=self.COLOR_SECANT),
            Indicate(p_coord, color=self.COLOR_TANGENT),
            Indicate(dy_label, color=self.COLOR_DY)
        )
        self.play(Write(num))
        self.wait(0.5)
        
        # Highlight x-coordinates and dx, then write denominator
        self.play(
            Indicate(q_coord, color=self.COLOR_SECANT),
            Indicate(p_coord, color=self.COLOR_TANGENT),
            Indicate(dx_label, color=self.COLOR_DX)
        )
        self.play(Write(den))
        self.wait(1.5)
        
        self.play(Write(limit_text))
        self.wait(1)
        
        self.play(
            FadeOut(dx_label), FadeOut(dy_label), FadeOut(x_h_label),
            FadeOut(p_coord), FadeOut(q_coord)
        )
        
        self.play(h_tracker.animate.set_value(0.001), run_time=6, rate_func=rate_functions.ease_out_expo)
        self.wait(1)
        
        self.play(Write(tangent_eq))
        
        secant_line.clear_updaters()
        dot_q.clear_updaters()
        
        final_tangent = get_secant_line().set_color(self.COLOR_TANGENT).set_stroke(width=4)
        self.play(Transform(secant_line, final_tangent), dot_q.animate.set_color(self.COLOR_TANGENT))
        
        box = SurroundingRectangle(tangent_eq, color=self.COLOR_TANGENT, buff=0.15, stroke_width=2, stroke_opacity=0.8, corner_radius=0.1)
        self.play(Create(box))
        self.wait(3)

    def show_sin_example(self):
        title = Tex("First Principle: $f(x) = \sin(x)$", font_size=38)
        title.to_edge(UP, buff=0.2)
        self.play(Write(title))
        
        # Larger axes adjusted for 9:16
        axes = Axes(
            x_range=[-0.5, 3.5, 1],
            y_range=[-1.5, 1.5, 1],
            x_length=6.5,
            y_length=4.5,
            axis_config={"include_numbers": False, "color": GREY_B},
        ).next_to(title, DOWN, buff=0.5)
        
        sin_curve = axes.plot(lambda x: np.sin(x), color=self.COLOR_CURVE, x_range=[0, 3.2])
        sin_label = MathTex(r"\sin(x)", color=self.COLOR_CURVE, font_size=28).next_to(axes.c2p(2.5, np.sin(2.5)), UR, buff=0.1)
        
        self.play(Create(axes))
        self.play(Create(sin_curve), Write(sin_label))
        self.wait(0.5)
        
        x_val = 0.5
        h_tracker = ValueTracker(2.0)
        
        def get_p(): return axes.c2p(x_val, np.sin(x_val))
        def get_q(): return axes.c2p(x_val + h_tracker.get_value(), np.sin(x_val + h_tracker.get_value()))
        
        dot_p = Dot(get_p(), color=self.COLOR_TANGENT, radius=0.06)
        dot_q = always_redraw(lambda: Dot(get_q(), color=self.COLOR_SECANT, radius=0.06))
        
        def get_secant_line():
            p = get_p()
            q = get_q()
            vec = q - p
            norm = np.linalg.norm(vec)
            if norm < 1e-6:
                slope = np.cos(x_val)
                p1 = axes.c2p(x_val, np.sin(x_val))
                p2 = axes.c2p(x_val + 1, np.sin(x_val) + slope)
                vec = p2 - p1
                norm = np.linalg.norm(vec)
            if norm < 1e-6:
                direction = RIGHT
            else:
                direction = vec / norm
            
            # Ensure line always touches both points by centering at midpoint
            length = max(3.2, norm + 1.0)
            midpoint = (p + q) / 2
            return Line(midpoint - direction*(length/2), midpoint + direction*(length/2), color=self.COLOR_SECANT, stroke_width=2)
            
        secant_line = always_redraw(get_secant_line)
        self.play(FadeIn(dot_p), FadeIn(dot_q), Create(secant_line))
        self.wait(0.5)
        
        # Smaller font sizes
        F_SIZE = 30
        eq1 = MathTex("f'(x)", "=", r"\lim_{h \to 0} \frac{\sin(x+h) - \sin(x)}{h}", font_size=F_SIZE)
        eq2 = MathTex("=", r"\lim_{h \to 0} \frac{\sin(x)\cos(h) + \cos(x)\sin(h) - \sin(x)}{h}", font_size=F_SIZE)
        eq3 = MathTex("=", r"\lim_{h \to 0} \left[ \sin(x)\frac{\cos(h)-1}{h} + \cos(x)\frac{\sin(h)}{h} \right]", font_size=F_SIZE)
        eq4 = MathTex("=", r"\sin(x)(0) + \cos(x)(1)", font_size=F_SIZE)
        eq5 = MathTex("=", r"\cos(x)", font_size=34, color=self.COLOR_TANGENT)
        
        # Adjusted buff between lines to utilize vertical space in 9:16
        eq_group = VGroup(eq1, eq2, eq3, eq4, eq5).arrange(DOWN, buff=0.4)
        eq_group.scale(0.95)
        
        for eq in [eq2, eq3, eq4, eq5]:
            shift_amount = eq1[1].get_left()[0] - eq[0].get_left()[0]
            eq.shift(RIGHT * shift_amount)
            
        eq_group.next_to(axes, DOWN, buff=0.75)
        
        self.play(Write(eq1))
        self.wait(0.5)
        self.play(Write(eq2))
        self.wait(0.5)
        self.play(Write(eq3))
        self.wait(1)
        
        self.play(h_tracker.animate.set_value(0.001), run_time=3, rate_func=smooth)
        
        secant_line.clear_updaters()
        dot_q.clear_updaters()
        final_tangent = get_secant_line().set_color(self.COLOR_TANGENT).set_stroke(width=3)
        self.play(Transform(secant_line, final_tangent), dot_q.animate.set_color(self.COLOR_TANGENT))
        self.wait(0.5)
        
        self.play(Write(eq4))
        self.wait(0.5)
        
        self.play(Write(eq5))
        self.wait(3)
