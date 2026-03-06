from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Configuration
        config.frame_width = 14.0
        config.frame_height = 8.0
        
        # Colors
        MASS_COLOR = BLUE
        SPRING_COLOR = GRAY
        DAMPING_COLOR = RED
        FORCE_COLOR = YELLOW
        TEXT_COLOR = WHITE
        
        # System parameters
        mass_radius = 0.4
        spring_length = 3.0
        equilibrium_x = 2.0
        
        # Create fixed anchor point
        fixed_point = Dot(LEFT * 4, color=WHITE)
        fixed_point.shift(UP * 0.5)
        
        # Create spring
        spring = Line(
            fixed_point.get_right(),
            fixed_point.get_right() + RIGHT * spring_length,
            color=SPRING_COLOR
        )
        # Add spring coils
        coils = 8
        coil_height = 0.2
        for i in range(coils):
            t = i / (coils - 1)
            point = spring.point_from_proportion(t)
            offset = coil_height * np.sin(np.pi * t * coils) * UP
            spring.add_line_to(point + offset)
        
        # Create mass
        mass = Circle(
            radius=mass_radius,
            color=MASS_COLOR,
            fill_color=MASS_COLOR,
            fill_opacity=0.5
        )
        mass.move_to(fixed_point.get_right() + RIGHT * (spring_length + mass_radius))
        
        # Create equilibrium line
        eq_line = DashedLine(
            mass.get_center() + LEFT * 2,
            mass.get_center() + RIGHT * 2,
            color=GRAY,
            dash_length=0.1
        )
        eq_line.shift(DOWN * mass_radius)
        
        # Create labels
        mass_label = MathTex(r"m", color=TEXT_COLOR)
        mass_label.next_to(mass, UP, buff=0.2)
        
        # Create damping representation (red arrow)
        damping_arrow = Arrow(
            mass.get_bottom() + DOWN * 0.5,
            mass.get_bottom(),
            color=DAMPING_COLOR,
            buff=0.1,
            stroke_width=6
        )
        damping_label = MathTex(r"c", color=DAMPING_COLOR)
        damping_label.next_to(damping_arrow, DOWN, buff=0.1)
        damping_text = Text("Damping Coefficient", font_size=24, color=TEXT_COLOR)
        damping_text.next_to(damping_label, DOWN, buff=0.1)
        
        # Create driving force (yellow arrow)
        force_arrow = Arrow(
            mass.get_top() + UP * 1.5,
            mass.get_top(),
            color=FORCE_COLOR,
            buff=0.1,
            stroke_width=8
        )
        force_label = MathTex(r"F(t) = F_0 \cos(\omega t)", color=FORCE_COLOR)
        force_label.next_to(force_arrow, UP, buff=0.1)
        
        # Create equation of motion
        eq_motion = MathTex(
            r"m \ddot{x} + c \dot{x} + k x = F_0 \cos(\omega t)",
            color=TEXT_COLOR
        )
        eq_motion.scale(0.8)
        eq_motion.to_corner(UL, buff=0.5)
        
        # Create driving frequency label
        freq_text = Text("Driving Frequency", font_size=24, color=TEXT_COLOR)
        freq_omega = MathTex(r"\omega", color=YELLOW)
        wave_icon = Text("~", font_size=36, color=YELLOW)
        
        freq_group = VGroup(freq_text, freq_omega, wave_icon)
        freq_group.arrange(RIGHT, buff=0.2)
        freq_group.next_to(eq_motion, DOWN, aligned_edge=LEFT, buff=0.3)
        
        # Create transient to steady state text
        transient_text = Text("Transient", color=RED)
        steady_text = Text("Steady State", color=GREEN)
        arrow_text = Arrow(LEFT, RIGHT, color=WHITE, buff=0.5)
        
        state_group = VGroup(transient_text, arrow_text, steady_text)
        state_group.arrange(RIGHT, buff=0.3)
        state_group.to_edge(DOWN, buff=0.5)
        
        # Create resonance label
        resonance_label = MathTex(r"\omega \approx \omega_0", color=YELLOW)
        resonance_label.scale(0.9)
        resonance_label.next_to(mass, RIGHT, buff=0.5)
        
        # Create amplitude indicator
        amp_arrow = DoubleArrow(
            mass.get_center() + UP * 0.5,
            mass.get_center() + DOWN * 0.5,
            color=GREEN,
            buff=0,
            stroke_width=4
        )
        amp_label = MathTex(r"A", color=GREEN)
        amp_label.next_to(amp_arrow, RIGHT, buff=0.1)
        
        # Create final amplitude equation
        amp_eq = MathTex(
            r"A = \frac{F_0}{\sqrt{(k - m\omega^2)^2 + (c\omega)^2}}",
            color=TEXT_COLOR
        )
        amp_eq.scale(0.7)
        amp_eq.to_corner(UR, buff=0.5)
        
        # Animation timeline
        # Scene 1: Setup (0-3s)
        self.play(
            Create(fixed_point),
            Create(spring),
            run_time=1
        )
        self.play(
            Create(mass),
            run_time=1
        )
        self.wait(0.5)
        
        self.play(
            Write(mass_label),
            Create(eq_line),
            run_time=1
        )
        self.wait(0.5)
        
        self.play(
            Create(damping_arrow),
            Write(damping_label),
            Write(damping_text),
            run_time=1
        )
        self.wait(0.5)
        
        # Scene 2: Driving force & equation (3-6s)
        self.play(
            Create(force_arrow),
            Write(force_label),
            run_time=1
        )
        
        # Pulse the force arrow
        self.play(
            force_arrow.animate.set_stroke_width(12),
            rate_func=there_and_back,
            run_time=0.3
        )
        
        self.play(
            Write(eq_motion),
            run_time=1
        )
        
        self.play(
            Write(freq_text),
            Write(freq_omega),
            Write(wave_icon),
            run_time=1
        )
        self.wait(0.5)
        
        # Scene 3: Demonstrate motion (6-10s)
        # Create oscillation animation
        def update_mass(mob, dt):
            t = self.time - 6.0  # Start time for oscillation
            if t < 0:
                return
            
            # Transient response (first 2 seconds)
            if t < 2.0:
                decay = np.exp(-0.5 * t)
                freq = 2.0 + 0.5 * np.sin(t * 3)
                amp = 0.3 * (1 - np.exp(-2 * t))
                displacement = amp * decay * np.sin(freq * t * 2 * PI)
            # Steady state (after 2 seconds)
            else:
                amp = 0.8
                freq = 2.0
                displacement = amp * np.sin(freq * (t - 2) * 2 * PI)
            
            mob.move_to(fixed_point.get_right() + RIGHT * (spring_length + mass_radius + displacement))
            
            # Update spring
            spring_end = mob.get_left()
            spring_start = fixed_point.get_right()
            spring.put_start_and_end_on(spring_start, spring_end)
        
        # Start oscillation
        mass.add_updater(update_mass)
        spring.add_updater(lambda m: m)  # Keep spring updated by mass updater
        
        self.wait(1)  # 6-7s: Transient
        
        self.wait(1)  # 7-8s: Transition to steady state
        
        # Show transient to steady state text
        self.play(
            Write(transient_text),
            Write(arrow_text),
            Write(steady_text),
            run_time=1
        )
        
        # Pulse force arrow in sync with displacement
        for _ in range(2):
            self.play(
                force_arrow.animate.set_stroke_width(12),
                rate_func=there_and_back,
                run_time=0.5
            )
            self.wait(0.5)
        
        # Show resonance label
        self.play(
            Write(resonance_label),
            run_time=0.5
        )
        self.play(
            FadeOut(resonance_label),
            run_time=0.5
        )
        
        # Scene 4: Summary & freeze (10-12s)
        # Remove updaters to freeze motion
        mass.remove_updater(update_mass)
        spring.remove_updater(lambda m: m)
        
        # Show amplitude indicator
        self.play(
            Create(amp_arrow),
            Write(amp_label),
            run_time=1
        )
        
        # Show final amplitude equation
        self.play(
            Write(amp_eq),
            run_time=1
        )
        
        # Hold final frame
        self.wait(1)