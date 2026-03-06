from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Title
        title = Text("积分的几何意义", font_size=48, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        # Main explanation
        explanation1 = Text("积分就是求面积", font_size=36, color=GREEN)
        explanation1.next_to(title, DOWN, buff=0.8)
        
        explanation2 = Text("曲线下的总面积", font_size=36, color=GREEN)
        explanation2.next_to(explanation1, DOWN, buff=0.5)
        
        self.play(Write(explanation1))
        self.wait(0.5)
        self.play(Write(explanation2))
        self.wait(1)
        
        # Create a simple visual representation without axes
        # Create a curved shape to represent area under curve
        curve_points = [
            LEFT * 3 + DOWN * 1,
            LEFT * 2 + DOWN * 0.5,
            LEFT * 1 + UP * 0.2,
            ORIGIN + UP * 0.8,
            RIGHT * 1 + UP * 1.2,
            RIGHT * 2 + UP * 0.7,
            RIGHT * 3 + UP * 0.3
        ]
        
        # Create the curve
        curve = VMobject()
        curve.set_points_smoothly(curve_points)
        curve.set_color(RED).set_stroke(width=4)
        curve.shift(DOWN * 0.5)
        
        # Create area polygon
        area_points = curve_points.copy()
        area_points.append(RIGHT * 3 + DOWN * 1)
        area_points.append(LEFT * 3 + DOWN * 1)
        
        area = Polygon(*area_points, color=BLUE, fill_opacity=0.5)
        
        # Create x-axis line
        x_axis = Line(LEFT * 3.5 + DOWN * 1, RIGHT * 3.5 + DOWN * 1, color=WHITE)
        x_axis.shift(DOWN * 0.5)
        
        # Create vertical lines at boundaries
        left_line = Line(LEFT * 3 + DOWN * 1, LEFT * 3 + UP * 0.2, color=GREEN)
        left_line.shift(DOWN * 0.5)
        
        right_line = Line(RIGHT * 3 + DOWN * 1, RIGHT * 3 + UP * 0.3, color=GREEN)
        right_line.shift(DOWN * 0.5)
        
        # Labels for boundaries - using Text instead of MathTex
        a_label = Text("a", font_size=32, color=GREEN)
        a_label.next_to(left_line.get_bottom(), DOWN, buff=0.1)
        
        b_label = Text("b", font_size=32, color=GREEN)
        b_label.next_to(right_line.get_bottom(), DOWN, buff=0.1)
        
        # Animate the visual
        self.play(Create(x_axis), run_time=1)
        self.play(Create(curve), run_time=1.5)
        self.wait(0.5)
        
        # Show boundaries
        self.play(Create(left_line), Create(right_line))
        self.play(Write(a_label), Write(b_label))
        self.wait(0.5)
        
        # Fill the area
        self.play(FadeIn(area), run_time=1.5)
        
        # Integral notation - using Text for simple math
        integral = Text("∫ f(x) dx", font_size=40, color=YELLOW)
        integral.move_to(area.get_center() + UP * 0.8)
        
        self.play(Write(integral))
        self.wait(1)
        
        # Equals sign and explanation
        equals = Text("=", font_size=48, color=WHITE)
        equals.next_to(integral, RIGHT, buff=1)
        
        area_text = Text("曲线下面积", font_size=32, color=GREEN)
        area_text.next_to(equals, RIGHT, buff=0.5)
        
        self.play(Write(equals), Write(area_text))
        self.wait(1.5)
        
        # Final summary - using Text for everything
        summary = VGroup(
            Text("定积分:", font_size=32, color=BLUE),
            Text("∫ f(x) dx", font_size=32, color=YELLOW),
            Text("表示曲线", font_size=32, color=WHITE),
            Text("y = f(x)", font_size=32, color=RED),
            Text("从", font_size=32, color=WHITE),
            Text("x = a", font_size=32, color=GREEN),
            Text("到", font_size=32, color=WHITE),
            Text("x = b", font_size=32, color=GREEN),
            Text("之间的面积", font_size=32, color=WHITE)
        )
        
        summary.arrange(RIGHT, buff=0.2)
        summary.next_to(explanation2, DOWN, buff=1.2)
        
        self.play(FadeOut(integral), FadeOut(equals), FadeOut(area_text))
        self.play(Write(summary), run_time=2)
        self.wait(2)
        
        # Clean fade out
        self.play(
            FadeOut(title),
            FadeOut(explanation1),
            FadeOut(explanation2),
            FadeOut(summary),
            FadeOut(curve),
            FadeOut(area),
            FadeOut(x_axis),
            FadeOut(left_line),
            FadeOut(right_line),
            FadeOut(a_label),
            FadeOut(b_label),
            run_time=1
        )
        self.wait(0.5)