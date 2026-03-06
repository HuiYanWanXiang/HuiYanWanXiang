from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Colors
        TRIANGLE_COLOR = BLUE
        SQUARE_A_COLOR = GREEN
        SQUARE_B_COLOR = YELLOW
        SQUARE_C_COLOR = RED
        TEXT_COLOR = WHITE
        
        # Triangle dimensions (scaled for visibility)
        a_val = 3
        b_val = 4
        c_val = 5
        scale = 0.8
        
        a = a_val * scale
        b = b_val * scale
        c = c_val * scale
        
        # Scene 1: Triangle Setup (3 seconds)
        # Create right triangle vertices
        B = ORIGIN
        A = UP * a
        C = RIGHT * b
        
        triangle = Polygon(A, B, C, color=TRIANGLE_COLOR, fill_opacity=0.3)
        
        # Right angle indicator
        right_angle = RightAngle(
            Line(B, A), Line(B, C),
            length=0.3, color=YELLOW
        )
        
        # Vertex labels
        label_A = MathTex(r"A", color=TEXT_COLOR).next_to(A, UP, buff=0.1)
        label_B = MathTex(r"B", color=TEXT_COLOR).next_to(B, DOWN + LEFT, buff=0.1)
        label_C = MathTex(r"C", color=TEXT_COLOR).next_to(C, RIGHT, buff=0.1)
        
        # Side labels
        side_a_label = MathTex(r"a", color=TEXT_COLOR).next_to(
            (A + B) / 2, LEFT, buff=0.1
        )
        side_b_label = MathTex(r"b", color=TEXT_COLOR).next_to(
            (B + C) / 2, DOWN, buff=0.1
        )
        side_c_label = MathTex(r"c", color=TEXT_COLOR).next_to(
            (A + C) / 2, UP + RIGHT, buff=0.1
        )
        
        # Animate triangle appearance
        self.play(Create(triangle), run_time=1)
        self.play(
            Create(right_angle),
            Write(label_A),
            Write(label_B),
            Write(label_C),
            run_time=1
        )
        self.play(
            Write(side_a_label),
            Write(side_b_label),
            Write(side_c_label),
            run_time=1
        )
        
        # Group triangle elements
        triangle_group = VGroup(
            triangle, right_angle,
            label_A, label_B, label_C,
            side_a_label, side_b_label, side_c_label
        )
        
        # Scene 2: Square Construction (4 seconds)
        # Square on side a (vertical)
        square_a = Square(side_length=a, color=SQUARE_A_COLOR, fill_opacity=0.3)
        square_a.next_to(Line(A, B), LEFT, buff=0)
        
        # Square on side b (horizontal)
        square_b = Square(side_length=b, color=SQUARE_B_COLOR, fill_opacity=0.3)
        square_b.next_to(Line(B, C), DOWN, buff=0)
        
        # Square on side c (hypotenuse)
        # Calculate angle of hypotenuse
        angle = np.arctan2(a, b)
        square_c = Square(side_length=c, color=SQUARE_C_COLOR, fill_opacity=0.3)
        square_c.rotate(angle)
        # Position so it shares the hypotenuse
        square_c.move_to(A + (C - A) / 2 + np.array([-a/2 * np.sin(angle), a/2 * np.cos(angle), 0]))
        
        # Area labels
        area_a_label = MathTex(r"a^2", color=TEXT_COLOR).move_to(square_a.get_center())
        area_b_label = MathTex(r"b^2", color=TEXT_COLOR).move_to(square_b.get_center())
        area_c_label = MathTex(r"c^2", color=TEXT_COLOR).move_to(square_c.get_center())
        
        # Animate squares appearing
        self.play(Create(square_a), Write(area_a_label), run_time=1)
        self.play(Create(square_b), Write(area_b_label), run_time=1)
        self.wait(0.5)
        self.play(Create(square_c), Write(area_c_label), run_time=1.5)
        self.wait(0.5)
        
        # Scene 3: Area Comparison (3 seconds)
        # Create copies for transformation
        square_a_copy = square_a.copy()
        square_b_copy = square_b.copy()
        square_c_copy = square_c.copy()
        
        # Position copies for transformation
        squares_combined = VGroup(square_a_copy, square_b_copy)
        squares_combined.move_to(ORIGIN)
        
        # Transform combined squares to hypotenuse square
        self.play(
            squares_combined.animate.move_to(square_c.get_center()),
            run_time=1.5
        )
        self.play(
            Transform(squares_combined, square_c_copy),
            run_time=1.5
        )
        self.wait(0.5)
        
        # Remove temporary copies
        self.remove(squares_combined, square_c_copy)
        
        # Scene 4: Equation Reveal (2 seconds)
        # Main equation
        equation = MathTex(r"a^2 + b^2 = c^2", color=YELLOW)
        equation.scale(1.2)
        equation.to_edge(DOWN, buff=0.8)
        
        # Numerical example
        example = MathTex(
            r"3^2 + 4^2 = 5^2",
            r"\quad\Rightarrow\quad",
            r"9 + 16 = 25",
            color=GREEN
        )
        example.next_to(equation, DOWN, buff=0.4)
        
        # Animate equation appearance
        self.play(Write(equation), run_time=1)
        self.play(Write(example), run_time=1)
        
        # Final hold
        self.wait(2)