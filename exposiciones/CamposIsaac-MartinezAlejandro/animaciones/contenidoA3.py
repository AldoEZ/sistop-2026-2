from manim import *

class Acto3(Scene):
    def construct(self):
        self.camera.background_color = "#020304"

        # Fondo
        grid = NumberPlane(
            x_range=[-8, 8, 1],
            y_range=[-4.5, 4.5, 1],
            background_line_style={
                "stroke_color": "#00ff99",
                "stroke_opacity": 0.04,
                "stroke_width": 1,
            },
            axis_config={"stroke_opacity": 0}
        )
        self.play(FadeIn(grid), run_time=1)

        # =========================
        # FUNCIÓN NODO CIRCULAR
        # =========================
        def nodo(texto, radio=0.95, borde="#00ff99", relleno="#07110d", fsize=24):
            circ = Circle(
                radius=radio,
                stroke_color=borde,
                stroke_width=2.5,
                fill_color=relleno,
                fill_opacity=0.78
            )
            txt = Text(
                texto,
                font="Times New Roman",
                font_size=fsize,
                color=WHITE
            )
            txt.move_to(circ.get_center())
            return VGroup(circ, txt)

        # Nodos principales
        repo = nodo("Repo", radio=0.85, fsize=24)
        pub = nodo("Publicación", radio=1.05, fsize=22)
        comp = nodo("Build", radio=0.9, fsize=24)
        lib = nodo("liblzma", radio=0.95, fsize=22)

        flujo = VGroup(repo, pub, comp, lib).arrange(RIGHT, buff=1.1)
        flujo.shift(UP * 1.2)

        # Flechas del flujo
        f1 = Arrow(repo.get_right(), pub.get_left(), buff=0.1, color="#00ccff")
        f2 = Arrow(pub.get_right(), comp.get_left(), buff=0.1, color="#00ccff")
        f3 = Arrow(comp.get_right(), lib.get_left(), buff=0.1, color="#00ccff")

        self.play(
            LaggedStart(
                FadeIn(repo, scale=0.85),
                FadeIn(pub, scale=0.85),
                FadeIn(comp, scale=0.85),
                FadeIn(lib, scale=0.85),
                lag_ratio=0.18
            ),
            run_time=2
        )

        self.play(
            GrowArrow(f1),
            GrowArrow(f2),
            GrowArrow(f3),
            run_time=1.5
        )

        self.wait(0.5)

        # =========================
        # NODO MALICIOSO
        # =========================
        mal = nodo(
            "Payload",
            radio=0.75,
            borde="#ff3b5c",
            relleno="#26060c",
            fsize=22
        )
        mal.move_to(DOWN * 2.2)

        flecha_mal = Arrow(
            mal.get_top(),
            pub.get_bottom(),
            buff=0.1,
            color="#ff3b5c",
            stroke_width=5
        )

        self.play(FadeIn(mal, scale=0.9), run_time=0.8)
        self.play(GrowArrow(flecha_mal), run_time=0.8)

        # Pulso rojo en Publicación
        pulso_pub = Circle(radius=1.2, color="#ff3b5c").move_to(pub.get_center())
        pulso_pub.set_stroke(width=5, opacity=0.9)

        self.play(Create(pulso_pub), run_time=0.6)
        self.play(FadeOut(pulso_pub), run_time=0.5)

        # Cambiar color de publicación a comprometido
        self.play(pub[0].animate.set_stroke("#ff3b5c").set_fill("#22070c", opacity=0.85), run_time=0.8)

        self.wait(0.4)

        # =========================
        # PROPAGACIÓN HACIA BUILD
        # =========================
        rastro1 = Dot(point=f2.get_start(), color="#ff3b5c", radius=0.06)
        self.add(rastro1)
        self.play(rastro1.animate.move_to(f2.get_end()), run_time=0.9)
        self.remove(rastro1)

        pulso_comp = Circle(radius=1.05, color="#ff3b5c").move_to(comp.get_center())
        pulso_comp.set_stroke(width=5, opacity=0.9)

        self.play(Create(pulso_comp), run_time=0.6)
        self.play(FadeOut(pulso_comp), run_time=0.5)
        self.play(comp[0].animate.set_stroke("#ff3b5c").set_fill("#22070c", opacity=0.85), run_time=0.8)

        self.wait(0.4)

        # =========================
        # PROPAGACIÓN HACIA LIBLZMA
        # =========================
        rastro2 = Dot(point=f3.get_start(), color="#ff3b5c", radius=0.06)
        self.add(rastro2)
        self.play(rastro2.animate.move_to(f3.get_end()), run_time=0.9)
        self.remove(rastro2)

        pulso_lib = Circle(radius=1.1, color="#ff3b5c").move_to(lib.get_center())
        pulso_lib.set_stroke(width=5, opacity=0.9)

        self.play(Create(pulso_lib), run_time=0.6)
        self.play(FadeOut(pulso_lib), run_time=0.5)
        self.play(lib[0].animate.set_stroke("#ff3b5c").set_fill("#22070c", opacity=0.85), run_time=0.8)

        self.wait(2)