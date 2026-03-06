from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Configuration
        triangle_scale = 1.2
        square_scale = 0.8
        colors = {
            "triangle": WHITE,
            "a_square": BLUE,
            "b_square": GREEN,
            "c_square": RED,
            "triangle_copy": LIGHT_GRAY,
            "text": WHITE,
        }
        
        # Scene 1: Triangle Introduction (3.0s)
        # Create right triangle (3-4-5 proportions)
        triangle_points = [
            ORIGIN,  # C (right angle)
            [3 * triangle_scale, 0, 0],  # B
            [0, 4 * triangle_scale, 0],  # A
        ]
        
        triangle = Polygon(*triangle_points, color=colors["triangle"], stroke_width=6)
        triangle.shift(LEFT * 2.5 + DOWN * 0.5)
        
        # Labels for vertices
        vertex_labels = VGroup(
            MathTex(r"A", color=colors["text"]).next_to(triangle_points[2], UP, buff=0.1),
            MathTex(r"B", color=colors["text"]).next_to(triangle_points[1], RIGHT, buff=0.1),
            MathTex(r"C", color=colors["text"]).next_to(triangle_points[0], LEFT + DOWN, buff=0.1)
        ).shift(LEFT * 2.5 + DOWN * 0.5)
        
        # Side labels
        side_a = Line(triangle_points[0], triangle_points[2], color=colors["triangle"])
        side_b = Line(triangle_points[0], triangle_points[1], color=colors["triangle"])
        side_c = Line(triangle_points[1], triangle_points[2], color=colors["triangle"])
        
        side_labels = VGroup(
            MathTex(r"a", color=colors["text"]).next_to(side_a, LEFT, buff=0.15),
            MathTex(r"b", color=colors["text"]).next_to(side_b, DOWN, buff=0.15),
            MathTex(r"c", color=colors["text"]).next_to(side_c.get_center(), UP + RIGHT, buff=0.15)
        ).shift(LEFT * 2.5 + DOWN * 0.5)
        
        # Right angle symbol
        right_angle = RightAngle(
            side_b, side_a, length=0.4, color=YELLOW, stroke_width=5
        ).shift(LEFT * 2.5 + DOWN * 0.5)
        
        # Animate triangle drawing
        self.play(Create(triangle), run_time=1.5)
        self.play(
            Create(right_angle),
            Write(vertex_labels),
            run_time=1.0
        )
        self.play(Write(side_labels), run_time=0.5)
        self.wait(0.5)
        
        # Scene 2: Construct Squares (3.0s)
        # Square on side a (vertical)
        a_square = Square(
            side_length=4 * triangle_scale * square_scale,
            color=colors["a_square"],
            fill_color=colors["a_square"],
            fill_opacity=0.3,
            stroke_width=4
        )
        a_square.move_to(triangle.get_center() + RIGHT * 3.5 + UP * 1.5)
        
        # Square on side b (horizontal)
        b_square = Square(
            side_length=3 * triangle_scale * square_scale,
            color=colors["b_square"],
            fill_color=colors["b_square"],
            fill_opacity=0.3,
            stroke_width=4
        )
        b_square.move_to(triangle.get_center() + RIGHT * 3.5 + DOWN * 1.5)
        
        # Square on hypotenuse c
        c_square = Square(
            side_length=5 * triangle_scale * square_scale,
            color=colors["c_square"],
            fill_color=colors["c_square"],
            fill_opacity=0.3,
            stroke_width=4
        )
        c_square.move_to(triangle.get_center() + RIGHT * 8.5)
        
        # Area labels for squares
        area_labels = VGroup(
            MathTex(r"a^2", color=colors["a_square"]).next_to(a_square, UP, buff=0.2),
            MathTex(r"b^2", color=colors["b_square"]).next_to(b_square, DOWN, buff=0.2),
            MathTex(r"c^2", color=colors["c_square"]).next_to(c_square, UP, buff=0.2)
        )
        
        # Animate squares
        self.play(
            Create(a_square),
            Create(b_square),
            run_time=1.0
        )
        self.play(Write(area_labels[0:2]), run_time=0.5)
        self.play(Create(c_square), run_time=1.0)
        self.play(Write(area_labels[2]), run_time=0.5)
        self.wait(0.5)
        
        # Scene 3: Geometric Proof (4.0s)
        # Create 4 copies of the triangle
        triangle_copies = VGroup(*[
            triangle.copy().set_color(colors["triangle_copy"]).set_fill(colors["triangle_copy"], opacity=0.3)
            for _ in range(4)
        ])
        
        # Position triangles around the c square
        positions = [
            c_square.get_corner(UL) + RIGHT * 0.5 * c_square.side_length + DOWN * 0.5 * c_square.side_length,
            c_square.get_corner(UR) + LEFT * 0.5 * c_square.side_length + DOWN * 0.5 * c_square.side_length,
            c_square.get_corner(DL) + RIGHT * 0.5 * c_square.side_length + UP * 0.5 * c_square.side_length,
            c_square.get_corner(DR) + LEFT * 0.5 * c_square.side_length + UP * 0.5 * c_square.side_length,
        ]
        
        rotations = [0, 90 * DEGREES, -90 * DEGREES, 180 * DEGREES]
        
        # Animate triangles moving to form arrangement
        animations = []
        for i, (tri, pos, rot) in enumerate(zip(triangle_copies, positions, rotations)):
            tri.move_to(pos).rotate(rot, about_point=pos)
            animations.append(tri.animate.move_to(pos).rotate(rot, about_point=pos))
        
        self.play(*animations, run_time=2.0)
        
        # Show that remaining area equals a² + b²
        remaining_area = VGroup(a_square.copy(), b_square.copy())
        remaining_area.generate_target()
        remaining_area.target.arrange(RIGHT, buff=0.5)
        remaining_area.target.move_to(c_square.get_center())
        
        self.play(
            MoveToTarget(remaining_area),
            triangle_copies.animate.set_opacity(0.2),
            run_time=1.5
        )
        self.wait(0.5)
        
        # Clean up for final equation
        self.play(
            FadeOut(triangle_copies),
            FadeOut(remaining_area),
            run_time=0.5
        )
        
        # Scene 4: Equation Reveal (2.0s)
        # Title
        title = Text("Pythagorean Theorem", font_size=36, color=YELLOW)
        title.to_edge(UP, buff=0.5)
        
        # Equation with colored terms
        equation = MathTex(r"a^2", r"+", r"b^2", r"=", r"c^2", font_size=48)
        equation[0].set_color(colors["a_square"])
        equation[2].set_color(colors["b_square"])
        equation[4].set_color(colors["c_square"])
        equation.next_to(title, DOWN, buff=0.8)
        
        # Animate equation reveal
        self.play(Write(title), run_time=0.5)
        self.play(Write(equation), run_time=1.0)
        self.wait(1.5)
        
        # Final hold
        self.wait(0.5)