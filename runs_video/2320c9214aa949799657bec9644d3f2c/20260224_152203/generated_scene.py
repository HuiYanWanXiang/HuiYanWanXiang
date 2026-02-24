from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Scene Introduction
        title = MathTex(r"\text{勾股定理}").scale(1.5)
        self.play(FadeIn(title))
        self.wait(1.5)
        self.play(FadeOut(title))

        # Draw the Right Triangle
        triangle = Polygon(ORIGIN, 3*RIGHT, 3*UP, color=BLUE)
        labels = {
            'A': Dot(ORIGIN, color=RED),
            'B': Dot(3*RIGHT, color=RED),
            'C': Dot(3*UP, color=RED)
        }
        label_texts = {
            'A': MathTex(r"A").next_to(labels['A'], DOWN),
            'B': MathTex(r"B").next_to(labels['B'], DOWN),
            'C': MathTex(r"C").next_to(labels['C'], LEFT)
        }
        side_labels = {
            'AB': MathTex(r"a").next_to(Line(labels['A'].get_center(), labels['B'].get_center()), DOWN),
            'BC': MathTex(r"b").next_to(Line(labels['B'].get_center(), labels['C'].get_center()), LEFT),
            'AC': MathTex(r"c").next_to(Line(labels['A'].get_center(), labels['C'].get_center()), LEFT)
        }

        self.play(Create(triangle))
        self.play(*[FadeIn(labels[key]) for key in labels])
        self.play(*[FadeIn(label_texts[key]) for key in label_texts])
        self.play(*[FadeIn(side_labels[key]) for key in side_labels])
        self.wait(0.5)

        # Construct Squares on Each Side
        square_a = Square(side_length=3, color=GREEN).move_to(1.5*RIGHT + 1.5*DOWN)
        square_b = Square(side_length=3, color=YELLOW).move_to(1.5*RIGHT + 1.5*UP)
        square_c = Square(side_length=3*sqrt(2), color=ORANGE).move_to(1.5*UP + 1.5*RIGHT)

        area_labels = {
            'a^2': MathTex(r"a^2").move_to(square_a.get_center()),
            'b^2': MathTex(r"b^2").move_to(square_b.get_center()),
            'c^2': MathTex(r"c^2").move_to(square_c.get_center())
        }

        self.play(Create(square_a), FadeIn(area_labels['a^2']))
        self.wait(0.5)
        self.play(Create(square_b), FadeIn(area_labels['b^2']))
        self.wait(0.5)
        self.play(Create(square_c), FadeIn(area_labels['c^2']))
        self.wait(0.5)

        # Show Area Relationships
        equation = MathTex(r"a^2 + b^2 = c^2").to_edge(UP)
        self.play(Write(equation))
        self.wait(0.5)

        # Conclusion
        self.play(FadeOut(square_a), FadeOut(square_b), FadeOut(square_c), FadeOut(area_labels['a^2']), FadeOut(area_labels['b^2']), FadeOut(area_labels['c^2']))
        self.play(Transform(equation, MathTex(r"\text{在直角三角形中，两个直角边的平方和等于斜边的平方}").scale(0.75).to_edge(UP)))
        self.wait(2)
        self.play(FadeOut(equation))