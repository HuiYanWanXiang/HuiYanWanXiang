from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Title
        title = MathTex(r"a^2 + b^2 = c^2", font_size=72)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        # Create right triangle
        triangle = Polygon(
            [-3, -2, 0],
            [2, -2, 0],
            [2, 1, 0],
            color=BLUE,
            stroke_width=6
        )
        triangle.shift(DOWN * 0.5)
        
        # Right angle indicator
        right_angle = RightAngle(
            Line([2, -2, 0], [2, 1, 0]),
            Line([2, -2, 0], [-3, -2, 0]),
            length=0.3,
            color=YELLOW,
            stroke_width=4
        )
        right_angle.shift(DOWN * 0.5)
        
        # Side labels
        side_a = MathTex(r"a", font_size=36)
        side_a.move_to([-0.5, -2.8, 0])
        
        side_b = MathTex(r"b", font_size=36)
        side_b.move_to([2.8, -0.5, 0])
        
        side_c = MathTex(r"c", font_size=36)
        side_c.move_to([-0.5, -0.5, 0])
        side_c.rotate(angle=PI/6)
        
        # Animate triangle
        self.play(Create(triangle), Create(right_angle))
        self.wait(0.3)
        
        # Animate labels
        self.play(
            Write(side_a),
            Write(side_b),
            Write(side_c)
        )
        self.wait(0.7)
        
        # Create squares on each side
        square_a = Square(side_length=3, color=RED)
        square_a.move_to([-4.5, -3.5, 0])
        label_a2 = MathTex(r"a^2", font_size=32, color=RED)
        label_a2.move_to(square_a.get_center())
        
        square_b = Square(side_length=2, color=GREEN)
        square_b.move_to([4.5, -2.5, 0])
        label_b2 = MathTex(r"b^2", font_size=32, color=GREEN)
        label_b2.move_to(square_b.get_center())
        
        # Calculate side length for square_c (hypotenuse length = sqrt(3^2 + 5^2) = sqrt(34))
        side_c_length = np.sqrt(34)
        square_c = Square(side_length=side_c_length, color=PURPLE)
        square_c.move_to([0, 2, 0])
        square_c.rotate(np.arctan(3/5))
        label_c2 = MathTex(r"c^2", font_size=32, color=PURPLE)
        label_c2.move_to(square_c.get_center())
        
        # Animate squares
        self.play(
            Create(square_a),
            Write(label_a2),
            run_time=1
        )
        self.wait(0.2)
        
        self.play(
            Create(square_b),
            Write(label_b2),
            run_time=1
        )
        self.wait(0.2)
        
        self.play(
            Create(square_c),
            Write(label_c2),
            run_time=1
        )
        self.wait(0.5)
        
        # Show equation with colors - FIXED: Use separate colored parts instead of \textcolor
        equation = VGroup(
            MathTex(r"a^2", color=RED, font_size=48),
            MathTex(r"+", font_size=48),
            MathTex(r"b^2", color=GREEN, font_size=48),
            MathTex(r"=", font_size=48),
            MathTex(r"c^2", color=PURPLE, font_size=48)
        ).arrange(RIGHT, buff=0.2)
        equation.next_to(title, DOWN, buff=0.8)
        
        self.play(Write(equation))
        self.wait(1)
        
        # Visual proof animation
        self.play(
            square_a.animate.move_to(square_c.get_center()),
            label_a2.animate.move_to(square_c.get_center()),
            run_time=1.5
        )
        self.wait(0.3)
        
        self.play(
            square_b.animate.move_to(square_c.get_center()),
            label_b2.animate.move_to(square_c.get_center()),
            run_time=1.5
        )
        self.wait(0.5)
        
        # Final emphasis
        box = SurroundingRectangle(equation, color=YELLOW, buff=0.2)
        self.play(Create(box))
        self.wait(1.5)
        
        # Fade out
        self.play(
            FadeOut(triangle),
            FadeOut(right_angle),
            FadeOut(side_a),
            FadeOut(side_b),
            FadeOut(side_c),
            FadeOut(square_a),
            FadeOut(square_b),
            FadeOut(square_c),
            FadeOut(label_a2),
            FadeOut(label_b2),
            FadeOut(label_c2),
            FadeOut(box),
            run_time=0.8
        )
        
        # Keep title and equation
        self.wait(1)