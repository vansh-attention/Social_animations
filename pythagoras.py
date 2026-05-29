from manim import *

class PythagorasProof(Scene):
    def construct(self):
        # Parameters
        a = 2.0
        b = 3.0
        s = a + b
        
        # Define the triangles
        def get_triangle(color):
            return Polygon(ORIGIN, RIGHT*b, UP*a, fill_opacity=0.6, color=WHITE, fill_color=color, stroke_width=2)
            
        t1 = get_triangle(RED_E).shift(LEFT * s/2 + DOWN * s/2)
        t2 = get_triangle(GREEN_E).rotate(PI/2, about_point=ORIGIN).shift(RIGHT * s/2 + DOWN * s/2)
        t3 = get_triangle(YELLOW_E).rotate(PI, about_point=ORIGIN).shift(RIGHT * s/2 + UP * s/2)
        t4 = get_triangle(PURPLE_E).rotate(-PI/2, about_point=ORIGIN).shift(LEFT * s/2 + UP * s/2)
        
        triangles = VGroup(t1, t2, t3, t4)
        
        # Large bounding square
        large_square = Square(side_length=s, color=WHITE, stroke_width=2).move_to(ORIGIN)
        
        # Inner square c^2
        c_square = Polygon(
            [-s/2+b, -s/2, 0], 
            [s/2, -s/2+b, 0], 
            [s/2-b, s/2, 0], 
            [-s/2, s/2-b, 0], 
            color=BLUE_C, fill_opacity=0.4, fill_color=BLUE_C
        )
        c_text = MathTex("c^2", font_size=56).move_to(c_square.get_center())
        c_group = VGroup(c_square, c_text)
        
        # Labels for one of the triangles (t1)
        a_label = MathTex("a").next_to(t1, LEFT, buff=0.1)
        b_label = MathTex("b").next_to(t1, DOWN, buff=0.1)
        midpoint = np.array([-s/2 + b/2, -s/2 + a/2, 0])
        c_label = MathTex("c").move_to(midpoint).shift(RIGHT*0.25 + UP*0.25)
        
        # Titles
        title = Tex("Pythagorean Theorem", font_size=48).to_edge(UP)
        formula = MathTex("a^2 + b^2 = c^2", font_size=60).to_edge(DOWN)
        
        # --- Animation Sequence ---
        self.play(Write(title))
        
        # Draw first triangle
        self.play(DrawBorderThenFill(t1))
        self.play(Write(a_label), Write(b_label), Write(c_label))
        self.wait(1)
        
        # Duplicate to form the square
        self.play(
            FadeIn(t2, shift=UP*0.5),
            FadeIn(t3, shift=DOWN*0.5),
            FadeIn(t4, shift=RIGHT*0.5),
        )
        self.play(Create(large_square))
        self.wait(1)
        
        # Highlight c^2
        self.play(FadeOut(c_label))
        self.play(DrawBorderThenFill(c_square), Write(c_text))
        self.wait(2)
        
        # Remove c^2 fill and text to make room for rearrangement
        self.play(FadeOut(c_group))
        
        # Rearrange
        self.play(
            t3.animate.shift(LEFT * a + DOWN * b),
            t4.animate.shift(RIGHT * b + DOWN * a),
            run_time=2,
            path_arc=0.5
        )
        self.wait(1)
        
        # Highlight a^2 and b^2
        a_square = Square(side_length=a, color=RED_C, fill_opacity=0.4, fill_color=RED_C).move_to([b/2, b/2, 0])
        a_text = MathTex("a^2", font_size=56).move_to(a_square.get_center())
        
        b_square = Square(side_length=b, color=GREEN_C, fill_opacity=0.4, fill_color=GREEN_C).move_to([-a/2, a/2, 0])
        b_text = MathTex("b^2", font_size=56).move_to(b_square.get_center())
        
        self.play(
            DrawBorderThenFill(a_square), Write(a_text),
            DrawBorderThenFill(b_square), Write(b_text)
        )
        self.wait(1)
        
        # Show final formula
        self.play(Write(formula))
        self.wait(3)
