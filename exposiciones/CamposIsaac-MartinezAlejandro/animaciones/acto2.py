from manim import *

class Acto2(Scene):
    def construct(self):
        self.camera.background_color = "#020304"

        # Texto principal
        texto = Text(
            "ACTO II: EL CONTEXTO",
            font="Times New Roman",
            font_size=80,
            color=WHITE,
            weight=BOLD
        )

        # Centrar el texto
        texto.move_to(ORIGIN)

        # Aparición lenta tipo documental
        self.play(FadeIn(texto, shift=UP * 0.3), run_time=5)

        # Mantener en pantalla
        self.wait(2)