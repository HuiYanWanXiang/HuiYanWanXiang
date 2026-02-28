from manim import *
config.tex_compiler = "xelatex"
config.tex_template = TexTemplate()
config.tex_template.add_to_preamble(r"\\usepackage{ctex}")


class GeneratedScene(Scene):
    def construct(self):
        # Scene Introduction
        title = Text(r"勾股定理 (Pythagorean Theorem)", font_size=36)
        self.play(FadeIn(title))
        self.wait(1)
        self.play(FadeOut(title))

        # Draw Right Triangle
        triangle = Polygon(ORIGIN, 3 * RIGHT, 3 * RIGHT + 4 * UP, color=BLUE).set_fill(BLUE, opacity=0.5)
        label_a = MathTex(r"a", color=WHITE).next_to(triangle.get_edge_center(LEFT), LEFT)
        label_b = MathTex(r"b", color=WHITE).next_to(triangle.get_edge_center(UP), UP)
        label_c = MathTex(r"c", color=WHITE).next_to(triangle.get_edge_center(RIGHT), RIGHT)

        self.play(Create(triangle))
        self.play(Write(label_a), Write(label_b), Write(label_c))
        self.wait(1)

        # Highlight Sides
        self.play(triangle.set_fill, YELLOW, triangle.set_stroke, WHITE, 2)
        self.play(label_a.animate.set_color(ORANGE), label_b.animate.set_color(ORANGE))
        legs_text = Text(r"直角三角形的两条直角边", font_size=24).next_to(triangle, DOWN)
        self.play(Write(legs_text))
        self.wait(2)
        self.play(FadeOut(legs_text))

        # Introduce Hypotenuse
        self.play(triangle.set_fill, BLUE, triangle.set_stroke, WHITE, 1)
        self.play(label_c.animate.set_color(ORANGE))
        hypotenuse_text = Text(r"斜边", font_size=24).next_to(triangle, DOWN)
        self.play(Write(hypotenuse_text))
        self.wait(2)
        self.play(FadeOut(hypotenuse_text))

        # Present the Equation
        equation = MathTex(r"a^2 + b^2 = c^2").next_to(triangle, DOWN)
        self.play(Write(equation))
        self.wait(2)

        # Real-World Application
        ladder = Polygon(0, 0, 1, 2, color=GREEN).set_fill(GREEN, opacity=0.5).shift(LEFT * 2)
        wall = Line(ORIGIN, 3 * UP, color=GREY)
        self.play(Create(wall), Create(ladder))
        application_text = Text(r"应用示例: 计算斜边长度", font_size=24).to_edge(DOWN)
        self.play(Write(application_text))
        self.wait(1)

        # Scene Conclusion
        self.play(FadeOut(ladder), FadeOut(wall), FadeOut(equation))
        conclusion_text = Text(r"勾股定理的美妙!", font_size=36).to_edge(DOWN)
        self.play(Write(conclusion_text))
        self.wait(1)
        self.play(FadeOut(conclusion_text))