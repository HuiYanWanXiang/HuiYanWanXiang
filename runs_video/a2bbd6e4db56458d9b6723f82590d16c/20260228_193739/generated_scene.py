from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Scene 1: Setup (3.0 seconds)
        # Create right triangle
        triangle = Polygon(
            [-3, -1, 0],
            [-3, 2, 0],
            [0, -1, 0],
            color=WHITE,
            stroke_width=6
        )
        
        # Label vertices
        vertex_A = MathTex(r"A", color=WHITE).scale(0.8).next_to([-3, -1, 0], DL, buff=0.15)
        vertex_B = MathTex(r"B", color=WHITE).scale(0.8).next_to([-3, 2, 0], UP, buff=0.15)
        vertex_C = MathTex(r"C", color=WHITE).scale(0.8).next_to([0, -1, 0], DR, buff=0.15)
        
        # Label sides
        side_a = MathTex(r"a", color=WHITE).scale(0.7).next_to([-3, 0.5, 0], LEFT, buff=0.15)
        side_b = MathTex(r"b", color=WHITE).scale(0.7).next_to([-1.5, -1, 0], DOWN, buff=0.15)
        side_c = MathTex(r"c", color=WHITE).scale(0.7).next_to([-1.5, 0.5, 0], UR, buff=0.15)
        
        # Animate triangle and labels
        self.play(Create(triangle), run_time=1.5)
        self.play(
            Write(vertex_A),
            Write(vertex_B),
            Write(vertex_C),
            run_time=1.0
        )
        self.play(
            Write(side_a),
            Write(side_b),
            Write(side_c),
            run_time=0.5
        )
        self.wait(0.5)
        
        # Scene 2: Construct Squares (4.0 seconds)
        # Square on side a (vertical)
        square_a = Polygon(
            [-3, -1, 0],
            [-5, -1, 0],
            [-5, 2, 0],
            [-3, 2, 0],
            color=BLUE,
            fill_opacity=0.3,
            stroke_width=4
        )
        
        # Square on side b (horizontal)
        square_b = Polygon(
            [0, -1, 0],
            [3, -1, 0],
            [3, -4, 0],
            [0, -4, 0],
            color=GREEN,
            fill_opacity=0.3,
            stroke_width=4
        )
        
        # Square on hypotenuse c
        # Calculate points for tilted square
        # Hypotenuse vector from B to C: (3, -3, 0)
        # Perpendicular vector: rotate 90 degrees: (3, 3, 0)
        perp_vector = np.array([3, 3, 0])
        
        square_c = Polygon(
            [-3, 2, 0],  # B
            [-3, 2, 0] + perp_vector,  # B + perp
            [0, -1, 0] + perp_vector,  # C + perp
            [0, -1, 0],  # C
            color=YELLOW,
            fill_opacity=0.3,
            stroke_width=4
        )
        
        # Animate squares
        self.play(Create(square_a), run_time=1.0)
        self.play(Create(square_b), run_time=1.0)
        self.play(Create(square_c), run_time=1.0)
        self.wait(1.0)
        
        # Scene 3: Area Relationship (3.0 seconds)
        # Display equation
        equation = MathTex(r"a^2 + b^2 = c^2", color=WHITE).scale(1.2)
        equation.to_edge(UP).shift(RIGHT * 2)
        
        # Area labels
        area_a = MathTex(r"\text{Area} = a^2", color=BLUE).scale(0.8)
        area_a.next_to(square_a, DOWN, buff=0.3)
        
        area_b = MathTex(r"\text{Area} = b^2", color=GREEN).scale(0.8)
        area_b.next_to(square_b, DOWN, buff=0.3)
        
        area_c = MathTex(r"\text{Area} = c^2", color=YELLOW).scale(0.8)
        area_c.next_to(square_c, UP, buff=0.3)
        
        # Animate equation and area labels
        self.play(Write(equation), run_time=0.5)
        self.play(
            square_a.animate.set_fill(opacity=0.6),
            Write(area_a),
            run_time=0.5
        )
        self.play(
            square_b.animate.set_fill(opacity=0.6),
            Write(area_b),
            run_time=0.5
        )
        self.play(
            square_c.animate.set_fill(opacity=0.6),
            Write(area_c),
            run_time=0.5
        )
        self.wait(1.0)
        
        # Reset fill opacity
        self.play(
            square_a.animate.set_fill(opacity=0.3),
            square_b.animate.set_fill(opacity=0.3),
            square_c.animate.set_fill(opacity=0.3),
            run_time=0.5
        )
        
        # Scene 4: Visual Proof (2.0 seconds)
        # Create pieces from square_a (blue)
        piece_a1 = Polygon(
            [-3, -1, 0],
            [-4, -1, 0],
            [-4, 0, 0],
            [-3, 0, 0],
            color=BLUE,
            fill_opacity=0.6,
            stroke_width=3
        )
        
        piece_a2 = Polygon(
            [-4, 0, 0],
            [-5, 0, 0],
            [-5, 2, 0],
            [-4, 2, 0],
            color=BLUE,
            fill_opacity=0.6,
            stroke_width=3
        )
        
        # Create pieces from square_b (green)
        piece_b1 = Polygon(
            [0, -1, 0],
            [1, -1, 0],
            [1, -2, 0],
            [0, -2, 0],
            color=GREEN,
            fill_opacity=0.6,
            stroke_width=3
        )
        
        piece_b2 = Polygon(
            [1, -2, 0],
            [3, -2, 0],
            [3, -4, 0],
            [1, -4, 0],
            color=GREEN,
            fill_opacity=0.6,
            stroke_width=3
        )
        
        # Hide original squares
        self.play(
            FadeOut(square_a),
            FadeOut(square_b),
            FadeOut(area_a),
            FadeOut(area_b),
            run_time=0.3
        )
        
        # Show pieces
        self.play(
            FadeIn(piece_a1),
            FadeIn(piece_a2),
            FadeIn(piece_b1),
            FadeIn(piece_b2),
            run_time=0.3
        )
        
        # Animate pieces moving to fill square_c
        # Target positions within square_c
        # Adjusted to better fit the tilted square
        self.play(
            piece_a1.animate.move_to([-1.5, 0.5, 0]).rotate(PI/4),
            piece_a2.animate.move_to([0, 2, 0]).rotate(PI/4),
            piece_b1.animate.move_to([-1.5, 0.5, 0]).rotate(-PI/4),
            piece_b2.animate.move_to([0, 2, 0]).rotate(-PI/4),
            run_time=1.0
        )
        
        # Highlight the filled square
        self.play(
            square_c.animate.set_fill(opacity=0.6),
            run_time=0.3
        )
        
        # Final emphasis
        self.play(
            equation.animate.scale(1.3).set_color(YELLOW),
            run_time=0.3
        )
        self.wait(0.4)