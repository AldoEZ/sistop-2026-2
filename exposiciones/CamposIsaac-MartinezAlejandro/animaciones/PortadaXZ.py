from manim import *
import random
import numpy as np

class PortadaXZ(Scene):
    def construct(self):
        self.camera.background_color = "#020304"

        fondo = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            fill_color="#020304",
            fill_opacity=1,
            stroke_opacity=0
        )
        self.add(fondo)

        grid = NumberPlane(
            x_range=[-8, 8, 1],
            y_range=[-5, 5, 1],
            background_line_style={
                "stroke_color": GREEN,
                "stroke_opacity": 0.08,
                "stroke_width": 1,
            },
            axis_config={"stroke_opacity": 0},
        )
        self.add(grid)

        random.seed(10)
        circuitos = VGroup()

        for _ in range(18):
            x = random.uniform(-7, 7)
            y = random.uniform(-3.5, 3.5)

            puntos = [
                np.array([x, y, 0]),
                np.array([x + random.choice([0.8, 1.2, 1.6]), y, 0]),
                np.array([x + random.choice([0.8, 1.2, 1.6]), y + random.choice([-1, 1]) * random.choice([0.6, 1.0, 1.4]), 0]),
            ]

            linea = VMobject()
            linea.set_points_as_corners(puntos)
            linea.set_stroke(color=GREEN, width=2, opacity=0.35)

            nodo = Dot(point=puntos[-1], radius=0.035, color=GREEN).set_opacity(0.7)
            circuitos.add(linea, nodo)

        self.play(
            LaggedStart(*[Create(obj) for obj in circuitos], lag_ratio=0.03),
            run_time=1.6
        )

        halo = Circle(radius=3)
        halo.set_fill(GREEN, opacity=0.08)
        halo.set_stroke(opacity=0)
        self.add(halo)

        marco = RoundedRectangle(
            width=11,
            height=3.3,
            corner_radius=0.15,
            stroke_color=GREEN,
            stroke_width=2.5,
            fill_color="#07110b",
            fill_opacity=0.55
        )

        marco2 = RoundedRectangle(
            width=10.6,
            height=2.95,
            corner_radius=0.12,
            stroke_color=GREEN,
            stroke_width=1.2,
            fill_opacity=0
        )

        titulo = Text(
            "EL ATAQUE DE LA CADENA\nDE SUMINISTRO XZ",
            color=WHITE,
            weight=BOLD,
            font_size=34,
            line_spacing=0.85
        )

        glitch1 = titulo.copy().set_color(GREEN).set_opacity(0.35).shift(LEFT * 0.05)
        glitch2 = titulo.copy().set_color(BLUE_E).set_opacity(0.25).shift(RIGHT * 0.05)
        sombra = titulo.copy().set_color(BLACK).set_opacity(0.4).shift(DOWN * 0.08 + RIGHT * 0.08)

        self.play(FadeIn(marco), FadeIn(marco2), run_time=1.0)
        self.play(FadeIn(sombra), FadeIn(glitch1), FadeIn(glitch2), Write(titulo), run_time=1.8)

        self.play(
            glitch1.animate.shift(RIGHT * 0.08),
            glitch2.animate.shift(LEFT * 0.08),
            run_time=0.12
        )
        self.play(
            glitch1.animate.shift(LEFT * 0.08),
            glitch2.animate.shift(RIGHT * 0.08),
            run_time=0.12
        )

        self.play(
            halo.animate.scale(1.05).set_opacity(0.12),
            marco.animate.set_stroke(width=3),
            run_time=1
        )

        self.wait(2)