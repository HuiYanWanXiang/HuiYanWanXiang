from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Colors
        MASS_COLOR = BLUE
        SPRING_COLOR = YELLOW
        FORCE_COLOR = RED
        TEXT_COLOR = WHITE
        
        # Parameters
        NATURAL_FREQ = 2.0
        DRIVING_FREQ = 2.5
        AMPLITUDE = 1.5
        
        # Time tracker
        time = ValueTracker(0)
        
        # ========== PHYSICAL SYSTEM ==========
        
        # Wall
        wall = Rectangle(height=2, width=0.2, color=WHITE, fill_opacity=1)
        wall.to_edge(LEFT, buff=1)
        
        # Spring (simplified as a zigzag)
        def spring_updater(mob):
            t = time.get_value()
            # Position calculation
            if t < 2:
                # Free oscillation
                x = 0.5 * np.sin(NATURAL_FREQ * t)
            elif t < 4:
                # Transition period
                blend = (t - 2) / 2
                x = (1-blend)*0.5*np.sin(NATURAL_FREQ*t) + blend*AMPLITUDE*np.sin(DRIVING_FREQ*t)
            else:
                # Forced oscillation (steady state)
                x = AMPLITUDE * np.sin(DRIVING_FREQ * t)
            
            start = wall.get_right() + RIGHT * 0.1
            end = start + RIGHT * (2 + x)
            
            # Create spring path
            path = VMobject()
            points = []
            num_coils = 6
            for i in range(21):
                frac = i/20
                pos = interpolate(start, end, frac)
                offset = UP * 0.1 * np.sin(frac * num_coils * PI)
                points.append(pos + offset)
            
            path.set_points_as_corners(points)
            mob.become(path)
        
        spring = VMobject(color=SPRING_COLOR, stroke_width=3)
        spring.add_updater(spring_updater)
        
        # Mass
        mass = Circle(radius=0.3, color=MASS_COLOR, fill_opacity=0.8)
        mass.add_updater(lambda m: m.move_to(
            wall.get_right() + RIGHT * (2 + 0.5*np.sin(NATURAL_FREQ*time.get_value())) + UP*0.5
            if time.get_value() < 2 else
            wall.get_right() + RIGHT * (2 + AMPLITUDE*np.sin(DRIVING_FREQ*time.get_value())) + UP*0.5
        ))
        
        # Equilibrium line
        equilibrium = DashedLine(
            wall.get_right() + RIGHT*2 + UP*1.5,
            wall.get_right() + RIGHT*2 + DOWN*0.5,
            color=GREEN,
            dash_length=0.1
        )
        
        # Driving force indicator (appears at t=2)
        force_indicator = Arrow(
            start=RIGHT*3 + UP*0.5,
            end=RIGHT*2.5 + UP*0.5,
            color=FORCE_COLOR,
            stroke_width=6,
            max_tip_length_to_length_ratio=0.3
        )
        force_indicator.set_opacity(0)
        
        # ========== TEXT EXPLANATIONS ==========
        
        # Title
        title = Text("Forced Oscillation", font_size=36, color=TEXT_COLOR)
        title.to_edge(UP)
        
        # Phase labels
        free_label = Text("Free Oscillation", color=BLUE, font_size=24)
        free_label.to_edge(RIGHT).shift(UP*2)
        
        forced_label = Text("Forced Oscillation", color=RED, font_size=24)
        forced_label.to_edge(RIGHT).shift(UP*1)
        forced_label.set_opacity(0)
        
        # Equations
        free_eq = MathTex(r"m\ddot{x} + kx = 0", font_size=28, color=BLUE)
        free_eq.next_to(free_label, DOWN, buff=0.3)
        
        forced_eq = MathTex(r"m\ddot{x} + kx = F_0\cos(\omega t)", font_size=28, color=RED)
        forced_eq.next_to(forced_label, DOWN, buff=0.3)
        forced_eq.set_opacity(0)
        
        # Resonance note
        resonance_text = Text("Amplitude grows at resonance!", color=YELLOW, font_size=24)
        resonance_text.to_edge(RIGHT).shift(DOWN*0.5)
        resonance_text.set_opacity(0)
        
        # ========== ANIMATION ==========
        
        # Add all objects
        self.add(wall, spring, mass, equilibrium)
        self.add(title, free_label, free_eq)
        self.add(forced_label, forced_eq, force_indicator, resonance_text)
        
        # Initial setup
        self.play(
            Create(wall),
            Create(spring),
            Create(mass),
            Create(equilibrium),
            Write(title),
            Write(free_label),
            Write(free_eq),
            run_time=2
        )
        
        # Animate free oscillation for 2 seconds
        self.play(
            time.animate.set_value(2),
            rate_func=linear,
            run_time=2
        )
        
        # Transition to forced oscillation
        self.play(
            FadeOut(free_label),
            FadeOut(free_eq),
            FadeIn(forced_label),
            FadeIn(forced_eq),
            FadeIn(force_indicator),
            run_time=1
        )
        
        # Show resonance text
        self.play(
            FadeIn(resonance_text),
            run_time=0.5
        )
        
        # Animate forced oscillation
        self.play(
            time.animate.set_value(8),
            rate_func=linear,
            run_time=4
        )
        
        # Final emphasis
        self.play(
            Flash(mass, color=YELLOW, line_length=0.2),
            run_time=0.5
        )
        
        self.wait(1)