from manim import *
import numpy as np


class S3_EscalaPotencial(Scene):
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
                "stroke_color": "#00ff99", "stroke_opacity": 0.04, "stroke_width": 1,
            },
            axis_config={"stroke_opacity": 0}
        )
        self.play(FadeIn(grid), run_time=0.7)

        # Grilla de puntos (servidores)
        n_filas, n_cols = 8, 13
        dots = []
        for fila in range(n_filas):
            for col in range(n_cols):
                x = -6.0 + col * 1.0
                y = -2.6 + fila * 0.78
                d = Dot(point=np.array([x, y, 0]), radius=0.13, color="#00ff99")
                dots.append(d)

        self.play(
            LaggedStart(*[FadeIn(d, scale=0.4) for d in dots], lag_ratio=0.012),
            run_time=2.0
        )
        self.wait(0.5)

        # Punto cero (centro de la grilla)
        center_idx = (n_filas // 2) * n_cols + (n_cols // 2)
        center_pos = dots[center_idx].get_center()

        # Pulso inicial
        self.play(dots[center_idx].animate.set_color("#ff3b5c"), run_time=0.3)
        p0 = Circle(radius=0.3, color="#ff3b5c") \
            .move_to(center_pos).set_stroke(width=5, opacity=0.9)
        self.play(Create(p0), run_time=0.3)
        self.play(p0.animate.scale(4).set_opacity(0), run_time=0.7)
        self.remove(p0)

        # Infección se propaga radialmente (ordenada por distancia al centro)
        sorted_dots = sorted(
            dots,
            key=lambda d: np.linalg.norm(d.get_center() - center_pos)
        )
        self.play(
            LaggedStart(
                *[d.animate.set_color("#ff3b5c") for d in sorted_dots],
                lag_ratio=0.04
            ),
            run_time=3.5
        )

        # Onda expansiva final
        onda = Circle(radius=0.5, color="#ff3b5c") \
            .move_to(center_pos).set_stroke(width=6, opacity=0.85)
        self.play(Create(onda), run_time=0.3)
        self.play(onda.animate.scale(14).set_opacity(0), run_time=1.2)
        self.remove(onda)

        self.wait(2)