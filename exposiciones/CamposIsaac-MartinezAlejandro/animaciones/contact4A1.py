from manim import *
import numpy as np


class S1_CadenaDependencias(Scene):
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
        self.play(FadeIn(grid), run_time=0.8)

        def bloque(texto, color_borde="#00ff99", ancho=3.2, alto=0.85):
            caja = RoundedRectangle(
                width=ancho, height=alto, corner_radius=0.1,
                stroke_color=color_borde, stroke_width=2.2,
                fill_color="#07110d", fill_opacity=0.85
            )
            txt = Text(texto, font_size=26, color=WHITE)
            txt.move_to(caja.get_center())
            return VGroup(caja, txt)

        b_sshd       = bloque("sshd")
        b_systemd    = bloque("systemd")
        b_libsystemd = bloque("libsystemd")
        b_liblzma    = bloque("liblzma")

        cadena = VGroup(b_sshd, b_systemd, b_libsystemd, b_liblzma)
        cadena.arrange(DOWN, buff=0.62).move_to(ORIGIN)

        f1 = Arrow(b_sshd.get_bottom(),       b_systemd.get_top(),    buff=0.08, color="#00ccff")
        f2 = Arrow(b_systemd.get_bottom(),     b_libsystemd.get_top(), buff=0.08, color="#00ccff")
        f3 = Arrow(b_libsystemd.get_bottom(),  b_liblzma.get_top(),    buff=0.08, color="#00ccff")

        self.play(
            LaggedStart(
                FadeIn(b_sshd,       shift=LEFT * 0.2),
                FadeIn(b_systemd,    shift=LEFT * 0.2),
                FadeIn(b_libsystemd, shift=LEFT * 0.2),
                FadeIn(b_liblzma,    shift=LEFT * 0.2),
                lag_ratio=0.22
            ),
            run_time=2.2
        )
        self.play(GrowArrow(f1), GrowArrow(f2), GrowArrow(f3), run_time=1.5)
        self.wait(0.8)

        # liblzma se compromete
        self.play(
            b_liblzma[0].animate.set_stroke(color="#ff3b5c", width=3).set_fill("#22070c", opacity=0.92),
            run_time=0.9
        )
        for _ in range(2):
            p = Circle(radius=1.15, color="#ff3b5c") \
                .move_to(b_liblzma.get_center()).set_stroke(width=4, opacity=0.85)
            self.play(Create(p), run_time=0.3)
            self.play(p.animate.scale(2.5).set_opacity(0), run_time=0.65)
            self.remove(p)

        # Infección sube por la cadena
        for arrow, target in [(f3, b_libsystemd), (f2, b_systemd), (f1, b_sshd)]:
            self.play(
                arrow.animate.set_color("#ff3b5c"),
                target[0].animate.set_stroke(color="#ff3b5c", width=3).set_fill("#22070c", opacity=0.88),
                run_time=0.65
            )
            p = Circle(radius=0.9, color="#ff3b5c") \
                .move_to(target.get_center()).set_stroke(width=3, opacity=0.75)
            self.play(Create(p), run_time=0.25)
            self.play(p.animate.scale(2.3).set_opacity(0), run_time=0.5)
            self.remove(p)

        self.wait(2)