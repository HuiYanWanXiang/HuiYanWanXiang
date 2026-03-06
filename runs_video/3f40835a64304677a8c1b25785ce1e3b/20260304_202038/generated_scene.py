from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Configuration
        config.frame_width = 14.0
        config.frame_height = 8.0
        
        # Colors
        SPRING_COLOR = BLUE
        MASS_COLOR = GRAY
        FORCE_COLOR = RED
        EQUILIBRIUM_COLOR = GREEN
        TEXT_COLOR = WHITE
        
        # Fixed positions (within central 80%)
        TITLE_POS = UP * 3.2
        SUPPORT_POS = UP * 2.5
        EQUILIBRIUM_POS = DOWN * 0.5
        NATURAL_FREQ_POS = LEFT * 5.5 + DOWN * 3.0
        DRIVING_FORCE_POS = RIGHT * 5.0 + UP * 3.0
        TRANSIENT_LABEL_POS = LEFT * 5.5
        STEADY_LABEL_POS = LEFT * 5.5
        AMPLITUDE_LABEL_POS = RIGHT * 5.0
        RESONANCE_TEXT_POS = DOWN * 3.0
        
        # Scene 1: Initial System (2.0s)
        # Title
        title = Text("Forced Vibration", color=TEXT_COLOR, font_size=36)
        title.move_to(TITLE_POS)
        
        # Support line
        support_line = Line(LEFT * 2.0 + SUPPORT_POS, RIGHT * 2.0 + SUPPORT_POS, color=WHITE)
        
        # Spring (simplified as zigzag)
        spring_start = UP * 2.5
        spring_end = UP * 0.5
        spring = always_redraw(lambda: 
            ParametricFunction(
                lambda t: np.array([
                    0.2 * np.sin(8 * t * PI),
                    spring_start[1] + (spring_end[1] - spring_start[1]) * t,
                    0
                ]),
                t_range=[0, 1],
                color=SPRING_COLOR
            )
        )
        
        # Mass
        mass = Square(side_length=1.0, color=MASS_COLOR, fill_color=MASS_COLOR, fill_opacity=0.8)
        mass.move_to(spring_end + DOWN * 0.5)
        
        # Equilibrium line
        equilibrium_line = DashedLine(
            LEFT * 1.5 + EQUILIBRIUM_POS,
            RIGHT * 1.5 + EQUILIBRIUM_POS,
            color=EQUILIBRIUM_COLOR,
            dash_length=0.1
        )
        
        # Natural frequency label
        natural_freq_label = MathTex(r"\omega_0", r"\text{ (Natural Frequency)}", color=TEXT_COLOR)
        natural_freq_label.scale(0.8)
        natural_freq_label.move_to(NATURAL_FREQ_POS)
        
        # Add Scene 1 elements
        self.play(Write(title), run_time=0.5)
        self.play(Create(support_line), run_time=0.5)
        self.play(Create(spring), run_time=0.5)
        self.play(Create(mass), run_time=0.5)
        self.play(Create(equilibrium_line), run_time=0.5)
        self.play(Write(natural_freq_label), run_time=0.5)
        self.wait(0.5)
        
        # Scene 2: Introduce Driving Force (2.5s)
        # Driving force label
        driving_force_label = MathTex(r"F(t) = F_0 \cos(\omega t)", color=FORCE_COLOR)
        driving_force_label.scale(0.8)
        driving_force_label.move_to(DRIVING_FORCE_POS)
        
        # Force arrow (will be animated)
        force_arrow = Arrow(
            LEFT * 0.5 + mass.get_center(),
            RIGHT * 0.5 + mass.get_center(),
            color=FORCE_COLOR,
            buff=0.1,
            max_tip_length_to_length_ratio=0.3
        )
        
        # Frequency slider (visual representation)
        slider_line = Line(LEFT * 2.0 + DOWN * 2.5, RIGHT * 2.0 + DOWN * 2.5, color=WHITE)
        omega_marker = Triangle(color=FORCE_COLOR, fill_color=FORCE_COLOR, fill_opacity=1)
        omega_marker.scale(0.2)
        omega_marker.rotate(PI/2)
        omega_marker.move_to(LEFT * 1.0 + DOWN * 2.5 + UP * 0.2)
        
        omega_label = MathTex(r"\omega", color=FORCE_COLOR)
        omega_label.scale(0.7)
        omega_label.next_to(omega_marker, UP, buff=0.1)
        
        omega0_marker = Triangle(color=EQUILIBRIUM_COLOR, fill_color=EQUILIBRIUM_COLOR, fill_opacity=1)
        omega0_marker.scale(0.2)
        omega0_marker.rotate(PI/2)
        omega0_marker.move_to(RIGHT * 1.0 + DOWN * 2.5 + UP * 0.2)
        
        omega0_label = MathTex(r"\omega_0", color=EQUILIBRIUM_COLOR)
        omega0_label.scale(0.7)
        omega0_label.next_to(omega0_marker, UP, buff=0.1)
        
        # Add Scene 2 elements
        self.play(Write(driving_force_label), run_time=0.5)
        self.play(Create(force_arrow), run_time=0.5)
        
        # Animate pulsating force arrow
        for _ in range(3):
            self.play(
                force_arrow.animate.scale(1.2).set_color(YELLOW),
                run_time=0.3
            )
            self.play(
                force_arrow.animate.scale(1/1.2).set_color(FORCE_COLOR),
                run_time=0.3
            )
        
        self.play(
            Create(slider_line),
            Create(omega_marker),
            Create(omega0_marker),
            Write(omega_label),
            Write(omega0_label),
            run_time=1.0
        )
        self.wait(0.5)
        
        # Scene 3: Transient Response (2.5s)
        # Transient label
        transient_label = Text("Transient", color=YELLOW)
        transient_label.scale(0.8)
        transient_label.move_to(TRANSIENT_LABEL_POS)
        
        # Create oscillation for mass
        omega_tracker = ValueTracker(1.5)  # Driving frequency
        omega0 = 2.0  # Natural frequency
        
        def oscillation_func(t):
            # Combined oscillation: transient + forced
            w = omega_tracker.get_value()
            w0 = omega0
            # Transient part (decaying)
            transient = 0.3 * np.exp(-2*t) * np.cos(w0 * t)
            # Forced part
            forced = 0.2 * np.cos(w * t)
            return transient + forced
        
        # Animate mass oscillation
        mass.add_updater(lambda m: m.move_to(
            spring_end + DOWN * 0.5 + RIGHT * oscillation_func(self.time * 2)
        ))
        
        self.add(mass)
        self.play(Write(transient_label), run_time=0.5)
        
        # Show irregular oscillation
        self.wait(2.0)
        
        # Scene 4: Steady-State (3.0s)
        # Change label to Steady-State
        steady_label = Text("Steady-State", color=GREEN)
        steady_label.scale(0.8)
        steady_label.move_to(STEADY_LABEL_POS)
        
        # Amplitude display
        amplitude_label = MathTex(r"A(\omega)", color=GREEN)
        amplitude_label.scale(0.8)
        amplitude_label.move_to(AMPLITUDE_LABEL_POS)
        
        amplitude_value = DecimalNumber(
            0.2,
            color=GREEN,
            num_decimal_places=3
        )
        amplitude_value.scale(0.7)
        amplitude_value.next_to(amplitude_label, DOWN, buff=0.2)
        
        # Update oscillation to steady-state (remove transient)
        def steady_state_func(t):
            w = omega_tracker.get_value()
            return 0.2 * np.cos(w * t)
        
        mass.clear_updaters()
        mass.add_updater(lambda m: m.move_to(
            spring_end + DOWN * 0.5 + RIGHT * steady_state_func(self.time * 2)
        ))
        
        self.play(
            ReplacementTransform(transient_label, steady_label),
            Write(amplitude_label),
            Write(amplitude_value),
            run_time=1.0
        )
        
        # Show clean oscillation
        self.wait(2.0)
        
        # Scene 5: Resonance Hint (2.0s)
        # Move frequency marker to resonance
        resonance_text = Text("Maximum at Resonance ω = ω₀", color=RED)
        resonance_text.scale(0.8)
        resonance_text.move_to(RESONANCE_TEXT_POS)
        
        # Update amplitude for resonance
        def resonance_amplitude_func(t):
            w = 2.0  # Now equal to omega0
            return 0.8 * np.cos(w * t)  # Larger amplitude
        
        self.play(
            omega_marker.animate.move_to(omega0_marker.get_center()),
            omega_tracker.animate.set_value(2.0),  # Set to omega0
            run_time=1.0
        )
        
        mass.clear_updaters()
        mass.add_updater(lambda m: m.move_to(
            spring_end + DOWN * 0.5 + RIGHT * resonance_amplitude_func(self.time * 2)
        ))
        
        # Update amplitude value
        amplitude_value.add_updater(lambda d: d.set_value(
            0.8 * (1 - 0.5 * np.exp(-2 * self.time))  # Growing to resonance amplitude
        ))
        
        self.play(Write(resonance_text), run_time=0.5)
        self.wait(1.5)
        
        # Freeze final frame
        self.wait(1.0)