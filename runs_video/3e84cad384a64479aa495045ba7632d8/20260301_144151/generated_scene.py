from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Colors
        MASS_COLOR = BLUE
        SPRING_COLOR = GREEN
        FORCE_COLOR = RED
        TEXT_COLOR = WHITE
        
        # Create wall
        wall = Rectangle(
            height=2.5,
            width=0.3,
            fill_color=GRAY,
            fill_opacity=1,
            stroke_width=2
        ).to_edge(LEFT, buff=1.0)
        
        # Spring parameters
        spring_start = wall.get_right() + RIGHT * 0.15
        spring_rest_length = 3.0
        
        # Mass
        mass = Square(
            side_length=0.8,
            fill_color=MASS_COLOR,
            fill_opacity=0.8,
            stroke_width=2
        )
        mass.move_to(spring_start + RIGHT * spring_rest_length)
        mass.shift(DOWN * 1.5)
        
        # Baseline
        baseline = Line(
            wall.get_bottom() + DOWN * 0.5,
            wall.get_bottom() + DOWN * 0.5 + RIGHT * 8,
            color=GRAY,
            stroke_width=1
        )
        
        # Labels - using Tex with raw strings
        title = Tex(r"Forced Vibration", font_size=48, color=YELLOW)
        title.to_edge(UP, buff=0.5)
        
        mass_label = Tex(r"Mass m", color=TEXT_COLOR, font_size=24)
        mass_label.next_to(mass, DOWN, buff=0.3)
        
        spring_label = Tex(r"Spring k", color=TEXT_COLOR, font_size=24)
        spring_label.next_to(spring_start + RIGHT * spring_rest_length/2, UP, buff=0.3)
        
        # Scene 1: Setup
        self.play(Write(title))
        self.wait(0.5)
        
        self.play(
            Create(wall),
            Create(baseline),
            run_time=1
        )
        
        # Create spring
        spring = always_redraw(lambda: ParametricFunction(
            lambda t: spring_start + 
                     RIGHT * (t * (mass.get_left()[0] - spring_start[0])) +
                     UP * 0.3 * np.sin(12 * PI * t),
            t_range=[0, 1],
            color=SPRING_COLOR,
            stroke_width=4
        ))
        
        self.play(
            Create(spring),
            Create(mass),
            run_time=1
        )
        
        self.play(
            Write(mass_label),
            Write(spring_label),
            run_time=1
        )
        self.wait(1)
        
        # Scene 2: Introduce driving force
        force_eq = MathTex(r"F(t) = F_0 \cos(\omega_d t)", color=FORCE_COLOR, font_size=36)
        force_eq.to_edge(DOWN, buff=0.8)
        
        force_label = Tex(r"Driving Force", color=FORCE_COLOR, font_size=28)
        force_label.next_to(force_eq, UP, buff=0.3)
        
        self.play(
            Write(force_label),
            Write(force_eq),
            run_time=1
        )
        
        # Force arrow
        force_arrow = always_redraw(lambda: Arrow(
            start=mass.get_top() + UP * 0.2,
            end=mass.get_top() + UP * (1.2 + 0.5 * np.sin(2 * self.time)),
            color=FORCE_COLOR,
            stroke_width=6,
            buff=0,
            max_tip_length_to_length_ratio=0.2
        ))
        
        self.play(GrowArrow(force_arrow))
        self.wait(1)
        
        # Animate forced vibration
        mass_start_x = mass.get_x()
        
        def update_mass(mob, dt):
            t = self.time
            # Forced oscillation with some phase
            displacement = 0.8 * np.sin(2 * t - 0.5)
            mob.move_to([mass_start_x + displacement, mass.get_y(), 0])
        
        mass.add_updater(update_mass)
        
        self.wait(3)
        
        # Scene 3: Show resonance condition
        resonance_title = Tex(r"Resonance Condition", color=YELLOW, font_size=36)
        resonance_title.move_to(title)
        
        resonance_eq = MathTex(r"\omega_d \approx \omega_0", color=RED, font_size=42)
        resonance_eq.next_to(force_eq, UP, buff=0.5)
        
        natural_freq = MathTex(r"\omega_0 = \sqrt{\frac{k}{m}}", color=GREEN, font_size=36)
        natural_freq.next_to(resonance_eq, UP, buff=0.5)
        
        self.play(
            ReplacementTransform(title, resonance_title),
            Write(natural_freq),
            run_time=1
        )
        self.wait(1)
        
        self.play(Write(resonance_eq))
        self.wait(2)
        
        # Increase amplitude to show resonance
        amplitude_factor = ValueTracker(0.8)
        
        def update_mass_resonance(mob, dt):
            t = self.time
            displacement = amplitude_factor.get_value() * np.sin(2 * t - 0.5)
            mob.move_to([mass_start_x + displacement, mass.get_y(), 0])
        
        mass.remove_updater(update_mass)
        mass.add_updater(update_mass_resonance)
        
        self.play(amplitude_factor.animate.set_value(2.0), run_time=2)
        self.wait(2)
        
        # Scene 4: Steady state
        steady_state = Tex(r"Steady State", color=BLUE, font_size=36)
        steady_state.move_to(resonance_title)
        
        steady_eq = MathTex(r"x(t) = A \cos(\omega_d t - \phi)", color=BLUE, font_size=36)
        steady_eq.next_to(natural_freq, UP, buff=0.5)
        
        amplitude_label = MathTex(
            r"A = \frac{F_0/m}{\sqrt{(\omega_0^2 - \omega_d^2)^2 + (2\beta\omega_d)^2}}", 
            color=YELLOW, font_size=28
        )
        amplitude_label.next_to(steady_eq, UP, buff=0.3)
        
        self.play(
            ReplacementTransform(resonance_title, steady_state),
            Write(steady_eq),
            Write(amplitude_label),
            run_time=1.5
        )
        
        self.wait(3)
        
        # Final fade out
        self.play(
            FadeOut(force_label),
            FadeOut(force_eq),
            FadeOut(natural_freq),
            FadeOut(resonance_eq),
            FadeOut(steady_eq),
            FadeOut(amplitude_label),
            run_time=1
        )
        
        self.wait(1)
        
        # Keep animating while fading
        self.play(
            FadeOut(steady_state),
            FadeOut(mass_label),
            FadeOut(spring_label),
            FadeOut(wall),
            FadeOut(baseline),
            FadeOut(spring),
            FadeOut(mass),
            FadeOut(force_arrow),
            run_time=2
        )