from manim import *
import numpy as np

class S3_AuthBypass(Scene):
    def construct(self):
        self.camera.background_color = "#020304"

        fondo = Rectangle(
            width=config.frame_width, height=config.frame_height,
            fill_color="#020304", fill_opacity=1, stroke_opacity=0
        )
        self.add(fondo)

        grid = NumberPlane(
            x_range=[-8, 8, 1], y_range=[-4.5, 4.5, 1],
            background_line_style={
                "stroke_color": "#00ff99", "stroke_opacity": 0.05, "stroke_width": 1,
            },
            axis_config={"stroke_opacity": 0}
        )
        self.play(FadeIn(grid), run_time=0.7)

        def caja(texto, color="#00ff99", w=2.8, h=0.88):
            rect = RoundedRectangle(
                width=w, height=h, corner_radius=0.1,
                stroke_color=color, stroke_width=2,
                fill_color="#07110d", fill_opacity=0.85
            )
            txt = Text(texto, font_size=20, color=WHITE)
            txt.move_to(rect.get_center())
            return VGroup(rect, txt)

        # Atacante (izquierda)
        atacante_circ = Circle(radius=0.75, stroke_color="#ff3b5c", stroke_width=2.5,
                               fill_color="#22070c", fill_opacity=0.88)
        atk_txt = Text("ATK", font_size=22, color="#ff3b5c", weight=BOLD)
        atacante_grp = VGroup(atacante_circ, atk_txt)
        atacante_grp.move_to(LEFT * 5.8)
        atk_txt.move_to(atacante_circ.get_center())

        # Diamante de decisión (fingerprint check)
        diamond = Square(side_length=1.5, stroke_color="#ffaa00", stroke_width=2.2,
                         fill_color="#13100d", fill_opacity=0.88)
        diamond.rotate(PI / 4)
        d_lbl = Text("key\ncheck", font_size=17, color="#ffaa00")
        diamond_grp = VGroup(diamond, d_lbl)
        diamond_grp.move_to(LEFT * 1.5)
        d_lbl.move_to(diamond.get_center())

        # Ruta A — clave incorrecta → auth normal (arriba)
        normal_box = caja("normal auth", color="#00ff99", w=2.7)
        normal_box.move_to(np.array([3.8, 2.4, 0]))

        # Ruta B — clave del atacante → system() → RCE (abajo)
        sys_box = caja("system()", color="#ff3b5c", w=2.4)
        sys_box.move_to(np.array([3.0, -2.4, 0]))
        rce_box = caja("RCE", color="#ff3b5c", w=1.6)
        rce_box.move_to(np.array([5.8, -2.4, 0]))

        # Flechas (definidas después de posicionar los objetos)
        arrow_in   = Arrow(atacante_grp.get_right(), diamond_grp.get_left(),
                           buff=0.1, color="#ff3b5c")
        arrow_up   = Arrow(diamond.get_top(),    normal_box.get_left(),
                           buff=0.1, color="#00ff99")
        arrow_down = Arrow(diamond.get_bottom(), sys_box.get_left(),
                           buff=0.1, color="#ff3b5c")
        arrow_s_r  = Arrow(sys_box.get_right(), rce_box.get_left(),
                           buff=0.08, color="#ff3b5c")

        # ── Construcción del diagrama ──────────────────────────
        self.play(FadeIn(atacante_grp, shift=RIGHT * 0.2), run_time=1.0)
        self.play(GrowArrow(arrow_in), run_time=0.8)
        self.play(FadeIn(diamond_grp, scale=0.85), run_time=0.9)
        self.wait(0.4)

        # Ruta normal
        self.play(GrowArrow(arrow_up), run_time=0.7)
        self.play(FadeIn(normal_box, shift=LEFT * 0.15), run_time=0.7)
        self.wait(0.3)

        # Ruta del ataque
        self.play(GrowArrow(arrow_down), run_time=0.7)
        self.play(FadeIn(sys_box, shift=LEFT * 0.15), run_time=0.7)
        self.play(GrowArrow(arrow_s_r), FadeIn(rce_box, shift=LEFT * 0.15), run_time=0.8)
        self.wait(0.4)

        # Destacar la ruta del ataque
        for box in [sys_box, rce_box]:
            p = SurroundingRectangle(box, color="#ff3b5c", buff=0.1)
            self.play(Create(p), run_time=0.28)
            self.play(FadeOut(p), run_time=0.28)

        # Explosión en RCE
        explosion = Circle(radius=0.5, color="#ff3b5c") \
            .move_to(rce_box.get_center()).set_stroke(width=5, opacity=0.9)
        self.play(Create(explosion), run_time=0.3)
        self.play(explosion.animate.scale(4.5).set_opacity(0), run_time=1.0)
        self.remove(explosion)

        self.wait(2)