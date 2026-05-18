from manim import *
import numpy as np

class S1_PipelineInyeccion(Scene):
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

        def etapa(linea1, linea2, color_borde="#00ff99", w=2.75, h=1.55):
            rect = RoundedRectangle(
                width=w, height=h, corner_radius=0.1,
                stroke_color=color_borde, stroke_width=2,
                fill_color="#07110d", fill_opacity=0.85
            )
            t1 = Text(linea1, font_size=20, color=color_borde, weight=BOLD)
            t2 = Text(linea2, font_size=17, color=WHITE)
            t1.move_to(rect.get_center() + UP * 0.3)
            t2.move_to(rect.get_center() + DOWN * 0.3)
            return VGroup(rect, t1, t2)

        e0 = etapa(".tar.gz",  "build-to-host.m4",  color_borde="#00ccff", w=2.9)
        e1 = etapa("ETAPA 1",  "m4 → bash script",  color_borde="#00ff99")
        e2 = etapa("ETAPA 2",  "bash → .o file",    color_borde="#00ff99")
        e3 = etapa("liblzma",  "backdoored",         color_borde="#ff3b5c")

        pipeline = VGroup(e0, e1, e2, e3)
        pipeline.arrange(RIGHT, buff=0.45).move_to(ORIGIN)

        a01 = Arrow(e0.get_right(), e1.get_left(), buff=0.06, color="#00ccff")
        a12 = Arrow(e1.get_right(), e2.get_left(), buff=0.06, color="#00ff99")
        a23 = Arrow(e2.get_right(), e3.get_left(), buff=0.06, color="#ff3b5c")

        self.play(FadeIn(e0, shift=UP * 0.2), run_time=0.9)
        self.wait(0.3)

        for arrow, box, color in [
            (a01, e1, "#00ff99"),
            (a12, e2, "#00ff99"),
            (a23, e3, "#ff3b5c"),
        ]:
            self.play(GrowArrow(arrow), run_time=0.65)
            self.play(FadeIn(box, shift=RIGHT * 0.15), run_time=0.85)
            glow = SurroundingRectangle(box, color=color, buff=0.1)
            self.play(Create(glow), run_time=0.3)
            self.play(FadeOut(glow), run_time=0.3)
            self.wait(0.3)

        # liblzma pulsa — está infectado
        for _ in range(3):
            p = SurroundingRectangle(e3, color="#ff3b5c", buff=0.12)
            self.play(Create(p), run_time=0.25)
            self.play(FadeOut(p), run_time=0.25)

        self.wait(2)