from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Colors
        TRIANGLE_COLOR = WHITE
        SQUARE_A_COLOR = BLUE_D
        SQUARE_B_COLOR = GREEN_D
        SQUARE_C_COLOR = YELLOW_D
        HIGHLIGHT_COLOR = YELLOW
        
        # Layout parameters
        TRIANGLE_HEIGHT = 3.0
        TRIANGLE_BASE = 4.0
        TRIANGLE_HYP = 5.0
        
        # Scale factor for squares
        SQUARE_SCALE = 0.8
        
        # Scene 1: Triangle Introduction (3 seconds)
        # Create right triangle
        triangle = Polygon(
            ORIGIN,
            [TRIANGLE_BASE, 0, 0],
            [0, TRIANGLE_HEIGHT, 0],
            color=TRIANGLE_COLOR,
            stroke_width=6
        )
        triangle.move_to(ORIGIN)
        
        # Labels for vertices
        vertex_labels = VGroup(
            MathTex(r"A", font_size=36).next_to(triangle.get_vertices()[0], DOWN + LEFT, buff=0.1),
            MathTex(r"B", font_size=36).next_to(triangle.get_vertices()[1], DOWN + RIGHT, buff=0.1),
            MathTex(r"C", font_size=36).next_to(triangle.get_vertices()[2], UP + LEFT, buff=0.1)
        )
        
        # Side labels
        side_a_label = MathTex(r"a", font_size=32).next_to(
            Line(triangle.get_vertices()[0], triangle.get_vertices()[2]).get_center(),
            LEFT, buff=0.2
        )
        side_b_label = MathTex(r"b", font_size=32).next_to(
            Line(triangle.get_vertices()[0], triangle.get_vertices()[1]).get_center(),
            DOWN, buff=0.2
        )
        side_c_label = MathTex(r"c", font_size=32).next_to(
            Line(triangle.get_vertices()[1], triangle.get_vertices()[2]).get_center(),
            UP + RIGHT, buff=0.2
        )
        
        # Right angle symbol
        right_angle = RightAngle(
            Line(triangle.get_vertices()[0], triangle.get_vertices()[1]),
            Line(triangle.get_vertices()[0], triangle.get_vertices()[2]),
            length=0.3,
            color=YELLOW
        )
        
        # Animate triangle drawing
        self.play(Create(triangle), run_time=1.5)
        self.play(
            Write(vertex_labels),
            Write(side_a_label),
            Write(side_b_label),
            Write(side_c_label),
            run_time=1.0
        )
        self.play(Create(right_angle), run_time=0.5)
        self.wait(0.5)
        
        # Scene 2: Square Construction (3 seconds)
        # Create squares on each side
        square_a = Square(side_length=TRIANGLE_HEIGHT * SQUARE_SCALE, color=SQUARE_A_COLOR, fill_opacity=0.3)
        square_a.next_to(Line(triangle.get_vertices()[0], triangle.get_vertices()[2]), LEFT, buff=0)
        
        square_b = Square(side_length=TRIANGLE_BASE * SQUARE_SCALE, color=SQUARE_B_COLOR, fill_opacity=0.3)
        square_b.next_to(Line(triangle.get_vertices()[0], triangle.get_vertices()[1]), DOWN, buff=0)
        
        square_c = Square(side_length=TRIANGLE_HYP * SQUARE_SCALE, color=SQUARE_C_COLOR, fill_opacity=0.3)
        # Position square_c relative to hypotenuse
        hyp_center = Line(triangle.get_vertices()[1], triangle.get_vertices()[2]).get_center()
        square_c.move_to(hyp_center + np.array([0.5, -0.5, 0]) * SQUARE_SCALE)
        
        # Area labels
        area_a_label = MathTex(r"a^2", font_size=28, color=SQUARE_A_COLOR).move_to(square_a)
        area_b_label = MathTex(r"b^2", font_size=28, color=SQUARE_B_COLOR).move_to(square_b)
        area_c_label = MathTex(r"c^2", font_size=28, color=SQUARE_C_COLOR).move_to(square_c)
        
        # Animate squares
        self.play(
            Create(square_a),
            Create(square_b),
            Create(square_c),
            run_time=1.5
        )
        self.play(
            Write(area_a_label),
            Write(area_b_label),
            Write(area_c_label),
            run_time=1.0
        )
        self.wait(0.5)
        
        # Scene 3: Area Comparison (3 seconds)
        # Create equation
        equation = MathTex(r"a^2", "+", r"b^2", "=", r"c^2", font_size=40)
        equation.next_to(triangle, DOWN, buff=1.0)
        
        # Highlight squares
        highlight_a = square_a.copy().set_color(HIGHLIGHT_COLOR).set_stroke(width=3)
        highlight_b = square_b.copy().set_color(HIGHLIGHT_COLOR).set_stroke(width=3)
        highlight_c = square_c.copy().set_color(HIGHLIGHT_COLOR).set_stroke(width=3)
        
        self.play(
            Create(highlight_a),
            Create(highlight_b),
            run_time=0.5
        )
        self.play(
            Write(equation[0:3]),  # a^2 + b^2
            run_time=0.5
        )
        self.play(
            Write(equation[3]),  # =
            run_time=0.25
        )
        self.play(
            Create(highlight_c),
            run_time=0.5
        )
        self.play(
            Write(equation[4]),  # c^2
            run_time=0.5
        )
        self.wait(0.75)
        
        # Remove highlights
        self.play(
            FadeOut(highlight_a),
            FadeOut(highlight_b),
            FadeOut(highlight_c),
            run_time=0.25
        )
        
        # Scene 4: Visual Proof (3 seconds)
        # Remove original squares but keep equation
        self.play(
            FadeOut(square_a),
            FadeOut(square_b),
            FadeOut(square_c),
            FadeOut(area_a_label),
            FadeOut(area_b_label),
            FadeOut(area_c_label),
            FadeOut(vertex_labels),
            FadeOut(side_a_label),
            FadeOut(side_b_label),
            FadeOut(side_c_label),
            FadeOut(right_angle),
            run_time=0.5
        )
        
        # Create 4 copies of the triangle
        triangles = VGroup(*[triangle.copy() for _ in range(4)])
        
        # Position triangles to form a square with side (a+b)
        # This is a simplified visual proof arrangement
        positions = [
            ORIGIN,
            [TRIANGLE_BASE, 0, 0],
            [TRIANGLE_BASE, TRIANGLE_HEIGHT, 0],
            [0, TRIANGLE_HEIGHT, 0]
        ]
        
        for i, tri in enumerate(triangles):
            tri.move_to(positions[i])
            if i in [1, 3]:
                tri.rotate(PI/2)
            if i == 2:
                tri.rotate(PI)
            if i == 3:
                tri.rotate(3*PI/2)
        
        # Create large square outline
        large_square = Square(
            side_length=TRIANGLE_BASE + TRIANGLE_HEIGHT,
            color=WHITE,
            stroke_width=2
        )
        large_square.move_to(ORIGIN)
        
        # Show inner square with area c²
        inner_square = Square(
            side_length=TRIANGLE_HYP,
            color=SQUARE_C_COLOR,
            fill_opacity=0.3
        )
        inner_square.move_to(ORIGIN)
        
        # Animate arrangement
        self.play(
            LaggedStart(*[Create(tri) for tri in triangles], lag_ratio=0.2),
            run_time=1.0
        )
        self.play(Create(large_square), run_time=0.5)
        self.play(Create(inner_square), run_time=0.5)
        self.wait(0.5)
        
        # Transform to show a² and b² arrangement
        # For simplicity, we'll just show the transformation conceptually
        self.play(
            FadeOut(triangles),
            FadeOut(large_square),
            FadeOut(inner_square),
            run_time=0.5
        )
        
        # Bring back the original squares briefly
        self.play(
            FadeIn(square_a),
            FadeIn(square_b),
            run_time=0.5
        )
        self.wait(0.5)
        
        # Final emphasis on equation
        equation_box = SurroundingRectangle(equation, color=YELLOW, buff=0.2)
        self.play(Create(equation_box), run_time=0.5)
        self.wait(1.5)
        
        # Clean up
        self.play(
            FadeOut(square_a),
            FadeOut(square_b),
            FadeOut(triangle),
            FadeOut(equation_box),
            run_time=0.5
        )
        
        # Keep equation on screen
        self.wait(1.0)