from manim import *

class Acto2(Scene):
    def construct(self):
        self.camera.background_color = "#020304"

        # =========================
        # FONDO SUTIL TIPO HACKER
        # =========================
        grid = NumberPlane(
            x_range=[-8, 8, 1],
            y_range=[-4.5, 4.5, 1],
            background_line_style={
                "stroke_color": "#00ff99",
                "stroke_opacity": 0.05,
                "stroke_width": 1,
            },
            axis_config={"stroke_opacity": 0}
        )
        self.play(FadeIn(grid), run_time=1)

        # =========================
        # BLOQUES DE LA CADENA
        # =========================
        def bloque(texto, color_borde="#00ff99", ancho=2.3, alto=0.9):
            caja = RoundedRectangle(
                width=ancho,
                height=alto,
                corner_radius=0.08,
                stroke_color=color_borde,
                stroke_width=2,
                fill_color="#07110d",
                fill_opacity=0.75
            )
            txt = Text(
                texto,
                font_size=26,
                color=WHITE
            )
            txt.move_to(caja.get_center())
            return VGroup(caja, txt)

        b1 = bloque("Desarrollador")
        b2 = bloque("Repositorio")
        b3 = bloque("Paquete")
        b4 = bloque("Sistema")

        cadena = VGroup(b1, b2, b3, b4).arrange(RIGHT, buff=0.55)
        cadena.shift(UP * 1.2)

        flecha1 = Arrow(b1.get_right(), b2.get_left(), buff=0.08, color="#00ccff")
        flecha2 = Arrow(b2.get_right(), b3.get_left(), buff=0.08, color="#00ccff")
        flecha3 = Arrow(b3.get_right(), b4.get_left(), buff=0.08, color="#00ccff")

        self.play(
            LaggedStart(
                FadeIn(b1, shift=UP * 0.15),
                FadeIn(b2, shift=UP * 0.15),
                FadeIn(b3, shift=UP * 0.15),
                FadeIn(b4, shift=UP * 0.15),
                lag_ratio=0.2
            ),
            run_time=2.5
        )

        self.play(
            GrowArrow(flecha1),
            GrowArrow(flecha2),
            GrowArrow(flecha3),
            run_time=1.8
        )

        self.wait(0.8)

        # =========================
        # EXPLICACIÓN VISUAL
        # =========================
        explicacion1 = Text(
            "Un ataque a la cadena de suministro\nno entra por la fuerza al sistema final.",
            font="Times New Roman",
            font_size=34,
            color=WHITE
        )
        explicacion1.move_to(DOWN * 1.0)

        self.play(FadeIn(explicacion1, shift=UP * 0.2), run_time=2)
        self.wait(2.5)

        # Resaltar el paquete como punto comprometido
        alerta = SurroundingRectangle(
            b3,
            color="#ff3b5c",
            buff=0.12
        )
        x_mark = Cross(b3, stroke_color="#ff3b5c", stroke_width=6).scale(0.8)

        self.play(Create(alerta), run_time=0.8)
        self.play(Create(x_mark), run_time=0.8)
        self.wait(0.5)

        explicacion2 = Text(
            "Compromete una pieza confiable...\ny deja que la confianza haga el resto.",
            font="Times New Roman",
            font_size=34,
            color="#d9fff2"
        )
        explicacion2.move_to(DOWN * 2.3)

        self.play(FadeIn(explicacion2, shift=UP * 0.2), run_time=2)
        self.wait(2.5)

        # =========================
        # PROPAGACIÓN VISUAL
        # =========================
        brillo1 = SurroundingRectangle(b2, color="#00ff99", buff=0.10)
        brillo2 = SurroundingRectangle(b4, color="#00ff99", buff=0.10)

        self.play(
            ReplacementTransform(alerta.copy(), brillo1),
            run_time=1.0
        )
        self.play(
            ReplacementTransform(brillo1, brillo2),
            run_time=1.0
        )
        self.wait(0.5)

        cierre = Text(
            "Si comprometes un eslabón,\ncomprometes todo el camino.",
            font="Times New Roman",
            font_size=38,
            color=WHITE,
            weight=BOLD
        )
        cierre.move_to(DOWN * 0.8)

        self.play(
            FadeOut(explicacion1),
            FadeOut(explicacion2),
            FadeOut(x_mark),
            FadeOut(brillo2),
            run_time=1
        )

        self.play(FadeIn(cierre, shift=UP * 0.25), run_time=2.2)
        self.wait(3)