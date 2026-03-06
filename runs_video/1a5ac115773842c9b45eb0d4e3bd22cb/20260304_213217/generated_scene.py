from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Colors
        MASS_COLOR = BLUE
        SPRING_COLOR = YELLOW
        FORCE_COLOR = RED
        PHASE_COLOR = GREEN
        
        # Create wall
        wall = Rectangle(height=2.0, width=0.3, color=GRAY, fill_opacity=1)
        wall.to_edge(LEFT, buff=1.0).shift(UP * 0.5)
        
        # Equilibrium position
        eq_pos = wall.get_right() + RIGHT * 2.5
        eq_line = DashedLine(
            eq_pos + UP * 1.5,
            eq_pos + DOWN * 1.5,
            color=WHITE,
            stroke_width=2
        )
        
        # Create mass first (so spring can reference it)
        mass = Square(side_length=0.8, color=MASS_COLOR, fill_opacity=0.8)
        mass.move_to(eq_pos)
        
        # Create spring using always_redraw with proper closure
        def create_spring():
            # Calculate spring length based on current mass position
            mass_x = mass.get_center()[0]
            wall_x = wall.get_right()[0]
            spring_length = max(0.1, mass_x - wall_x)
            num_coils = 5
            
            return ParametricFunction(
                lambda t: wall.get_right() + 
                         RIGHT * (t * spring_length) +
                         UP * (0.2 * np.sin(2 * PI * num_coils * t)),
                t_range=[0, 1, 0.01],
                color=SPRING_COLOR,
                stroke_width=3
            )
        
        spring = always_redraw(create_spring)
        
        # Title
        title = Text("Forced Oscillations", font_size=36)
        title.to_edge(UP)
        
        # Equations
        eq1 = MathTex(r"x(t) = 0", font_size=32)
        eq2 = MathTex(r"F_d(t) = F_0 \cos(\omega_d t)", font_size=32)
        eq3 = MathTex(r"x(t) = A e^{-\beta t}\cos(\omega t + \phi) + \cdots", font_size=28)
        eq4 = MathTex(r"x(t) = A \cos(\omega_d t - \delta)", font_size=32)
        
        # Arrange equations on right side
        eq_group = VGroup(eq1, eq2, eq3, eq4)
        eq_group.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        eq_group.to_edge(RIGHT, buff=1.0).shift(DOWN * 0.5)
        
        # Response labels
        transient_label = Text("Transient Response", font_size=24, color=YELLOW)
        steady_label = Text("Steady State", font_size=24, color=GREEN)
        phase_label = Text("Phase Lag = δ", font_size=24, color=PHASE_COLOR)
        
        # Position labels below equations
        transient_label.next_to(eq_group, DOWN, buff=0.5)
        steady_label.next_to(eq_group, DOWN, buff=0.5)
        phase_label.next_to(eq_group, DOWN, buff=0.5)
        
        # Phase visualization circle
        phase_circle = Circle(radius=0.6, color=PHASE_COLOR, stroke_width=2)
        phase_circle.next_to(steady_label, DOWN, buff=0.5)
        phase_dot = Dot(color=PHASE_COLOR, radius=0.06)
        phase_dot.move_to(phase_circle.get_right())
        
        # Force arrow
        force_arrow = Arrow(
            start=UP * 0.5,
            end=ORIGIN,
            color=FORCE_COLOR,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.3
        )
        force_arrow.next_to(mass, UP, buff=0.1)
        force_label = MathTex(r"F_d(t)", font_size=20, color=FORCE_COLOR)
        force_label.next_to(force_arrow, UP, buff=0.1)
        
        # Trackers for animation
        time_tracker = ValueTracker(0)
        driving_freq = 2.0
        natural_freq = 3.0
        damping = 0.5
        phase_lag = PI/4
        
        # Mass position function
        def mass_position(t):
            if t < 2:
                return eq_pos
            elif t < 4:
                return eq_pos + RIGHT * 0.1 * np.sin(driving_freq * (t-2))
            elif t < 7:
                transient = np.exp(-damping * (t-4)) * np.sin(natural_freq * (t-4))
                forced = 0.3 * np.sin(driving_freq * (t-4))
                return eq_pos + RIGHT * (transient + forced)
            else:
                return eq_pos + RIGHT * 0.8 * np.sin(driving_freq * (t-7) - phase_lag)
        
        # Force magnitude function
        def force_magnitude(t):
            if t < 2:
                return 0
            else:
                return 0.6 * np.sin(driving_freq * (t-2))
        
        # Phase dot position
        def phase_dot_position(t):
            if t < 7:
                return phase_circle.get_right()
            else:
                angle = driving_freq * (t-7) - phase_lag
                return phase_circle.get_center() + 0.6 * np.array([np.cos(angle), np.sin(angle), 0])
        
        # Add updaters
        mass.add_updater(lambda m: m.move_to(mass_position(time_tracker.get_value())))
        force_arrow.add_updater(
            lambda f: f.put_start_and_end_on(
                mass.get_top() + UP * 0.1,
                mass.get_top() + UP * 0.1 + UP * force_magnitude(time_tracker.get_value())
            )
        )
        force_label.add_updater(lambda l: l.next_to(force_arrow, UP, buff=0.1))
        phase_dot.add_updater(lambda d: d.move_to(phase_dot_position(time_tracker.get_value())))
        
        # SCENE 1: System at Rest (0-2s)
        self.add(wall, eq_line, spring, mass, title)
        self.play(FadeIn(eq1))
        self.wait(1)
        
        # SCENE 2: Introduce Driving Force (2-4s)
        self.play(
            FadeIn(force_arrow),
            FadeIn(force_label),
            Transform(eq1, eq2)
        )
        self.add(eq2)
        self.remove(eq1)
        self.play(time_tracker.animate.set_value(4), run_time=2, rate_func=linear)
        
        # SCENE 3: Transient Response (4-7s)
        self.play(FadeIn(transient_label))
        self.play(Transform(eq2, eq3))
        self.add(eq3)
        self.remove(eq2)
        self.play(time_tracker.animate.set_value(7), run_time=3, rate_func=linear)
        
        # SCENE 4: Steady State (7-11s)
        self.play(
            FadeOut(transient_label),
            FadeIn(steady_label),
            FadeIn(phase_circle),
            FadeIn(phase_dot)
        )
        self.play(Transform(eq3, eq4))
        self.add(eq4)
        self.remove(eq3)
        self.play(time_tracker.animate.set_value(11), run_time=4, rate_func=linear)
        
        # SCENE 5: Highlight Phase Difference (11-12s)
        self.play(FadeIn(phase_label))
        self.play(
            mass.animate.set_color(YELLOW),
            force_arrow.animate.set_color(YELLOW),
            run_time=0.5
        )
        self.wait(0.5)
        
        # Clean up updaters
        mass.clear_updaters()
        force_arrow.clear_updaters()
        force_label.clear_updaters()
        phase_dot.clear_updaters()
        
        # Hold final frame
        self.wait(2)