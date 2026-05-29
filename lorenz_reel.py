from manim import *
import numpy as np

class LorenzAttractor(ThreeDScene):
    def construct(self):
        # 1. Background color
        self.camera.background_color = BLACK

        # 2. Add Title and Lorenz Equations (Scaled up for better visibility)
        title = Tex(r"\textbf{Lorenz-Attractor}").scale(1.7)
        eq_text = MathTex(
            r"\frac{dx}{dt} &= \sigma(y - x)\\[1ex]",
            r"\frac{dy}{dt} &= x(\rho - z) - y\\[1ex]",
            r"\frac{dz}{dt} &= xy - \beta z"
        ).scale(1.1)
        eq_text[0].set_color(BLUE_A)
        
        # Add to fixed frame
        self.add_fixed_in_frame_mobjects(title, eq_text)
        
        # ABSOLUTE POSITIONING
        title.move_to(np.array([0, 6.0, 0]))
        eq_text.move_to(np.array([0, -5.0, 0]))

        # 3. Create 3D Axes (Lengths increased by ~1.3x)
        axes = ThreeDAxes(
            x_range=[-30, 30, 10],
            y_range=[-30, 30, 10],
            z_range=[0, 60, 10],
            x_length=5.2,
            y_length=5.2,
            z_length=6.5
        )
        axes.shift(IN * 0.8)  
        axes.set_color(GRAY_D)
        axes.set_opacity(0.3)

        # 4. Compute Lorenz Attractor points
        sigma = 10.0
        rho = 28.0
        beta = 8.0 / 3.0
        dt = 0.01
        num_steps = 1800 
        
        def lorenz(x, y, z):
            dx = sigma * (y - x)
            dy = x * (rho - z) - y
            dz = x * y - beta * z
            return np.array([dx, dy, dz])

        points = [np.array([0.0, 1.0, 1.05])]
        for _ in range(num_steps):
            dp = lorenz(*points[-1]) * dt
            points.append(points[-1] + dp)
            
        mapped_points = [axes.coords_to_point(p[0], p[1], p[2]) for p in points]

        # 5. Create glowing stream effect segment-by-segment
        stream_group = VGroup()
        
        # Stroke widths also enlarged by ~1.3x to preserve the glowing ratio
        glow_parameters = [
            (1.0, 1.5), # Core bright line
            (0.5, 4.0), # First inner glow
            (0.2, 8.0), # Second outer glow
            (0.1, 13.0) # Faint outer aura
        ]
        
        color_left = ManimColor("#FF1493")  # Pink/Magenta
        color_right = ManimColor("#00FFFF") # Cyan
        
        for i in range(len(mapped_points) - 1):
            p1 = mapped_points[i]
            p2 = mapped_points[i+1]
            
            raw_x = points[i][0]
            safe_x = np.clip(-raw_x, -50, 50)
            alpha = 1 / (1 + np.exp(safe_x))
            
            c = interpolate_color(color_left, color_right, alpha)
            
            segment_group = VGroup()
            for opacity, width in glow_parameters:
                line = Line(p1, p2, stroke_width=width, stroke_opacity=opacity, color=c)
                segment_group.add(line)
            
            stream_group.add(segment_group)

        # 6. Create the pointer (Radius enlarged from 0.08 to 0.12)
        pointer = Sphere(radius=0.12).set_color(WHITE)
        pointer.move_to(mapped_points[0])
        
        tracker = ValueTracker(0)
        
        def update_pointer(mob):
            idx = int(tracker.get_value())
            if idx < len(mapped_points):
                mob.move_to(mapped_points[idx])
        
        pointer.add_updater(update_pointer)

        # 7. Set Camera Orientation
        self.set_camera_orientation(phi=70 * DEGREES, theta=30 * DEGREES)

        # 8. Animation Sequence
        self.play(Write(title), Write(eq_text), run_time=1.5)
        self.play(Create(axes), run_time=1.5)
        
        self.add(pointer)
        self.begin_ambient_camera_rotation(rate=0.15)
        
        self.play(
            Create(stream_group, lag_ratio=1),
            tracker.animate.set_value(len(mapped_points) - 1),
            run_time=20, 
            rate_func=linear
        )
        
        pointer.remove_updater(update_pointer)
        
        self.wait(5)
        self.stop_ambient_camera_rotation()
        
        self.play(FadeOut(stream_group), FadeOut(pointer), FadeOut(axes), FadeOut(eq_text), FadeOut(title), run_time=2)
