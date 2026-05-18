from manim import *

class Acto8(Scene):
    def construct(self):
        self.camera.background_color = "#020304"

        # =========================
        # FONDO
        # =========================
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
            y_range=[-4.5, 4.5, 1],
            background_line_style={
                "stroke_color": "#00ff99",
                "stroke_opacity": 0.025,
                "stroke_width": 1,
            },
            axis_config={"stroke_opacity": 0}
        )
        self.play(FadeIn(grid), run_time=0.8)

        # =========================
        # RED CENTRAL
        # =========================
        centro = Dot(point=ORIGIN, radius=0.08, color="#b7ffe3")

        arriba = Dot(point=UP * 2.0, radius=0.07, color="#00ff99")
        abajo = Dot(point=DOWN * 2.0, radius=0.07, color="#00ff99")
        izq = Dot(point=LEFT * 3.0, radius=0.07, color="#00ff99")
        der = Dot(point=RIGHT * 3.0, radius=0.07, color="#00ff99")
        sup_izq = Dot(point=LEFT * 2.1 + UP * 1.3, radius=0.07, color="#00ff99")
        sup_der = Dot(point=RIGHT * 2.1 + UP * 1.3, radius=0.07, color="#00ff99")
        inf_izq = Dot(point=LEFT * 2.1 + DOWN * 1.3, radius=0.07, color="#00ff99")
        inf_der = Dot(point=RIGHT * 2.1 + DOWN * 1.3, radius=0.07, color="#00ff99")

        nodos = VGroup(
            centro, arriba, abajo, izq, der,
            sup_izq, sup_der, inf_izq, inf_der
        )

        conexiones = VGroup(
            Line(centro.get_center(), arriba.get_center(), color="#00ccff"),
            Line(centro.get_center(), abajo.get_center(), color="#00ccff"),
            Line(centro.get_center(), izq.get_center(), color="#00ccff"),
            Line(centro.get_center(), der.get_center(), color="#00ccff"),
            Line(centro.get_center(), sup_izq.get_center(), color="#00ccff"),
            Line(centro.get_center(), sup_der.get_center(), color="#00ccff"),
            Line(centro.get_center(), inf_izq.get_center(), color="#00ccff"),
            Line(centro.get_center(), inf_der.get_center(), color="#00ccff"),
            Line(sup_izq.get_center(), arriba.get_center(), color="#00ff99"),
            Line(sup_der.get_center(), arriba.get_center(), color="#00ff99"),
            Line(inf_izq.get_center(), abajo.get_center(), color="#00ff99"),
            Line(inf_der.get_center(), abajo.get_center(), color="#00ff99"),
            Line(sup_izq.get_center(), izq.get_center(), color="#00ff99"),
            Line(inf_izq.get_center(), izq.get_center(), color="#00ff99"),
            Line(sup_der.get_center(), der.get_center(), color="#00ff99"),
            Line(inf_der.get_center(), der.get_center(), color="#00ff99"),
        ).set_stroke(width=2.1, opacity=0.7)

        self.play(
            LaggedStart(*[FadeIn(n, scale=0.8) for n in nodos], lag_ratio=0.05),
            run_time=1.2
        )
        self.play(
            LaggedStart(*[Create(c) for c in conexiones], lag_ratio=0.03),
            run_time=1.6
        )
        self.wait(0.6)

        # =========================
        # PUNTO DE QUIEBRE
        # =========================
        falla = Circle(radius=0.35, color="#ff3b5c").move_to(centro.get_center())
        falla.set_stroke(width=5, opacity=0.9)

        self.play(Create(falla), run_time=0.6)

        lineas_rojas = VGroup(
            Line(centro.get_center(), arriba.get_center(), color="#ff3b5c"),
            Line(centro.get_center(), der.get_center(), color="#ff3b5c"),
            Line(centro.get_center(), sup_der.get_center(), color="#ff3b5c"),
        ).set_stroke(width=3.2, opacity=0.9)

        self.play(
            Transform(conexiones[0], lineas_rojas[0]),
            Transform(conexiones[3], lineas_rojas[1]),
            Transform(conexiones[5], lineas_rojas[2]),
            run_time=0.9
        )

        onda = Circle(radius=0.45, color="#ff3b5c").move_to(ORIGIN).set_stroke(width=4, opacity=0.8)
        self.add(onda)
        self.play(onda.animate.scale(6).set_opacity(0), run_time=1.4)
        self.remove(onda)

        # Atenuar la red, dejando clara la fragilidad
        self.play(
            nodos.animate.set_opacity(0.35),
            conexiones.animate.set_opacity(0.22),
            run_time=1.0
        )

        self.play(
            centro.animate.set_opacity(1).set_color("#ff3b5c").scale(1.5),
            run_time=0.8
        )

        self.wait(0.8)

        # =========================
        # FRASE FINAL
        # =========================
        frase = Text(
            "No atacaron al usuario.\nAtacaron la confianza.",
            font="Times New Roman",
            font_size=42,
            color=WHITE,
            weight=BOLD
        )
        frase.move_to(ORIGIN)

        sombra = frase.copy().set_color(BLACK).set_opacity(0.45).shift(DOWN * 0.08 + RIGHT * 0.08)
        glow1 = frase.copy().set_color("#00ff99").set_opacity(0.18).shift(LEFT * 0.04)
        glow2 = frase.copy().set_color("#00ccff").set_opacity(0.14).shift(RIGHT * 0.04)

        self.play(
            FadeOut(nodos),
            FadeOut(conexiones),
            FadeOut(falla),
            run_time=1.0
        )

        self.play(
            FadeIn(sombra),
            FadeIn(glow1),
            FadeIn(glow2),
            Write(frase),
            run_time=2.2
        )

        self.play(
            glow1.animate.shift(RIGHT * 0.06),
            glow2.animate.shift(LEFT * 0.06),
            run_time=0.12
        )
        self.play(
            glow1.animate.shift(LEFT * 0.06),
            glow2.animate.shift(RIGHT * 0.06),
            run_time=0.12
        )

        self.wait(3)