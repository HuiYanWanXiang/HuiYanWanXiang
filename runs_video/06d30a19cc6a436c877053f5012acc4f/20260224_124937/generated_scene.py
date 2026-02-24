from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Title
        title = Text("Forced Oscillation", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        # Mass-spring-damper diagram
        # Wall
        wall = Rectangle(height=1.5, width=0.2, color=GRAY, fill_opacity=1)
        wall.to_edge(LEFT, buff=1)
        
        # Spring start and end positions
        spring_start = wall.get_right() + RIGHT * 0.1
        spring_end_default = spring_start + RIGHT * 2
        
        # Initial spring (static)
        spring = ParametricFunction(
            lambda t: spring_start + t * (spring_end_default - spring_start) + 
                     UP * 0.3 * np.sin(10 * t) * (1 - t),
            t_range=[0, 1, 0.01],
            color=GREEN
        )
        
        # Mass
        mass = Square(side_length=0.8, color=YELLOW, fill_opacity=0.8)
        mass.move_to(spring_end_default + RIGHT * 0.5)
        
        # Damper (simplified)
        damper = VGroup(
            Line(spring_start + UP * 0.5, spring_end_default + UP * 0.5, color=RED),
            Circle(radius=0.1, color=RED, fill_opacity=0.3).move_to(
                (spring_start + spring_end_default) / 2 + UP * 0.5
            )
        )
        
        # External force arrow
        force_arrow = Arrow(
            mass.get_left() + LEFT * 0.5,
            mass.get_left(),
            color=PURPLE,
            buff=0,
            stroke_width=6
        )
        
        # Labels
        mass_label = MathTex(r"m", color=YELLOW).next_to(mass, UP, buff=0.1)
        spring_label = MathTex(r"k", color=GREEN).next_to(spring, UP, buff=0.1)
        damper_label = MathTex(r"c", color=RED).next_to(damper, UP, buff=0.1)
        force_label = MathTex(r"F(t)", color=PURPLE).next_to(force_arrow, LEFT, buff=0.1)
        
        # Draw system
        self.play(
            FadeIn(wall),
            FadeIn(mass),
            Create(spring),
            Create(damper),
            GrowArrow(force_arrow)
        )
        self.play(
            Write(mass_label),
            Write(spring_label),
            Write(damper_label),
            Write(force_label)
        )
        self.wait(1)
        
        # Equation of motion
        eq_title = Text("Equation of Motion:", font_size=32)
        eq_title.next_to(title, DOWN, buff=0.5)
        self.play(Write(eq_title))
        
        equation = MathTex(
            r"m\ddot{x} + c\dot{x} + kx = F_0\cos(\omega t)",
            font_size=36
        )
        equation.next_to(eq_title, DOWN, buff=0.3)
        self.play(Write(equation))
        self.wait(1.5)
        
        # Solution form
        sol_title = Text("Steady-state solution:", font_size=32)
        sol_title.next_to(equation, DOWN, buff=0.5)
        self.play(Write(sol_title))
        
        solution = MathTex(
            r"x(t) = A\cos(\omega t - \phi)",
            font_size=36
        )
        solution.next_to(sol_title, DOWN, buff=0.3)
        self.play(Write(solution))
        self.wait(1)
        
        # Amplitude and phase
        amp_eq = MathTex(
            r"A = \frac{F_0}{\sqrt{(k-m\omega^2)^2 + (c\omega)^2}}",
            font_size=32
        )
        amp_eq.next_to(solution, DOWN, buff=0.5)
        phase_eq = MathTex(
            r"\phi = \tan^{-1}\left(\frac{c\omega}{k-m\omega^2}\right)",
            font_size=32
        )
        phase_eq.next_to(amp_eq, DOWN, buff=0.3)
        
        self.play(Write(amp_eq))
        self.wait(0.8)
        self.play(Write(phase_eq))
        self.wait(1.5)
        
        # Animate oscillation
        time = ValueTracker(0)
        
        # Create updatable copies for animation
        mass_anim = mass.copy()
        spring_anim = spring.copy()
        damper_anim = damper.copy()
        force_arrow_anim = force_arrow.copy()
        
        # Remove original static elements
        self.remove(mass, spring, damper, force_arrow)
        
        # Add updatable versions
        self.add(mass_anim, spring_anim, damper_anim, force_arrow_anim)
        
        # Define updaters
        def update_mass(m):
            displacement = 1.5 * np.sin(2 * time.get_value())
            m.move_to(spring_end_default + RIGHT * 0.5 + RIGHT * displacement)
        
        def update_spring(s):
            current_mass_pos = mass_anim.get_left()
            s.become(ParametricFunction(
                lambda t: spring_start + t * (current_mass_pos - spring_start) + 
                         UP * 0.3 * np.sin(10 * t) * (1 - t),
                t_range=[0, 1, 0.01],
                color=GREEN
            ))
        
        def update_damper(d):
            current_mass_pos = mass_anim.get_left()
            d.become(VGroup(
                Line(spring_start + UP * 0.5, current_mass_pos + UP * 0.5, color=RED),
                Circle(radius=0.1, color=RED, fill_opacity=0.3).move_to(
                    (spring_start + current_mass_pos) / 2 + UP * 0.5
                )
            ))
        
        def update_force_arrow(a):
            current_mass_pos = mass_anim.get_left()
            a.become(Arrow(
                current_mass_pos + LEFT * 0.5,
                current_mass_pos,
                color=PURPLE,
                buff=0,
                stroke_width=6
            ))
        
        # Add updaters
        mass_anim.add_updater(update_mass)
        spring_anim.add_updater(update_spring)
        damper_anim.add_updater(update_damper)
        force_arrow_anim.add_updater(update_force_arrow)
        
        # Animate
        self.play(time.animate.set_value(4 * PI), run_time=8, rate_func=linear)
        
        # Clean up
        mass_anim.clear_updaters()
        spring_anim.clear_updaters()
        damper_anim.clear_updaters()
        force_arrow_anim.clear_updaters()
        
        self.wait(1)