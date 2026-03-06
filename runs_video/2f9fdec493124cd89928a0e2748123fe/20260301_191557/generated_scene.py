from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Setup coordinate system
        axes = Axes(
            x_range=[-2, 6, 1],
            y_range=[-4, 4, 1],
            x_length=8,
            y_length=6,
            axis_config={"color": BLUE_D, "stroke_width": 2},
        ).shift(DOWN * 0.5)
        
        # Parabola: y^2 = 4x
        # Use parametric plot with proper parameter range
        parabola = axes.plot_parametric_curve(
            lambda t: np.array([t**2/4, t, 0]),
            t_range=[-4, 4],
            color=YELLOW,
            stroke_width=4
        )
        
        # Point P on parabola (x=1, y=2)
        P = Dot(axes.c2p(1, 2), color=RED, radius=0.08)
        P_label = MathTex(r"P", color=RED).next_to(P, UP+RIGHT, buff=0.1)
        
        # Focus F at (1,0)
        F = Dot(axes.c2p(1, 0), color=GREEN, radius=0.08)
        F_label = MathTex(r"F", color=GREEN).next_to(F, DOWN, buff=0.1)
        
        # Directrix line x = -1
        directrix = DashedLine(
            axes.c2p(-1, -4),
            axes.c2p(-1, 4),
            color=PURPLE,
            stroke_width=3,
            dash_length=0.1
        )
        directrix_label = MathTex(r"l", color=PURPLE).next_to(
            directrix, LEFT, buff=0.1
        ).shift(UP * 0.5)
        
        # Scene 1: Setup (0-3 seconds)
        self.play(Create(axes), run_time=1)
        self.wait(0.2)
        
        self.play(Create(parabola), run_time=1)
        parabola_label = Text("Parabola", color=YELLOW).scale(0.7).to_edge(UP)
        self.play(Write(parabola_label), run_time=0.5)
        self.wait(0.3)
        
        self.play(FadeIn(P), Write(P_label), run_time=0.5)
        self.play(FadeIn(F), Write(F_label), run_time=0.5)
        self.play(Create(directrix), Write(directrix_label), run_time=0.5)
        self.wait(0.5)
        
        # Scene 2: Geometric Construction (3-9 seconds)
        # Segment PF
        PF = Line(P.get_center(), F.get_center(), color=BLUE, stroke_width=3)
        PF_mid = PF.point_from_proportion(0.5)
        PF_label = MathTex(r"PF", color=BLUE).scale(0.7).next_to(
            PF_mid, LEFT, buff=0.1
        )
        
        self.play(Create(PF), Write(PF_label), run_time=1)
        self.wait(0.2)
        
        # Point Q: projection of P onto directrix
        Q_point = axes.c2p(-1, 2)
        Q = Dot(Q_point, color=ORANGE, radius=0.08)
        Q_label = MathTex(r"Q", color=ORANGE).next_to(Q, LEFT, buff=0.1)
        
        # Line from P perpendicular to directrix
        PQ = DashedLine(P.get_center(), Q_point, color=ORANGE, stroke_width=2.5)
        PQ_mid = (P.get_center() + Q_point) / 2
        PQ_label = MathTex(r"PQ", color=ORANGE).scale(0.7).next_to(
            PQ_mid, UP, buff=0.1
        )
        
        self.play(Create(PQ), Write(PQ_label), run_time=0.8)
        self.play(FadeIn(Q), Write(Q_label), run_time=0.7)
        self.wait(0.5)
        
        # Segment FQ
        FQ = DashedLine(F.get_center(), Q_point, color=PINK, stroke_width=2.5)
        FQ_mid = (F.get_center() + Q_point) / 2
        FQ_label = MathTex(r"FQ", color=PINK).scale(0.7).next_to(
            FQ_mid, DOWN, buff=0.1
        )
        
        self.play(Create(FQ), Write(FQ_label), run_time=0.8)
        self.wait(0.2)
        
        # Perpendicular bisector of FQ (tangent line)
        mid_point = (F.get_center() + Q_point) / 2
        mid_dot = Dot(mid_point, color=WHITE, radius=0.06)
        
        # Direction vector of FQ
        dir_vec = Q_point - F.get_center()
        perp_vec = np.array([-dir_vec[1], dir_vec[0], 0])
        perp_vec = perp_vec / np.linalg.norm(perp_vec) * 3
        
        tangent_line = Line(
            mid_point - perp_vec,
            mid_point + perp_vec,
            color=RED,
            stroke_width=4
        )
        
        self.play(FadeIn(mid_dot), run_time=0.5)
        self.play(Create(tangent_line), run_time=1)
        self.play(FadeOut(mid_dot), run_time=0.3)
        
        # Calculate position for tangent label
        tangent_label_pos = tangent_line.point_from_proportion(0.7)
        tangent_label = Text("Tangent Line at P", color=RED).scale(0.6).next_to(
            tangent_label_pos, UP+RIGHT, buff=0.1
        )
        self.play(Write(tangent_label), run_time=0.8)
        self.wait(0.5)
        
        # Fade out construction lines
        construction_group = VGroup(PF, PF_label, PQ, PQ_label, FQ, FQ_label, Q, Q_label)
        self.play(FadeOut(construction_group), run_time=1)
        self.wait(0.5)
        
        # Scene 3: Generalization & Conclusion (9-12 seconds)
        key_text = Text(
            "Key Property: Tangent is the perpendicular bisector of FQ",
            color=YELLOW
        ).scale(0.5).to_edge(UP, buff=0.3)
        
        self.play(Write(key_text), run_time=1.5)
        self.wait(0.5)
        
        # Final summary
        summary = Text(
            "Method applies to all conic sections",
            color=GREEN
        ).scale(0.6).to_edge(DOWN, buff=0.3)
        
        self.play(Write(summary), run_time=1)
        self.wait(0.5)
        
        # Fade out
        fade_group = VGroup(
            axes, parabola, parabola_label,
            P, P_label, F, F_label,
            directrix, directrix_label,
            tangent_line, tangent_label,
            key_text, summary
        )
        self.play(FadeOut(fade_group), run_time=1)