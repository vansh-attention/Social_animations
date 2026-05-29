from manim import *
import numpy as np

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16

class BaselProblem(Scene):
    def construct(self):
        # ---------------------------------------------------------
        # 3Blue1Brown Aesthetic Constraints & Camera Configuration
        # ---------------------------------------------------------
        self.camera.background_color = "#0F0F0F"

        # Core Palette
        TEXT_COLOR = "#ECEFF1"
        LIGHT_BLUE = "#58ACFA"
        YELLOW_GOLD = "#E6C229"
        LIGHT_GREEN = "#A6E22E"

        # =========================================================
        # 1. THE RIGOROUS SETUP (0-15s)
        # =========================================================
        
        # Center the core target equation at the top
        target_eq = MathTex(
            "\\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}",
            color=TEXT_COLOR
        ).scale(1.2).shift(UP * 6)
        
        self.play(Write(target_eq), run_time=1.5)

        # Fade in a horizontal x-axis line at y=0. Place an observer at the origin (0,0).
        axis = NumberLine(
            x_range=[-5, 5, 1],
            length=8,
            color=LIGHT_BLUE,
            include_numbers=False,
        ).shift(DOWN * 2)
        
        observer = Dot(axis.n2p(0), color=YELLOW_GOLD, radius=0.15)
        observer_label = Tex("Observer", color=YELLOW_GOLD, font_size=28).next_to(observer, DOWN)

        self.play(Create(axis), FadeIn(observer), FadeIn(observer_label))

        # Place a light source at x = 1. Show its distance vector labeled d=1.
        light_1 = Dot(axis.n2p(1), color=LIGHT_GREEN, radius=0.1)
        dist_vector_1 = Line(axis.n2p(0), axis.n2p(1), color=LIGHT_GREEN, stroke_width=4)
        dist_label_1 = MathTex("d=1", color=LIGHT_GREEN, font_size=28).next_to(dist_vector_1, UP, buff=0.1)
        
        self.play(FadeIn(light_1), Create(dist_vector_1), Write(dist_label_1))

        # Write the absolute intensity equation near the observer
        intensity_eq = MathTex("I = \\frac{1}{d^2}", color=TEXT_COLOR).next_to(observer_label, DOWN, buff=0.5)
        self.play(Write(intensity_eq))

        # Animate a point moving to x = 2, showing its distance scaling
        dist_label_2 = MathTex("d=2", color=LIGHT_GREEN, font_size=28).next_to(axis.n2p(1), UP, buff=0.1)
        intensity_eq_2 = MathTex("I = \\frac{1}{4}", color=TEXT_COLOR).next_to(observer_label, DOWN, buff=0.5)
        
        self.play(
            light_1.animate.move_to(axis.n2p(2)),
            dist_vector_1.animate.put_start_and_end_on(axis.n2p(0), axis.n2p(2)),
            Transform(dist_label_1, dist_label_2),
            Transform(intensity_eq, intensity_eq_2),
            run_time=1.5
        )
        self.wait(0.5)

        # Add the infinite sequence of points along the positive and negative integer line
        lights_pos = VGroup(*[Dot(axis.n2p(n), color=LIGHT_GREEN, radius=0.08) for n in range(1, 5)])
        lights_neg = VGroup(*[Dot(axis.n2p(-n), color=LIGHT_GREEN, radius=0.08) for n in range(1, 5)])
        dots_pos = MathTex("\\dots", color=LIGHT_GREEN).next_to(axis.n2p(4.5), RIGHT, buff=0.1)
        dots_neg = MathTex("\\dots", color=LIGHT_GREEN).next_to(axis.n2p(-4.5), LEFT, buff=0.1)

        total_intensity = MathTex("E = 2 \\cdot \\sum_{n=1}^{\\infty} \\frac{1}{n^2}", color=YELLOW_GOLD)
        total_intensity.next_to(intensity_eq, DOWN, buff=0.5)

        self.play(
            FadeOut(light_1), FadeOut(dist_vector_1), FadeOut(dist_label_1),
            FadeIn(lights_pos), FadeIn(lights_neg), FadeIn(dots_pos), FadeIn(dots_neg),
            ReplacementTransform(intensity_eq, total_intensity),
            run_time=1.5
        )
        self.wait(1)

        # =========================================================
        # 2. THE COTANGENT IDENTITY GEOMETRY (15-35s)
        # =========================================================
        self.play(
            FadeOut(axis), FadeOut(observer), FadeOut(observer_label),
            FadeOut(lights_pos), FadeOut(lights_neg), FadeOut(dots_pos), FadeOut(dots_neg),
            FadeOut(total_intensity)
        )

        # Single right-angled triangle
        triangle_origin = DOWN * 1.5 + LEFT * 1.5
        v_line = Line(triangle_origin, triangle_origin + UP * 3, color=LIGHT_BLUE)
        h_line = Line(triangle_origin, triangle_origin + RIGHT * 4, color=LIGHT_GREEN)
        hyp_line = Line(triangle_origin + RIGHT * 4, triangle_origin + UP * 3, color=YELLOW_GOLD)

        v_label = MathTex("1", color=LIGHT_BLUE).next_to(v_line, LEFT)
        
        # Angle \theta
        angle_theta = MathTex("\\theta", color=TEXT_COLOR, font_size=32).move_to(triangle_origin + UP * 2.1 + RIGHT * 0.3)
        arc = ArcBetweenPoints(
            triangle_origin + UP * 2.3, 
            triangle_origin + UP * 3 + DOWN * 0.7 * 3/5 + RIGHT * 0.7 * 4/5, 
            angle=-PI/4, 
            color=TEXT_COLOR
        )
        
        self.play(Create(v_line), Write(v_label))
        self.play(Create(h_line), Create(hyp_line))
        self.play(Create(arc), Write(angle_theta))

        # Base length morphing & cot(\theta) label
        cot_label = MathTex("d = \\cot(\\theta)", color=LIGHT_GREEN).next_to(h_line, DOWN)
        self.play(Write(cot_label))

        csc_label = MathTex("\\csc(\\theta)", color=YELLOW_GOLD)
        csc_label.next_to(hyp_line.get_center(), UP+RIGHT, buff=0.1).shift(LEFT * 0.2)
        self.play(Write(csc_label))

        # Map the brightness mathematically
        prompt_id = MathTex("\\frac{1}{d^2} = \\frac{1}{\\cot^2(\\theta)}", color=TEXT_COLOR).shift(DOWN * 3.5)
        self.play(Write(prompt_id))
        self.wait(1.5)

        self.play(
            FadeOut(v_line), FadeOut(h_line), FadeOut(hyp_line), FadeOut(v_label), 
            FadeOut(cot_label), FadeOut(csc_label), FadeOut(arc), FadeOut(angle_theta),
            FadeOut(prompt_id)
        )

        # =========================================================
        # 3. THE CIRCULAR TRANSFORMATION (35-50s)
        # =========================================================
        
        # Smoothly warp into a perfect circle
        circle = Circle(radius=2.5, color=LIGHT_BLUE).shift(UP * 0.5)
        origin_pt = Dot(circle.get_bottom(), color=YELLOW_GOLD, radius=0.12)
        
        self.play(Create(circle), FadeIn(origin_pt))

        angles_eq = MathTex("\\theta_n = \\frac{n\\pi}{N}", color=LIGHT_GREEN).next_to(circle, UP, buff=0.4)
        self.play(Write(angles_eq))

        # Map to discrete angles on perimeter
        circle_dots = VGroup()
        center = circle.get_center()
        for i in range(1, 8):
            theta = i * PI / 15
            pt_pos = center + np.array([2.5 * np.cos(-PI/2 + theta), 2.5 * np.sin(-PI/2 + theta), 0])
            pt_neg = center + np.array([2.5 * np.cos(-PI/2 - theta), 2.5 * np.sin(-PI/2 - theta), 0])
            circle_dots.add(Dot(pt_pos, color=LIGHT_GREEN, radius=0.08))
            circle_dots.add(Dot(pt_neg, color=LIGHT_GREEN, radius=0.08))

        self.play(FadeIn(circle_dots), lag_ratio=0.1, run_time=1.5)

        # Algebraic identity
        sum_cot = MathTex(
            "\\sum_{k=1}^{m} \\cot^2\\left(\\frac{k\\pi}{2m+1}\\right)", 
            "=", 
            "\\frac{m(2m-1)}{3}",
            color=TEXT_COLOR
        ).scale(0.85).shift(DOWN * 3)
        
        self.play(Write(sum_cot))
        self.wait(1.5)

        # =========================================================
        # 4. THE LIMIT & THE CLIMAX (50-60s)
        # =========================================================
        
        limit_text = MathTex("m \\to \\infty", color=YELLOW_GOLD).next_to(sum_cot, DOWN, buff=0.4)
        self.play(Write(limit_text))

        sub_text = MathTex("\\cot(\\theta) \\approx \\frac{1}{\\theta}", color=LIGHT_BLUE).next_to(limit_text, DOWN, buff=0.3)
        self.play(Write(sub_text))
        self.wait(1.5)

        # Animate the algebraic terms grouping, cancelling out
        limit_sum = MathTex(
            "\\sum_{n=1}^{\\infty} \\frac{1}{(n\\pi)^2}",
            "=",
            "\\frac{1}{6}",
            color=TEXT_COLOR
        ).scale(1.1).shift(DOWN * 3)

        self.play(
            FadeOut(circle), FadeOut(origin_pt), FadeOut(circle_dots), FadeOut(angles_eq),
            ReplacementTransform(sum_cot, limit_sum),
            FadeOut(limit_text), FadeOut(sub_text),
            run_time=1.5
        )
        self.wait(1)

        # Factor out \pi^2 dynamically using TransformMatchingShapes
        # We'll use ReplacementTransform as a safe, smooth fallback to simulate the isolation
        final_eq = MathTex(
            "\\sum_{n=1}^{\\infty} \\frac{1}{n^2}",
            "=",
            "\\frac{\\pi^2}{6}",
            color=TEXT_COLOR
        ).scale(1.2).shift(DOWN * 3)

        self.play(ReplacementTransform(limit_sum, final_eq), run_time=1.5)
        
        # Surround in a clean, elegant gold bounding box
        box = SurroundingRectangle(final_eq, color=YELLOW_GOLD, buff=0.25, stroke_width=3)
        self.play(Create(box))
        
        self.wait(3)
