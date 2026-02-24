from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Scene Introduction
        title = MathTex(r"\text{Pythagorean Theorem}").scale(1.5)
        self.play(FadeIn(title))
        self.wait(1)
        self.clear()

        # Right Triangle Creation
        triangle = Polygon(0, 0, 3, 0, 0, 4, color=BLUE)
        self.play(Create(triangle))
        
        labels = [
            MathTex(r"A").next_to(triangle.get_vertices()[0], DOWN),
            MathTex(r"B").next_to(triangle.get_vertices()[1], RIGHT),
            MathTex(r"C").next_to(triangle.get_vertices()[2], UP),
            MathTex(r"AB = a").next_to(triangle.get_vertices()[0], LEFT),
            MathTex(r"BC = b").next_to(triangle.get_vertices()[1], UP),
            MathTex(r"AC = c").next_to(triangle.get_vertices()[2], LEFT),
            MathTex(r"\text{In a right triangle...}").to_edge(UP)
        ]
        
        for label in labels:
            self.play(Write(label))
        self.wait(1)
        self.clear()

        # Area Visualization
        square_a = Square(side_length=3, color=YELLOW).shift(1.5 * LEFT + 1.5 * DOWN)
        square_b = Square(side_length=4, color=GREEN).shift(1.5 * RIGHT + 2 * UP)
        square_c = Square(side_length=5, color=RED).shift(0.5 * LEFT + 2.5 * DOWN)

        self.play(Create(square_a), Create(square_b), Create(square_c))
        area_labels = [
            MathTex(r"a^2").move_to(square_a.get_center()),
            MathTex(r"b^2").move_to(square_b.get_center()),
            MathTex(r"c^2").move_to(square_c.get_center()),
            MathTex(r"a^2 + b^2 = c^2").to_edge(DOWN)
        ]
        
        for label in area_labels:
            self.play(Write(label))
        self.wait(1)
        self.clear()

        # Area Comparison
        self.play(FadeIn(square_c))
        self.play(square_a.animate.shift(0.5 * RIGHT), square_b.animate.shift(0.5 * DOWN))
        self.play(square_a.animate.set_color(ORANGE), square_b.animate.set_color(PINK))
        self.play(square_c.animate.set_color(GOLD).set_opacity(1))
        self.play(Write(MathTex(r"\text{The sum of the areas of the squares on the legs equals the area of the square on the hypotenuse.}").to_edge(DOWN)))
        self.wait(1)
        self.clear()

        # Conclusion
        final_equation = MathTex(r"a^2 + b^2 = c^2").scale(1.5)
        self.play(FadeIn(final_equation))
        self.wait(2)