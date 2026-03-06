from manim import *
config.tex_compiler = "xelatex"
config.tex_template = TexTemplate()
config.tex_template.add_to_preamble(r"\\usepackage{ctex}")


class GeneratedScene(Scene):
    def construct(self):
        # Title
        title = Text(r"导数的几何意义", font_size=48, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        # Main explanation
        explanation = VGroup(
            Text(r"导数", font_size=36, color=YELLOW),
            Text(r"表示函数在某一点的", font_size=28),
            Text(r"瞬时变化率", font_size=36, color=GREEN),
            Text(r"几何上对应", font_size=28),
            Text(r"曲线在该点切线的斜率", font_size=36, color=RED)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).center()
        
        self.play(FadeIn(explanation, shift=UP))
        self.wait(1)
        
        # Clear for visual demonstration
        self.play(FadeOut(explanation))
        
        # Create a simple curve using dots (no axes)
        curve_points = [
            np.array([-3, -1, 0]),
            np.array([-2, 0.5, 0]),
            np.array([-1, 1.5, 0]),
            np.array([0, 2, 0]),
            np.array([1, 1.5, 0]),
            np.array([2, 0.5, 0]),
            np.array([3, -1, 0])
        ]
        
        curve = VMobject()
        curve.set_points_smoothly(curve_points)
        curve.set_color(BLUE).set_stroke(width=3)
        self.play(Create(curve), run_time=1.5)
        
        # Point of interest
        point = Dot(color=YELLOW).move_to(curve_points[3])
        point_label = MathTex(r"P(x_0, f(x_0))", font_size=24).next_to(point, UR, buff=0.1)
        self.play(FadeIn(point), Write(point_label))
        self.wait(0.5)
        
        # Secant lines approaching tangent
        secant_lines = VGroup()
        offsets = [1.5, 0.8, 0.3]
        
        for offset in offsets:
            start_point = curve_points[3]
            end_point = np.array([3 + offset, 2 - offset**2, 0])
            secant = Line(start_point, end_point, color=GRAY, stroke_width=2)
            secant_lines.add(secant)
        
        # Animate secant lines
        for i, secant in enumerate(secant_lines):
            self.play(Create(secant), run_time=0.5)
            if i < len(secant_lines) - 1:
                self.play(FadeOut(secant), run_time=0.3)
        
        # Tangent line at the point
        tangent_line = Line(
            start=curve_points[3] + LEFT * 2,
            end=curve_points[3] + RIGHT * 2,
            color=RED,
            stroke_width=4
        )
        
        # Reveal tangent line
        self.play(ReplacementTransform(secant_lines[-1], tangent_line))
        
        # Derivative equation
        derivative_eq = MathTex(
            r"f'(x_0) = \lim_{\Delta x \to 0} \frac{f(x_0+\Delta x) - f(x_0)}{\Delta x}",
            font_size=28
        ).to_edge(DOWN, buff=0.5)
        
        geometric_eq = MathTex(
            r"= \text{切线斜率}",
            font_size=28,
            color=RED
        ).next_to(derivative_eq, RIGHT)
        
        self.play(Write(derivative_eq))
        self.wait(0.5)
        self.play(Write(geometric_eq))
        self.wait(1)
        
        # Summary box
        summary_box = Rectangle(
            width=5, height=2,
            color=WHITE,
            stroke_width=2
        ).to_edge(LEFT, buff=1)
        
        summary_text = VGroup(
            Text(r"导数几何意义:", font_size=24, color=YELLOW),
            Text(r"1. 切线斜率", font_size=20),
            Text(r"2. 瞬时变化率", font_size=20),
            Text(r"3. 局部线性近似", font_size=20)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(summary_box)
        
        self.play(Create(summary_box))
        self.play(FadeIn(summary_text, shift=RIGHT))
        self.wait(1.5)
        
        # Final emphasis
        final_text = Text(r"导数 = 切线斜率", font_size=36, color=GREEN)
        final_text.move_to(ORIGIN + UP * 2)
        
        self.play(
            FadeOut(VGroup(curve, point, point_label, tangent_line, 
                          derivative_eq, geometric_eq, summary_box, summary_text)),
            Write(final_text)
        )
        self.wait(1)
        
        # Clean up
        self.play(FadeOut(final_text), FadeOut(title))