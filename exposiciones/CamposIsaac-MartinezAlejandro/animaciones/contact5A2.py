from manim import *
import numpy as np

class S2_RastreoInvestigacion(Scene):
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

        # Lupa geométrica
        lente = Circle(radius=0.5, stroke_color="#00ccff", stroke_width=3.5, fill_opacity=0)
        mango = Line(
            np.array([0.35, -0.35, 0]),
            np.array([0.75, -0.75, 0]),
            color="#00ccff", stroke_width=4
        )
        lupa = VGroup(lente, mango).move_to(np.array([-7.5, 3.0, 0]))

        # Nodos de la investigación
        labels_seq  = ["SSH\nlento",  "xz\nupdate",  "perf\ntrace",  "IFUNC\nhook",  "RSA\nredir."]
        colores_seq = ["#00ff99",     "#00ff99",      "#00ccff",      "#ffaa00",      "#ff3b5c"]
        posiciones  = [
            np.array([-5.5, 0.3, 0]),
            np.array([-2.5, 0.3, 0]),
            np.array([ 0.5, 0.3, 0]),
            np.array([ 3.5, 0.3, 0]),
            np.array([ 6.0, 0.3, 0]),
        ]

        nodos = []
        for lbl, col, pos in zip(labels_seq, colores_seq, posiciones):
            circ = Circle(radius=0.82, stroke_color=col, stroke_width=2.2,
                          fill_color="#07110d", fill_opacity=0.88)
            txt  = Text(lbl, font_size=19, color=WHITE)
            txt.move_to(circ.get_center())
            node = VGroup(circ, txt).move_to(pos)
            node.set_opacity(0.28)
            nodos.append(node)

        # Todos los nodos aparecen tenues
        self.play(
            LaggedStart(*[FadeIn(n) for n in nodos], lag_ratio=0.12),
            run_time=1.8
        )
        self.play(FadeIn(lupa, scale=0.7), run_time=0.8)

        # La lupa recorre cada nodo y lo "activa"
        for i, (node, col) in enumerate(zip(nodos, colores_seq)):
            target_lupa = node.get_center() + UP * 1.75
            self.play(lupa.animate.move_to(target_lupa), run_time=0.7)
            self.play(node.animate.set_opacity(1), run_time=0.4)
            node[0].set_stroke(color=col, width=3)

            if i < len(nodos) - 1:
                arr = Arrow(
                    node.get_right(), nodos[i + 1].get_left(),
                    buff=0.1, color=col, stroke_width=1.8
                )
                self.play(GrowArrow(arr), run_time=0.5)

        # Hallazgo: nodo RSA pulsa rojo
        for _ in range(2):
            p = Circle(radius=1.1, color="#ff3b5c") \
                .move_to(nodos[-1].get_center()).set_stroke(width=4, opacity=0.85)
            self.play(Create(p), run_time=0.3)
            self.play(p.animate.scale(2.3).set_opacity(0), run_time=0.65)
            self.remove(p)

        self.wait(2)