from manim import *

class Acto7(Scene):
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
                "stroke_opacity": 0.035,
                "stroke_width": 1,
            },
            axis_config={"stroke_opacity": 0}
        )
        self.play(FadeIn(grid), run_time=0.8)

        # =========================
        # FUNCIÓN DE NODO
        # =========================
        def nodo(texto, radio=0.9, borde="#00ff99", relleno="#07110d", fsize=20):
            circ = Circle(
                radius=radio,
                stroke_color=borde,
                stroke_width=2.4,
                fill_color=relleno,
                fill_opacity=0.82
            )
            txt = Text(
                texto,
                font="Times New Roman",
                font_size=fsize,
                color=WHITE
            )
            txt.move_to(circ.get_center())
            return VGroup(circ, txt)

        # =========================
        # AMENAZA CENTRAL
        # =========================
        amenaza = nodo(
            "RIESGO",
            radio=1.0,
            borde="#ff3b5c",
            relleno="#22070c",
            fsize=24
        )
        amenaza.move_to(ORIGIN)

        self.play(FadeIn(amenaza, scale=0.85), run_time=0.9)

        # Ondas del riesgo
        onda1 = Circle(radius=1.2, color="#ff3b5c").move_to(ORIGIN).set_stroke(width=4, opacity=0.7)
        onda2 = Circle(radius=1.6, color="#ff3b5c").move_to(ORIGIN).set_stroke(width=3, opacity=0.45)
        self.play(Create(onda1), Create(onda2), run_time=0.7)
        self.play(
            onda1.animate.scale(1.8).set_opacity(0),
            onda2.animate.scale(2.0).set_opacity(0),
            run_time=1.0
        )
        self.remove(onda1, onda2)

        # =========================
        # ACTORES DE RESPUESTA
        # =========================
        fedora = nodo("Fedora", radio=0.82, fsize=22)
        debian = nodo("Debian", radio=0.82, fsize=22)
        redhat = nodo("Red Hat", radio=0.88, fsize=20)
        comunidad = nodo("Comunidad", radio=1.0, fsize=18)
        seguridad = nodo("Seguridad", radio=0.95, fsize=18)
        parche = nodo("Rollback", radio=0.88, fsize=20)

        fedora.move_to(LEFT * 4.7 + UP * 1.7)
        debian.move_to(RIGHT * 4.7 + UP * 1.7)
        redhat.move_to(LEFT * 4.5 + DOWN * 1.8)
        comunidad.move_to(RIGHT * 4.6 + DOWN * 1.8)
        seguridad.move_to(UP * 3.0)
        parche.move_to(DOWN * 3.0)

        actores = VGroup(fedora, debian, redhat, comunidad, seguridad, parche)

        self.play(
            LaggedStart(*[FadeIn(a, scale=0.8) for a in actores], lag_ratio=0.12),
            run_time=1.8
        )

        # =========================
        # CONEXIONES HACIA EL CENTRO
        # =========================
        conexiones = VGroup(
            Line(fedora.get_center(), amenaza.get_center(), color="#00ccff"),
            Line(debian.get_center(), amenaza.get_center(), color="#00ccff"),
            Line(redhat.get_center(), amenaza.get_center(), color="#00ccff"),
            Line(comunidad.get_center(), amenaza.get_center(), color="#00ccff"),
            Line(seguridad.get_center(), amenaza.get_center(), color="#00ccff"),
            Line(parche.get_center(), amenaza.get_center(), color="#00ccff"),
        ).set_stroke(width=2.2, opacity=0.5)

        self.play(LaggedStart(*[Create(c) for c in conexiones], lag_ratio=0.08), run_time=1.3)

        # =========================
        # MOVIMIENTO DE CONTENCIÓN
        # =========================
        self.play(
            fedora.animate.shift(RIGHT * 1.1 + DOWN * 0.4),
            debian.animate.shift(LEFT * 1.1 + DOWN * 0.4),
            redhat.animate.shift(RIGHT * 1.0 + UP * 0.4),
            comunidad.animate.shift(LEFT * 1.0 + UP * 0.4),
            seguridad.animate.shift(DOWN * 0.9),
            parche.animate.shift(UP * 0.9),
            run_time=1.6
        )

        # Rehacer conexiones tras moverse
        nuevas_conexiones = VGroup(
            Line(fedora.get_center(), amenaza.get_center(), color="#00ff99"),
            Line(debian.get_center(), amenaza.get_center(), color="#00ff99"),
            Line(redhat.get_center(), amenaza.get_center(), color="#00ff99"),
            Line(comunidad.get_center(), amenaza.get_center(), color="#00ff99"),
            Line(seguridad.get_center(), amenaza.get_center(), color="#00ff99"),
            Line(parche.get_center(), amenaza.get_center(), color="#00ff99"),
        ).set_stroke(width=2.6, opacity=0.65)

        self.play(Transform(conexiones, nuevas_conexiones), run_time=0.9)

        # =========================
        # CORTES DE PROPAGACIÓN
        # =========================
        cortes = VGroup()
        for linea in conexiones:
            corte = Cross(
                linea,
                stroke_color="#00ff99",
                stroke_width=4
            ).scale(0.22)
            cortes.add(corte)

        self.play(LaggedStart(*[Create(c) for c in cortes], lag_ratio=0.06), run_time=1.0)

        # =========================
        # BARRERA ALREDEDOR DEL RIESGO
        # =========================
        barrera1 = Circle(radius=1.45, color="#00ff99").move_to(ORIGIN).set_stroke(width=4, opacity=0.8)
        barrera2 = Circle(radius=1.8, color="#00ccff").move_to(ORIGIN).set_stroke(width=3, opacity=0.5)
        barrera3 = Circle(radius=2.15, color="#00ff99").move_to(ORIGIN).set_stroke(width=2.5, opacity=0.35)

        self.play(Create(barrera1), Create(barrera2), Create(barrera3), run_time=1.0)

        # El riesgo se reduce visualmente
        self.play(
            amenaza[0].animate.scale(0.82).set_opacity(0.75),
            amenaza[1].animate.scale(0.82).set_opacity(0.75),
            run_time=0.9
        )

        # =========================
        # SELLADO FINAL
        # =========================
        hexagono = RegularPolygon(
            n=6,
            radius=2.4,
            color="#00ff99"
        ).move_to(ORIGIN).set_stroke(width=3, opacity=0.75)

        self.play(Create(hexagono), run_time=0.9)

        pulso = Circle(radius=2.5, color="#00ff99").move_to(ORIGIN).set_stroke(width=4, opacity=0.7)
        self.play(Create(pulso), run_time=0.6)
        self.play(FadeOut(pulso), run_time=0.4)

        # Atenuar el riesgo, reforzar contención
        self.play(
            amenaza.animate.set_opacity(0.4),
            actores.animate.set_opacity(0.95),
            run_time=0.8
        )

        self.wait(2)