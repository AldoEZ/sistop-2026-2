from manim import *
import random
import numpy as np

class FraseImpacto(Scene):
    def construct(self):
        self.camera.background_color = "#020304"

        # Fondo base
        fondo = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            fill_color="#020304",
            fill_opacity=1,
            stroke_opacity=0
        )
        self.add(fondo)

        # Grid tenue
        grid = NumberPlane(
            x_range=[-8, 8, 1],
            y_range=[-5, 5, 1],
            background_line_style={
                "stroke_color": "#00ff99",
                "stroke_opacity": 0.06,
                "stroke_width": 1,
            },
            axis_config={"stroke_opacity": 0}
        )
        self.add(grid)

        # Circuitos decorativos
        random.seed(10)
        circuitos = VGroup()
        colores = ["#00ff99", "#00ccff", "#66ffcc"]

        for _ in range(22):
            x = random.uniform(-7, 7)
            y = random.uniform(-3.8, 3.8)
            dx1 = random.choice([0.8, 1.2, 1.6])
            dy = random.choice([-1.2, -0.8, 0.8, 1.2])
            dx2 = random.choice([0.6, 1.0, 1.4])

            puntos = [
                np.array([x, y, 0]),
                np.array([x + dx1, y, 0]),
                np.array([x + dx1, y + dy, 0]),
                np.array([x + dx1 + dx2, y + dy, 0]),
            ]

            linea = VMobject()
            linea.set_points_as_corners(puntos)
            linea.set_stroke(
                color=random.choice(colores),
                width=2,
                opacity=0.28
            )

            nodo = Dot(
                point=puntos[-1],
                radius=0.03,
                color="#b7ffe3"
            ).set_opacity(0.6)

            circuitos.add(linea, nodo)

        self.add(circuitos)

        # Halo central
        halo = Circle(radius=2.9, stroke_opacity=0)
        halo.set_fill("#00ff99", opacity=0.07)

        halo2 = Circle(radius=3.7, stroke_opacity=0)
        halo2.set_fill("#00ccff", opacity=0.05)

        self.add(halo2, halo)

        # Marco central
        marco = RoundedRectangle(
            width=11.6,
            height=3.9,
            corner_radius=0.18,
            stroke_color="#00ff99",
            stroke_width=2.3,
            fill_color="#06110d",
            fill_opacity=0.58
        )

        marco2 = RoundedRectangle(
            width=11.2,
            height=3.55,
            corner_radius=0.15,
            stroke_color="#00ccff",
            stroke_width=1.1,
            fill_opacity=0
        )

        # Frase principal
        frase = Text(
            "Una sola línea de código malicioso,\nescondida durante meses,\ncasi compromete la seguridad\nde internet entero.",
            font_size=30,
            color="#eafff7",
            weight=BOLD,
            line_spacing=0.9
        )

        # Capas glitch
        glitch1 = frase.copy().set_color("#00ff99").set_opacity(0.22).shift(LEFT * 0.05)
        glitch2 = frase.copy().set_color("#00ccff").set_opacity(0.18).shift(RIGHT * 0.05)
        sombra = frase.copy().set_color(BLACK).set_opacity(0.45).shift(DOWN * 0.08 + RIGHT * 0.08)

        bloque = VGroup(marco, marco2, sombra, glitch1, glitch2, frase)
        bloque.move_to(ORIGIN)

        self.play(FadeIn(marco), FadeIn(marco2), run_time=1.0)
        self.play(FadeIn(sombra), FadeIn(glitch1), FadeIn(glitch2), Write(frase), run_time=2.4)

        # Micro-glitch
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

        # Pulso final
        self.play(
            marco.animate.set_stroke(color="#b7ffe3", width=3),
            halo.animate.scale(1.05).set_opacity(0.1),
            halo2.animate.scale(1.03).set_opacity(0.07),
            run_time=1
        )

        self.wait(2)