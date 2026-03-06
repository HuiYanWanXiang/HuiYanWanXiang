from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Configuration
        F1_POS = np.array([-2, 0, 0])
        F2_POS = np.array([2, 0, 0])
        AXIS_LENGTH = 7
        TOTAL_TIME = 12.0
        
        # Scene timing breakdown
        SCENE1_TIME = 3.0
        SCENE2_TIME = 3.0
        SCENE3_TIME = 4.0
        SCENE4_TIME = 2.0
        
        # Create axes
        axes = Axes(
            x_range=[-3.5, 3.5, 1],
            y_range=[-2, 2, 1],
            axis_config={"color": GRAY, "stroke_width": 1},
            x_length=AXIS_LENGTH,
            y_length=4,
        ).set_opacity(0.3)
        
        # Create foci
        f1 = Dot(F1_POS, color=RED, radius=0.08)
        f2 = Dot(F2_POS, color=RED, radius=0.08)
        f1_label = MathTex(r"F_1", color=RED).next_to(f1, DOWN, buff=0.1)
        f2_label = MathTex(r"F_2", color=RED).next_to(f2, DOWN, buff=0.1)
        
        # Initial k value
        k_value = ValueTracker(0.5)
        
        # Function to calculate circle center and radius
        def get_circle_data(k):
            x1 = F1_POS[0]
            x2 = F2_POS[0]
            d = abs(x2 - x1)
            
            if abs(k - 1) < 0.001:
                # Degenerate case: perpendicular bisector
                center_x = (x1 + x2) / 2
                radius = 100  # Large radius for visualization
            else:
                center_x = (k**2 * x2 - x1) / (k**2 - 1)
                radius = abs(k * d / (k**2 - 1))
            
            # Limit radius to keep circle in frame
            radius = min(radius, 3.0)
            return np.array([center_x, 0, 0]), radius
        
        # Create circle (will be updated)
        circle = always_redraw(lambda: Circle(
            radius=get_circle_data(k_value.get_value())[1],
            color=BLUE,
            stroke_width=2,
            stroke_opacity=0.8
        ).move_to(get_circle_data(k_value.get_value())[0]))
        
        # Create moving point P on circle
        angle_tracker = ValueTracker(0)
        
        def get_point_position():
            center, radius = get_circle_data(k_value.get_value())
            angle = angle_tracker.get_value()
            return center + radius * np.array([np.cos(angle), np.sin(angle), 0])
        
        P = always_redraw(lambda: Dot(
            get_point_position(),
            color=YELLOW,
            radius=0.1,
            fill_opacity=1
        ))
        
        P_label = always_redraw(lambda: MathTex(r"P", color=YELLOW)
            .next_to(P, UP, buff=0.1).scale(0.8))
        
        # Distance lines
        line_f1 = always_redraw(lambda: Line(
            F1_POS, get_point_position(),
            color=LIGHT_GRAY, stroke_width=1.5
        ).set_opacity(0.7))
        
        line_f2 = always_redraw(lambda: Line(
            F2_POS, get_point_position(),
            color=LIGHT_GRAY, stroke_width=1.5
        ).set_opacity(0.7))
        
        # Distance labels
        dist_label = always_redraw(lambda: VGroup(
            MathTex(r"|PF_1|", color=LIGHT_GRAY).scale(0.6),
            MathTex(r"|PF_2|", color=LIGHT_GRAY).scale(0.6)
        ).arrange(RIGHT, buff=0.5).next_to(axes, UP, buff=0.1))
        
        # Ratio display
        ratio_display = always_redraw(lambda: MathTex(
            r"\frac{|PF_1|}{|PF_2|} = " + f"{k_value.get_value():.2f}",
            color=WHITE
        ).scale(0.8).to_corner(UR, buff=0.5))
        
        # Title
        title = Tex(r"Apollonius Circle: Points where distance ratio to two foci is constant",
                   color=WHITE).scale(0.6).to_edge(UP, buff=0.2)
        
        # Parameter display
        k_display = always_redraw(lambda: MathTex(
            r"k = " + f"{k_value.get_value():.2f}",
            color=GREEN
        ).scale(0.7).to_corner(DL, buff=0.5))
        
        # Circle label
        circle_label = always_redraw(lambda: MathTex(
            r"\text{Apollonius Circle}",
            color=BLUE
        ).scale(0.6).next_to(circle, UP, buff=0.2))
        
        # SCENE 1: Setup and Definition (3.0s)
        self.play(
            Create(axes),
            Create(f1), Create(f2),
            Write(f1_label), Write(f2_label),
            run_time=1.5
        )
        
        self.play(
            Write(title),
            run_time=1.0
        )
        
        definition = MathTex(r"|PF_1|/|PF_2| = k", color=YELLOW)
        definition.scale(0.8).next_to(title, DOWN, buff=0.3)
        self.play(Write(definition), run_time=0.5)
        self.wait(0.5)
        
        # SCENE 2: Circle Formation (3.0s)
        self.play(
            Create(circle),
            Write(circle_label),
            Write(k_display),
            run_time=1.5
        )
        
        # Show radius formula briefly
        radius_formula = MathTex(
            r"r = \frac{k \cdot d}{|k^2 - 1|}",
            color=BLUE
        ).scale(0.7).next_to(circle, DOWN, buff=0.3)
        self.play(Write(radius_formula), run_time=0.5)
        self.wait(0.5)
        self.play(FadeOut(radius_formula), run_time=0.5)
        
        # SCENE 3: Point Motion and Tracing (4.0s)
        self.play(
            FadeIn(P),
            Write(P_label),
            Create(line_f1),
            Create(line_f2),
            Write(dist_label),
            Write(ratio_display),
            run_time=1.0
        )
        
        # Animate P moving around circle
        self.play(
            angle_tracker.animate.set_value(2 * PI),
            rate_func=linear,
            run_time=3.0
        )
        
        # SCENE 4: Parameter Variation (2.0s)
        # Animate k changing
        self.play(
            k_value.animate.set_value(2.0),
            rate_func=smooth,
            run_time=1.0
        )
        
        # Show k=1 case (perpendicular bisector)
        self.play(
            k_value.animate.set_value(1.0),
            rate_func=smooth,
            run_time=0.5
        )
        
        final_text = Tex(
            r"Apollonius Circles generate conic sections when $k$ varies",
            color=YELLOW
        ).scale(0.6).to_edge(DOWN, buff=0.3)
        
        self.play(
            Write(final_text),
            run_time=0.5
        )
        
        self.wait(0.5)