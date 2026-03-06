from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Configuration
        config.frame_width = 14.2
        config.frame_height = 8.0
        
        # Colors
        MASS_COLOR = BLUE
        SPRING_COLOR = YELLOW
        FORCE_COLOR = RED
        DAMPING_COLOR = GREEN
        EQUILIBRIUM_COLOR = GRAY
        TEXT_COLOR = WHITE
        
        # Parameters
        wall_x = -5.0
        eq_x = -2.0
        mass_radius = 0.4
        spring_length = 2.0
        amplitude = 1.5
        
        # Create wall
        wall = Rectangle(height=2.0, width=0.3, color=GRAY, fill_opacity=1)
        wall.move_to([wall_x, 0, 0])
        
        # Create spring
        spring = Line(
            start=[wall_x + 0.15, 0, 0],
            end=[eq_x, 0, 0],
            color=SPRING_COLOR,
            stroke_width=3
        )
        
        # Create mass
        mass = Circle(radius=mass_radius, color=MASS_COLOR, fill_opacity=0.8)
        mass.move_to([eq_x, 0, 0])
        mass_label = MathTex(r"m", color=WHITE).scale(0.7)
        mass_label.move_to(mass.get_center())
        
        # Create equilibrium line
        eq_line = DashedLine(
            start=[eq_x, -1.5, 0],
            end=[eq_x, 1.5, 0],
            color=EQUILIBRIUM_COLOR,
            dash_length=0.1
        )
        eq_label = MathTex(r"x=0", color=EQUILIBRIUM_COLOR).scale(0.6)
        eq_label.next_to(eq_line, DOWN, buff=0.1)
        
        # Create x-axis
        x_axis = NumberLine(
            x_range=[-2, 2, 1],
            length=4,
            include_numbers=True,
            numbers_to_include=[-2, -1, 0, 1, 2],
            label_direction=DOWN
        )
        x_axis.move_to([eq_x, -2.5, 0])
        x_label = MathTex(r"x", color=WHITE).scale(0.7)
        x_label.next_to(x_axis, RIGHT, buff=0.1)
        
        # Group physical system
        system = VGroup(wall, spring, mass, mass_label, eq_line, eq_label, x_axis, x_label)
        
        # Create equation box (bottom left)
        equation_box = Rectangle(
            height=2.0, width=4.0,
            color=BLUE, stroke_width=2
        )
        equation_box.move_to([-3.5, -3.0, 0])
        
        eq_title = Text("Equation of Motion", color=YELLOW).scale(0.5)
        eq_title.next_to(equation_box.get_top(), DOWN, buff=0.1)
        
        eq_motion = MathTex(r"m\frac{d^2x}{dt^2} + \gamma\frac{dx}{dt} + kx = F_d(t)", color=WHITE).scale(0.6)
        eq_motion.next_to(eq_title, DOWN, buff=0.2)
        
        driving_force = MathTex(r"F_d(t) = F_0\cos(\omega_d t)", color=RED).scale(0.6)
        driving_force.next_to(eq_motion, DOWN, buff=0.2)
        
        # Create parameter display (bottom right)
        param_box = Rectangle(
            height=2.0, width=4.0,
            color=GREEN, stroke_width=2
        )
        param_box.move_to([3.5, -3.0, 0])
        
        param_title = Text("Parameters", color=YELLOW).scale(0.5)
        param_title.next_to(param_box.get_top(), DOWN, buff=0.1)
        
        omega_natural = MathTex(r"\omega_0 = \sqrt{k/m}", color=WHITE).scale(0.6)
        omega_natural.next_to(param_title, DOWN, buff=0.2)
        
        omega_drive = MathTex(r"\omega_d = 1.2\omega_0", color=RED).scale(0.6)
        omega_drive.next_to(omega_natural, DOWN, buff=0.2)
        
        force_amp = MathTex(r"F_0 = 0.5", color=WHITE).scale(0.6)
        force_amp.next_to(omega_drive, DOWN, buff=0.2)
        
        # Create separation line
        sep_line = Line(
            start=[-7, -1.5, 0],
            end=[7, -1.5, 0],
            color=GRAY, stroke_width=1
        )
        
        # SCENE 1: Setup and Natural Damped Oscillation
        self.play(
            Create(wall),
            Create(spring),
            Create(mass),
            Write(mass_label),
            run_time=1.0
        )
        self.wait(0.2)
        
        self.play(
            Create(eq_line),
            Write(eq_label),
            Create(x_axis),
            Write(x_label),
            run_time=1.0
        )
        self.wait(0.3)
        
        # Show initial displacement
        initial_pos = [eq_x + amplitude, 0, 0]
        displacement_label = Text("Initial Displacement", color=YELLOW).scale(0.5)
        displacement_label.next_to(mass, UP, buff=0.3)
        
        self.play(
            mass.animate.move_to(initial_pos),
            spring.animate.put_start_and_end_on(
                [wall_x + 0.15, 0, 0],
                [eq_x + amplitude - mass_radius, 0, 0]
            ),
            Write(displacement_label),
            run_time=1.0
        )
        self.wait(0.5)
        
        # Create damping arrow (always opposite to velocity)
        damping_arrow = Arrow(
            start=[0, 0, 0],
            end=[-0.5, 0, 0],
            color=DAMPING_COLOR,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.2
        )
        damping_arrow.next_to(mass, LEFT, buff=0.1)
        
        # Animate damped oscillation
        damped_label = Text("Damped Natural Oscillation: Amplitude decays", color=GREEN).scale(0.5)
        damped_label.move_to([0, 2.5, 0])
        
        self.play(Write(damped_label), run_time=0.5)
        self.remove(displacement_label)
        
        # Simulate damped oscillation with ValueTracker
        t = ValueTracker(0)
        
        def get_mass_position():
            time_val = t.get_value()
            # Damped oscillation: x = A * exp(-βt) * cos(ωt)
            decay = np.exp(-0.8 * time_val)
            osc = np.cos(3.0 * time_val)
            x_pos = eq_x + amplitude * decay * osc
            return [x_pos, 0, 0]
        
        def get_spring_end():
            mass_pos = get_mass_position()
            return [mass_pos[0] - mass_radius, 0, 0]
        
        def update_damping_arrow(arr):
            time_val = t.get_value()
            # Velocity: derivative of position
            decay = np.exp(-0.8 * time_val)
            vel = -amplitude * (0.8 * decay * np.cos(3.0 * time_val) + 
                              3.0 * decay * np.sin(3.0 * time_val))
            
            # Damping force opposite to velocity
            if abs(vel) < 0.01:
                arr.become(Arrow(start=[0,0,0], end=[0,0,0], color=DAMPING_COLOR))
            else:
                direction = -1 if vel > 0 else 1
                arr.become(Arrow(
                    start=[0, 0, 0],
                    end=[0.3 * direction, 0, 0],
                    color=DAMPING_COLOR,
                    stroke_width=4,
                    max_tip_length_to_length_ratio=0.2
                ))
                arr.next_to(mass, LEFT if direction > 0 else RIGHT, buff=0.1)
        
        mass.add_updater(lambda m: m.move_to(get_mass_position()))
        spring.add_updater(lambda s: s.put_start_and_end_on(
            [wall_x + 0.15, 0, 0],
            get_spring_end()
        ))
        damping_arrow.add_updater(update_damping_arrow)
        
        self.add(damping_arrow)
        self.play(t.animate.set_value(2.0), rate_func=linear, run_time=2.0)
        
        # SCENE 2: Introduce Driving Force
        # Freeze motion
        mass.clear_updaters()
        spring.clear_updaters()
        damping_arrow.clear_updaters()
        
        self.play(FadeOut(damped_label), run_time=0.5)
        self.wait(0.5)
        
        # Create driving force arrow
        drive_arrow = Arrow(
            start=[0, 0, 0],
            end=[0.8, 0, 0],
            color=FORCE_COLOR,
            stroke_width=6,
            max_tip_length_to_length_ratio=0.3
        )
        drive_arrow.next_to(mass, UP, buff=0.3)
        drive_label = MathTex(r"F_d(t)", color=FORCE_COLOR).scale(0.6)
        drive_label.next_to(drive_arrow, UP, buff=0.1)
        
        # Add equation box and parameters
        self.play(
            Create(equation_box),
            Write(eq_title),
            Write(eq_motion),
            Write(driving_force),
            run_time=1.0
        )
        
        self.play(
            Create(param_box),
            Write(param_title),
            Write(omega_natural),
            Write(omega_drive),
            Write(force_amp),
            run_time=1.0
        )
        
        self.play(
            Create(sep_line),
            run_time=0.5
        )
        
        # Add driving force
        self.play(
            GrowArrow(drive_arrow),
            Write(drive_label),
            run_time=0.8
        )
        
        # Pulsate driving force
        drive_t = ValueTracker(0)
        
        def update_drive_arrow(arr):
            time_val = drive_t.get_value()
            force = 0.8 * (0.8 + 0.2 * np.cos(3.6 * time_val))  # ω_d = 1.2 * ω_natural
            arr.become(Arrow(
                start=[0, 0, 0],
                end=[force, 0, 0],
                color=FORCE_COLOR,
                stroke_width=6,
                max_tip_length_to_length_ratio=0.3
            ))
            arr.next_to(mass, UP, buff=0.3)
        
        drive_arrow.add_updater(update_drive_arrow)
        self.add(drive_arrow)
        
        # SCENE 3: Transient and Steady-State Response
        # Show transient response
        transient_label = Text("Transient Response: Complex motion", color=ORANGE).scale(0.5)
        transient_label.move_to([0, 2.5, 0])
        
        self.play(Write(transient_label), run_time=0.5)
        
        # Combined motion: transient + steady state
        t2 = ValueTracker(0)
        
        def get_forced_position():
            time_val = t2.get_value()
            # Transient: damped natural oscillation
            transient = amplitude * np.exp(-0.8 * (time_val + 2.0)) * np.cos(3.0 * (time_val + 2.0))
            # Steady state: driving frequency response
            steady = 0.6 * np.cos(3.6 * time_val - 0.5)  # ω_d = 3.6, with phase
            # Blend from transient to steady state
            blend = min(1.0, time_val / 3.0)
            x_pos = eq_x + (1 - blend) * transient + blend * steady
            return [x_pos, 0, 0]
        
        def get_forced_spring_end():
            mass_pos = get_forced_position()
            return [mass_pos[0] - mass_radius, 0, 0]
        
        mass.add_updater(lambda m: m.move_to(get_forced_position()))
        spring.add_updater(lambda s: s.put_start_and_end_on(
            [wall_x + 0.15, 0, 0],
            get_forced_spring_end()
        ))
        
        # Update both trackers together
        self.play(
            t2.animate.set_value(3.0),
            drive_t.animate.set_value(3.0),
            rate_func=linear,
            run_time=3.0
        )
        
        # Show steady state
        self.play(FadeOut(transient_label), run_time=0.3)
        
        steady_label = Text("Steady-State: Oscillates at driving frequency ω_d", color=GREEN).scale(0.5)
        steady_label.move_to([0, 2.5, 0])
        
        # Highlight ω_d parameter
        omega_drive_box = SurroundingRectangle(omega_drive, color=RED, buff=0.1)
        
        self.play(
            Write(steady_label),
            Create(omega_drive_box),
            run_time=0.7
        )
        
        # Continue steady state motion
        self.play(
            t2.animate.set_value(6.0),
            drive_t.animate.set_value(6.0),
            rate_func=linear,
            run_time=3.0
        )
        
        # Final message
        final_text = Text(
            "Forced Vibration: System eventually 'locks' to the driver's frequency.",
            color=YELLOW
        ).scale(0.5)
        final_text.move_to([0, -4.0, 0])
        
        self.play(Write(final_text), run_time=1.0)
        self.wait(1.0)
        
        # Clean up updaters
        mass.clear_updaters()
        spring.clear_updaters()
        drive_arrow.clear_updaters()