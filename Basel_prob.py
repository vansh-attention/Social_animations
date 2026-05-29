from manim import *

MAGENTA = "#FF00FF"

# Set the resolution and aspect ratio for vertical video (1080x1920)
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 8.0
config.frame_height = 8.0 * (1920 / 1080)

class BaselProblem(Scene):
    def construct(self):
        # Step 1: The Problem
        problem = MathTex(r"\sum_{n=1}^{\infty} \frac{1}{n^2}", r"=", r"?")
        problem[0].set_color(BLUE)
        problem.scale(1.5)
        self.play(Write(problem), run_time=2)
        self.wait(1)
        
        problem_top = MathTex(r"\sum_{n=1}^{\infty} \frac{1}{n^2}", r"=", r"?").to_edge(UP, buff=1.5)
        problem_top[0].set_color(BLUE)
        self.play(Transform(problem, problem_top), run_time=1)
        
        # Step 2: Maclaurin series for sin(x)/x
        sin_series = MathTex(r"\frac{\sin(x)}{x} = 1 - ", r"\frac{x^2}{3!}", r" + \frac{x^4}{5!} - \cdots")
        sin_series[1].set_color(MAGENTA)
        
        self.play(Write(sin_series), run_time=3)
        self.wait(1)
        
        # Step 3: Product formula based on roots
        sin_product = MathTex(r"\frac{\sin(x)}{x} = \left(1 - ", r"\frac{x^2}{\pi^2}", r"\right)\left(1 - ", r"\frac{x^2}{4\pi^2}", r"\right)\cdots")
        sin_product[1].set_color(MAGENTA)
        sin_product[3].set_color(MAGENTA)
        sin_product.next_to(sin_series, DOWN, buff=1.5)
        self.play(Write(sin_product), run_time=3)
        self.wait(1)
        
        # Step 4: Equating coefficients of x^2
        equate_text = Text("Equating coefficients of ", font_size=36, color=BLUE)
        x2 = MathTex(r"x^2", font_size=48, color=MAGENTA)
        equate_group = VGroup(equate_text, x2).arrange(RIGHT)
        
        # Clear screen to make room
        self.play(
            FadeOut(sin_series),
            FadeOut(sin_product),
            FadeIn(equate_group),
            run_time=1
        )
        
        # Increase gap between equation of x^2 and summation sign
        self.play(equate_group.animate.next_to(problem_top, DOWN, buff=3.0), run_time=1)
        self.wait(1)
        
        # Coefficient from series
        coeff_series = MathTex(r"-\frac{1}{3!}")
        
        # Coefficient from product
        coeff_product = MathTex(r"-\left(\frac{1}{\pi^2} + \frac{1}{4\pi^2} + \frac{1}{9\pi^2} + \cdots\right)")
        coeff_product.set_color(MAGENTA)
        
        equation = VGroup(coeff_series, MathTex("="), coeff_product).arrange(RIGHT)
        equation.next_to(equate_group, DOWN, buff=1.5)
        
        self.play(Write(equation), run_time=3)
        self.wait(2)
        
        # Step 5: Final simplification
        simplify1 = MathTex(r"-\frac{1}{6} = -\frac{1}{\pi^2}\left(1 + \frac{1}{4} + \frac{1}{9} + \cdots\right)")
        simplify1.set_color(MAGENTA)
        simplify1.move_to(equation)
        
        self.play(Transform(equation, simplify1), run_time=2)
        self.wait(1)
        
        final_answer = MathTex(r"\sum_{n=1}^{\infty} \frac{1}{n^2}", r"=", r"\frac{\pi^2}{6}")
        final_answer[0].set_color(BLUE)
        final_answer[2].set_color(MAGENTA)
        final_answer.scale(1.5)
        final_answer.next_to(equate_group, DOWN, buff=1.5)
        
        self.play(
            FadeOut(equate_group),
            Transform(equation, final_answer),
            FadeOut(problem),
            run_time=3
        )
        self.wait(3)
