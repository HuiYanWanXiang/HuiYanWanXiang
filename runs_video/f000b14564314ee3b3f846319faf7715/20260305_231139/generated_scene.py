from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Colors
        TRIANGLE_COLOR = WHITE
        SQUARE_A_COLOR = BLUE
        SQUARE_B_COLOR = GREEN
        SQUARE_C_COLOR = RED
        TEXT_COLOR = WHITE
        
        # Layout parameters
        TRIANGLE_HEIGHT = 2.5
        TRIANGLE_POSITION = ORIGIN
        EQUATION_POSITION = DOWN * 2.5
        
        # Scene 1: Triangle Introduction (3.0s)
        # Create right triangle
        triangle_points = [
            LEFT * 1.5 + DOWN * 1,  # A (bottom left)
            RIGHT * 2 + DOWN * 1,    # B (bottom right)
            LEFT * 1.5 + UP * 1.5,   # C (top left, right angle)
        ]
        
        triangle = Polygon(*triangle_points, color=TRIANGLE_COLOR, stroke_width=6)
        
        # Right angle symbol
        right_angle = RightAngle(
            Line(triangle_points[2], triangle_points[0]),
            Line(triangle_points[2], triangle_points[1]),
            length=0.3,
            color=YELLOW,
            stroke_width=4
        )
        
        # Vertex labels
        label_A = MathTex(r"A", color=TEXT_COLOR).next_to(triangle_points[0], DOWN + LEFT, buff=0.15)
        label_B = MathTex(r"B", color=TEXT_COLOR).next_to(triangle_points[1], DOWN + RIGHT, buff=0.15)
        label_C = MathTex(r"C", color=TEXT_COLOR).next_to(triangle_points[2], UP + LEFT, buff=0.15)
        
        # Side labels
        side_a = MathTex(r"a", color=TEXT_COLOR).next_to(
            Line(triangle_points[2], triangle_points[0]).get_center(), LEFT, buff=0.15
        )
        side_b = MathTex(r"b", color=TEXT_COLOR).next_to(
            Line(triangle_points[0], triangle_points[1]).get_center(), DOWN, buff=0.15
        )
        side_c = MathTex(r"c", color=TEXT_COLOR).next_to(
            Line(triangle_points[2], triangle_points[1]).get_center(), UP + RIGHT, buff=0.15
        )
        
        # Animate triangle drawing
        self.play(Create(triangle), run_time=1.5)
        self.play(Create(right_angle), run_time=0.5)
        self.play(
            Write(label_A),
            Write(label_B),
            Write(label_C),
            run_time=1.0
        )
        self.play(
            Write(side_a),
            Write(side_b),
            Write(side_c),
            run_time=1.0
        )
        self.wait(0.5)
        
        # Group triangle elements
        triangle_group = VGroup(triangle, right_angle, label_A, label_B, label_C, side_a, side_b, side_c)
        
        # Scene 2: Construct Squares (3.0s)
        # Get side lengths from triangle
        side_a_vec = triangle_points[2] - triangle_points[0]
        side_b_vec = triangle_points[1] - triangle_points[0]
        side_c_vec = triangle_points[1] - triangle_points[2]
        
        # Square on side a (vertical)
        square_a = Square(side_length=np.linalg.norm(side_a_vec), color=SQUARE_A_COLOR, stroke_width=4)
        square_a.move_to(triangle_points[0] + side_a_vec/2 + LEFT * np.linalg.norm(side_a_vec)/2)
        square_a.set_fill(SQUARE_A_COLOR, opacity=0.3)
        
        # Square on side b (horizontal)
        square_b = Square(side_length=np.linalg.norm(side_b_vec), color=SQUARE_B_COLOR, stroke_width=4)
        square_b.move_to(triangle_points[0] + side_b_vec/2 + DOWN * np.linalg.norm(side_b_vec)/2)
        square_b.set_fill(SQUARE_B_COLOR, opacity=0.3)
        
        # Square on hypotenuse c (rotated)
        square_c = Square(side_length=np.linalg.norm(side_c_vec), color=SQUARE_C_COLOR, stroke_width=4)
        # Rotate to align with hypotenuse
        angle = np.arctan2(side_c_vec[1], side_c_vec[0])
        square_c.rotate(angle - PI/4)  # Square's diagonal aligns with hypotenuse
        square_c.move_to(triangle_points[2] + side_c_vec/2)
        square_c.set_fill(SQUARE_C_COLOR, opacity=0.3)
        
        # Area labels
        label_a2 = MathTex(r"a^2", color=TEXT_COLOR).move_to(square_a.get_center())
        label_b2 = MathTex(r"b^2", color=TEXT_COLOR).move_to(square_b.get_center())
        label_c2 = MathTex(r"c^2", color=TEXT_COLOR).move_to(square_c.get_center())
        
        # Animate squares
        self.play(
            Create(square_a),
            Create(square_b),
            Create(square_c),
            run_time=1.5
        )
        self.play(
            Write(label_a2),
            Write(label_b2),
            Write(label_c2),
            run_time=1.0
        )
        self.wait(0.5)
        
        # Group squares
        squares_group = VGroup(square_a, square_b, square_c, label_a2, label_b2, label_c2)
        
        # Scene 3: Equation Reveal (2.0s)
        # Fade out squares, keep triangle
        self.play(
            FadeOut(squares_group),
            triangle_group.animate.move_to(TRIANGLE_POSITION).scale_to_fit_height(TRIANGLE_HEIGHT),
            run_time=0.5
        )
        
        # Create equation
        equation = MathTex(r"a^2", r"+", r"b^2", r"=", r"c^2", color=TEXT_COLOR)
        equation.scale(1.5)
        equation.move_to(EQUATION_POSITION)
        
        # Color terms
        equation[0].set_color(SQUARE_A_COLOR)  # a²
        equation[2].set_color(SQUARE_B_COLOR)  # b²
        equation[4].set_color(SQUARE_C_COLOR)  # c²
        
        # Animate equation
        self.play(Write(equation), run_time=1.5)
        self.wait(0.5)
        
        # Scene 4: Visual Proof (4.0s)
        # Bring back squares
        self.play(
            FadeIn(squares_group),
            FadeOut(equation),
            run_time=0.5
        )
        
        # Create pieces for rearrangement
        # For simplicity, we'll animate the squares moving to show equivalence
        # In a more detailed proof, we would dissect the squares
        
        # Move squares to show a² + b² = c²
        target_pos = ORIGIN
        
        # Position squares to show equivalence
        square_a_target = square_a.copy().move_to(target_pos + LEFT * 2)
        square_b_target = square_b.copy().move_to(target_pos + RIGHT * 2)
        square_c_target = square_c.copy().move_to(target_pos)
        
        # Animate movement
        self.play(
            square_a.animate.move_to(square_a_target.get_center()),
            square_b.animate.move_to(square_b_target.get_center()),
            square_c.animate.move_to(square_c_target.get_center()),
            label_a2.animate.move_to(square_a_target.get_center()),
            label_b2.animate.move_to(square_b_target.get_center()),
            label_c2.animate.move_to(square_c_target.get_center()),
            run_time=1.5
        )
        
        # Show plus and equals signs
        plus_sign = MathTex(r"+", color=WHITE).scale(1.5).move_to(ORIGIN + LEFT * 0.5)
        equals_sign = MathTex(r"=", color=WHITE).scale(1.5).move_to(ORIGIN + RIGHT * 0.5)
        
        self.play(
            Write(plus_sign),
            Write(equals_sign),
            run_time=0.5
        )
        
        # Animate a² and b² combining into c²
        self.play(
            square_a.animate.move_to(square_c_target.get_center()).set_opacity(0.5),
            square_b.animate.move_to(square_c_target.get_center()).set_opacity(0.5),
            label_a2.animate.move_to(square_c_target.get_center() + UP * 0.3),
            label_b2.animate.move_to(square_c_target.get_center() + DOWN * 0.3),
            run_time=1.5
        )
        
        # Highlight final fit
        self.play(
            square_c.animate.set_stroke(width=8).set_fill(opacity=0.5),
            label_c2.animate.scale(1.3),
            run_time=0.5
        )
        
        self.wait(1.0)