from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Colors
        BLOCK_COLOR = BLUE_D
        SPRING_COLOR = GREEN_B
        DASHPOT_COLOR = RED_C
        FORCE_COLOR = YELLOW
        
        # Create wall
        wall = Rectangle(
            height=2, width=0.3,
            color=GRAY, fill_color=GRAY_E, fill_opacity=1
        ).to_edge(LEFT, buff=1)
        
        # Spring
        spring_start = wall.get_right()
        spring_end = spring_start + RIGHT * 3
        spring = Line(spring_start, spring_end, color=SPRING_COLOR, stroke_width=3)
        
        # Spring coils
        coils = VGroup()
        num_coils = 8
        for i in range(num_coils):
            coil = Arc(
                radius=0.15,
                start_angle=PI,
                angle=PI,
                color=SPRING_COLOR
            )
            coil.shift(spring_start + RIGHT * (0.2 + i * 0.35))
            coils.add(coil)
        
        # Block
        block = Rectangle(
            height=1, width=1.5,
            color=BLOCK_COLOR,
            fill_color=BLOCK_COLOR,
            fill_opacity=0.8
        )
        block.move_to(spring_end + RIGHT * 0.75)
        
        # Labels
        mass_label = MathTex(r"m", color=WHITE).scale(0.8)
        mass_label.next_to(block, UP, buff=0.1)
        
        k_label = MathTex(r"k", color=SPRING_COLOR).scale(0.7)
        k_label.next_to(spring, UP, buff=0.1)
        
        # Dashpot (damping)
        dashpot = VGroup(
            Line(ORIGIN, RIGHT * 0.5, color=DASHPOT_COLOR),
            Line(ORIGIN, DOWN * 0.3, color=DASHPOT_COLOR),
            Line(RIGHT * 0.5, RIGHT * 0.5 + DOWN * 0.3, color=DASHPOT_COLOR),
            Line(DOWN * 0.15, DOWN * 0.15 + RIGHT * 0.5, color=DASHPOT_COLOR, stroke_width=2)
        )
        dashpot.move_to(block.get_left() + LEFT * 0.5 + UP * 0.3)
        b_label = MathTex(r"b", color=DASHPOT_COLOR).scale(0.7)
        b_label.next_to(dashpot, UP, buff=0.05)
        
        # Equation
        equation = MathTex(
            r"m\ddot{x} + b\dot{x} + kx = F_0\cos(\omega_d t)",
            color=WHITE
        ).scale(0.8)
        equation.to_edge(DOWN, buff=0.5)
        
        # Build system
        system = VGroup(wall, coils, spring, block, mass_label, k_label, dashpot, b_label)
        
        # SCENE 1: Show system
        self.play(
            Create(wall),
            Create(coils),
            Create(spring),
            Create(block),
            run_time=2
        )
        self.play(
            Write(mass_label),
            Write(k_label),
            Create(dashpot),
            Write(b_label),
            run_time=1.5
        )
        self.wait(0.5)
        self.play(Write(equation))
        self.wait(1)
        
        # SCENE 2: Add driving force
        force_arrow = Arrow(
            start=block.get_center() + UP * 1.5,
            end=block.get_center() + UP * 0.5,
            color=FORCE_COLOR,
            buff=0,
            stroke_width=4
        )
        force_label = MathTex(r"F_d(t) = F_0\cos(\omega_d t)", color=FORCE_COLOR).scale(0.7)
        force_label.next_to(force_arrow, UP, buff=0.1)
        
        self.play(
            GrowArrow(force_arrow),
            Write(force_label),
            run_time=1
        )
        
        # Animate force oscillation
        for _ in range(3):
            self.play(
                force_arrow.animate.scale(0.5, about_point=force_arrow.get_start()),
                run_time=0.4
            )
            self.play(
                force_arrow.animate.scale(2, about_point=force_arrow.get_start()),
                run_time=0.4
            )
        self.wait(0.5)
        
        # SCENE 3: Show vibration response
        # Create tracker for time
        time_tracker = ValueTracker(0)
        
        # Response function (simplified)
        def response_func(t):
            # Damped oscillation with driving
            transient = 0.4 * np.exp(-0.5 * t) * np.sin(3 * t)
            steady = 0.6 * np.cos(2 * t - 0.3)
            if t < 2:
                return transient + steady
            else:
                return steady
        
        # Update block position
        block.add_updater(
            lambda b: b.move_to(
                spring_end + RIGHT * (0.75 + response_func(time_tracker.get_value()))
            )
        )
        
        # Labels for transient and steady state
        transient_text = Text("Transient", color=RED).scale(0.6)
        steady_text = Text("Steady State", color=GREEN).scale(0.6)
        arrow = Arrow(LEFT, RIGHT, color=WHITE, buff=0.2).scale(0.5)
        text_group = VGroup(transient_text, arrow, steady_text)
        text_group.arrange(RIGHT, buff=0.2)
        text_group.next_to(equation, UP, buff=0.3)
        
        self.play(Write(text_group))
        
        # Animate vibration
        self.play(
            time_tracker.animate.set_value(4),
            rate_func=linear,
            run_time=4
        )
        self.wait(0.5)
        
        # SCENE 4: Resonance demonstration
        block.clear_updaters()
        
        # Reset block
        block.move_to(spring_end + RIGHT * 0.75)
        
        # Frequency labels
        omega_d_label = MathTex(r"\omega_d", color=FORCE_COLOR).scale(0.7)
        omega_0_label = MathTex(r"\omega_0 = \sqrt{k/m}", color=GREEN).scale(0.7)
        freq_group = VGroup(omega_d_label, omega_0_label)
        freq_group.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        freq_group.next_to(force_label, DOWN, buff=0.3)
        
        self.play(Write(freq_group))
        
        # Different driving frequencies
        frequencies = [1.0, 1.5, 2.0, 2.5, 2.0]
        amplitude_tracker = ValueTracker(0.5)
        
        for freq in frequencies:
            # Update frequency display
            new_omega = MathTex(r"\omega_d = " + f"{freq:.1f}", color=FORCE_COLOR).scale(0.7)
            new_omega.move_to(omega_d_label)
            
            # Resonance response amplitude
            amplitude = 0.8 / (abs(2.0 - freq) + 0.3)  # Simplified resonance curve
            
            self.play(
                Transform(omega_d_label, new_omega),
                amplitude_tracker.animate.set_value(amplitude),
                run_time=0.5
            )
            
            # Vibrate block with current frequency
            def vibrate_block(b, f=freq, a=amplitude):
                return b.move_to(
                    spring_end + RIGHT * (0.75 + a * np.cos(f * time_tracker.get_value()))
                )
            
            block.add_updater(vibrate_block)
            self.play(
                time_tracker.animate.increment_value(2),
                rate_func=linear,
                run_time=1.5
            )
            block.clear_updaters()
        
        # Resonance message
        resonance_text = Text(
            "Maximum amplitude at resonance",
            color=YELLOW
        ).scale(0.7)
        resonance_text.next_to(equation, UP, buff=0.3)
        
        self.play(
            FadeOut(text_group),
            Write(resonance_text)
        )
        self.wait(2)
        
        # Final hold
        self.wait(1)