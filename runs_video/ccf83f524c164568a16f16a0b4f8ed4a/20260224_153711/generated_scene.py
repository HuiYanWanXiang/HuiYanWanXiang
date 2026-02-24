from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Scene Introduction
        title = MathTex(r"Pythagorean Theorem").scale(1.5)
        self.play(FadeIn(title))
        self.wait(2)
        self.play(FadeOut(title))

        # Triangle Creation
        triangle = Polygon(ORIGIN, 3 * RIGHT, 3 * UP, color=WHITE)
        labels = {
            'A': Dot(triangle.get_vertices()[0]),
            'B': Dot(triangle.get_vertices()[1]),
            'C': Dot(triangle.get_vertices()[2]),
        }
        label_texts = {key: MathTex(key).next_to(dot, UP) for key, dot in labels.items()}
        
        self.play(Create(triangle))
        for label in label_texts.values():
            self.play(FadeIn(label))
        self.wait(1)

        # Squares on Each Side
        square_a = Square(side_length=3).move_to(triangle.get_vertices()[0] + 1.5 * UP + 1.5 * LEFT)
        square_b = Square(side_length=4).move_to(triangle.get_vertices()[1] + 2 * UP + 2 * RIGHT)
        square_c = Square(side_length=5).move_to(triangle.get_vertices()[2] + 2 * UP + 2 * RIGHT / 2)

        self.play(Create(square_a), run_time=2)
        self.play(Create(square_b), run_time=2)
        self.play(Create(square_c), run_time=2)
        self.wait(1)

        # Equation Display
        equation = MathTex(r"a^2 + b^2 = c^2").to_edge(DOWN)
        self.play(FadeIn(equation))
        self.wait(1)
        for part in [r"a^2", r"+", r"b^2", r"=", r"c^2"]:
            self.play(Indicate(equation.get_part_by_tex(part)))
            self.wait(0.5)

        # Conclusion
        conclusion = Tex(r"In a right triangle, the square of the hypotenuse equals the sum of the squares of the other two sides.").scale(0.5).move_to(DOWN)
        self.play(FadeIn(conclusion))
        self.wait(2)
        self.play(FadeOut(triangle), FadeOut(equation), FadeOut(conclusion))