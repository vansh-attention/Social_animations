from manim import *

class TestMathTex(Scene):
    def construct(self):
        slope_eq = MathTex(
            "m =", 
            "\\frac{",
            "f(x+h) - f(x)", 
            "}{",
            "h", 
            "}"
        )
        print("Number of submobjects in slope_eq:", len(slope_eq))
        for i, sub in enumerate(slope_eq):
            print(f"Submobject {i} has {len(sub)} parts")

if __name__ == "__main__":
    scene = TestMathTex()
    scene.construct()
