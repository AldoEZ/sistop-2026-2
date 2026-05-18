from manim import *
import numpy as np


class S2_AnomaliaRendimiento(Scene):
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

        # ── Foto de Andres Freund ──────────────────────────────────────
        # Reemplaza "IMAGEN_FREUND.png" con la ruta real a la imagen
        foto = ImageMobject("IMAGEN_FREUND.png").set_height(3.4)
        foto.move_to(LEFT * 4.2)
        marco_foto = Rectangle(
            width=foto.width + 0.28, height=foto.height + 0.28,
            stroke_color="#00ccff", stroke_width=2, fill_opacity=0
        ).move_to(foto.get_center())
        nombre = Text("Andres Freund", font_size=20, color="#00ccff")
        nombre.next_to(marco_foto, DOWN, buff=0.2)

        self.play(FadeIn(foto), Create(marco_foto), run_time=1.2)
        self.play(FadeIn(nombre), run_time=0.5)
        self.wait(0.4)

        # ── Barras de comparación ──────────────────────────────────────
        BASELINE_Y = -2.0

        linea_base = Line(
            np.array([0.8, BASELINE_Y, 0]),
            np.array([6.5, BASELINE_Y, 0]),
            color="#00ff99", stroke_width=1.8, stroke_opacity=0.5
        )
        self.play(Create(linea_base), run_time=0.6)

        # Barra normal: 0.299 s
        h_norm = 1.55
        barra_norm = Rectangle(
            width=1.3, height=h_norm,
            fill_color="#00ff99", fill_opacity=0.82,
            stroke_color="#00ff99", stroke_width=1.5
        ).move_to(np.array([2.2, BASELINE_Y + h_norm / 2, 0]))

        etiq_norm = Text("0.3s", font_size=24, color="#00ff99")
        etiq_norm.move_to(np.array([2.2, BASELINE_Y + h_norm + 0.45, 0]))

        self.play(GrowFromEdge(barra_norm, DOWN), run_time=1.2)
        self.play(FadeIn(etiq_norm), run_time=0.5)
        self.wait(0.5)

        # Barra backdoor: 0.807 s  (≈ 2.7× más lenta, proporcional)
        h_back = 4.15
        barra_back = Rectangle(
            width=1.3, height=h_back,
            fill_color="#ff3b5c", fill_opacity=0.82,
            stroke_color="#ff3b5c", stroke_width=1.5
        ).move_to(np.array([4.5, BASELINE_Y + h_back / 2, 0]))

        etiq_back = Text("0.8s", font_size=24, color="#ff3b5c")
        etiq_back.move_to(np.array([4.5, BASELINE_Y + h_back + 0.45, 0]))

        self.play(GrowFromEdge(barra_back, DOWN), run_time=1.8)
        self.play(FadeIn(etiq_back), run_time=0.5)

        # Pulsos de alarma
        for _ in range(2):
            p = SurroundingRectangle(barra_back, color="#ff3b5c", buff=0.12)
            self.play(Create(p), run_time=0.3)
            self.play(FadeOut(p), run_time=0.3)

        self.wait(2)