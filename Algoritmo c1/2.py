import numpy as np
import random
import sys
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class Matriz():
    def __init__(self, m):
        self.ROWNS = m
        self.COLUMNS = 3
        self.matriz = np.zeros((self.ROWNS, self.COLUMNS), dtype=float)  # m x 3
        self.Crear_Validar()
        self.vertices = []
        self.contorno_convexo = []

    def Crear_Validar(self): # Funcion para crear matriz con valores validos.
        for i in range(self.ROWNS ):
            while True:
                a = random.randint(-9, 9)
                b = random.randint(-9, 9)
                c = random.randint(1, 15)

                if a == 0 and b == 0:
                    continue

                fila = [a, b, c]

                repetida = False
                for j in range(i):
                    if np.array_equal(self.matriz[j], fila):
                        repetida = True
                        break

                if not repetida:
                    self.matriz[i] = fila
                    break

    def mostrar_matriz(self):
        print(self.matriz)

    def OBTENER_Vertices(self):  # Parte objetivo: Encontrar intersecciones => Almacenar vertices
        self.vertices = []

        for I in range(self.ROWNS):
            for J in range(I + 1, self.ROWNS):
                Spot = self.OBTENER_INTERSECCION(self.matriz[I], self.matriz[J])
                if Spot is not None:
                    self.vertices.append({
                        "x": Spot[0],
                        "y": Spot[1],
                        "interseccion": (I, J)
                    })

    def OBTENER_INTERSECCION(self,r1,r2):
        a1,b1,c1 = r1  # Linia Recta L1
        a2,b2,c2 = r2  # Linia Recta L2

        Determinante =  a1 * b2 - a2 * b1
        if Determinante == 0: # // Indica q NO hay intersección unica.
            return None
        
        x = (c1 * b2 - c2 * b1) / Determinante
        y = (a1 * c2 - a2 * c1) / Determinante  

        return (round(x, 3), round(y, 3))      
    
    def CONTORNO_CONVENXO(self):  # Algoritmo de Monotone Chain
        if len(self.vertices) < 3:                                 # Si no hay vértices, no formara contorno
            self.contorno_convexo = self.vertices.copy()
            return
        puntos = list(set((v["x"], v["y"]) for v in self.vertices)) # Quitar repetidos y convertir a lista de tuplas
        puntos.sort()

        def cross(o, a, b):# Producto cruzado 
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

        # Parte inferior del hull
        lower = []
        for p in puntos:
            while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)

        # Parte superior del hull
        upper = []
        for p in reversed(puntos):
            while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)

        hull = lower[:-1] + upper[:-1]                                 # Unir ambas partes sin repetir extremos
        self.contorno_convexo = [{"x": p[0], "y": p[1]} for p in hull] # Guardar en formato lista de diccionarios

class VentanaGrafica(QWidget):
    def __init__(self, matriz_obj):
        super().__init__()
        self.setWindowTitle("Programación Lineal - Gráficas")
        self.setGeometry(100, 100, 1400, 700)

        self.matriz_obj = matriz_obj

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.fig = Figure(figsize=(14, 6))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        self.graficar()

    def graficar(self):
        self.fig.clear()

        ax1 = self.fig.add_subplot(121)  # Gráfico izquierda
        ax2 = self.fig.add_subplot(122)  # Gráfico derecha

        # --- Obtener datos ---
        self.matriz_obj.OBTENER_Vertices()
        self.matriz_obj.CONTORNO_CONVENXO()

        vertices = self.matriz_obj.vertices
        contorno = self.matriz_obj.contorno_convexo
        restricciones = self.matriz_obj.matriz

        # --- Rango visual dinámico ---
        xs = [v["x"] for v in vertices] if vertices else [0]
        ys = [v["y"] for v in vertices] if vertices else [0]

        x_min = min(xs) - 2
        x_max = max(xs) + 2
        y_min = min(ys) - 2
        y_max = max(ys) + 2

        if x_min == x_max:
            x_min -= 5
            x_max += 5
        if y_min == y_max:
            y_min -= 5
            y_max += 5

        x_vals = np.linspace(x_min, x_max, 400)

        # =========================================================
        # GRÁFICO 1: RECTAS + TODOS LOS VÉRTICES
        # =========================================================

        ax1.axhline(0, color='black', linewidth=1.5, label="L1: y = 0")
        ax1.axvline(0, color='black', linewidth=1.5, label="L2: x = 0")
        
        for i, fila in enumerate(restricciones):
            a, b, c = fila
            nombre = f"{a}x + {b}y + {c} = 0"

            tramo = self.OBTENER_TRAMO_RECTA(i, vertices)

            if tramo is not None:
                x_ini, x_fin, y_ini, y_fin = tramo

                if b != 0:
                    x_local = np.linspace(x_ini, x_fin, 100)
                    y_local = (c - a * x_local) / b
                    ax1.plot(x_local, y_local, label=nombre)
                elif a != 0:
                    x_const = c / a
                    ax1.plot([x_const, x_const], [y_ini, y_fin], linestyle='--', label=nombre)

            else:
                if b != 0:
                    y_vals = (c - a * x_vals) / b
                    ax1.plot(x_vals, y_vals, label=nombre)
                elif a != 0:
                    x_const = c / a
                    ax1.axvline(x=x_const, linestyle='--', label=nombre)

        for i, v in enumerate(vertices, start=1):
            ax1.scatter(v["x"], v["y"], s=60)
            ax1.text(v["x"] + 0.1, v["y"] + 0.1, f"V{i}", fontsize=8)

        ax1.set_title("Rectas + Intersecciones")
        ax1.set_xlabel("X")
        ax1.set_ylabel("Y")
        ax1.grid(True)
        ax1.legend(fontsize=8)
        ax1.set_xlim(x_min, x_max)
        ax1.set_ylim(y_min, y_max)

        # =========================================================
        # GRÁFICO 2: RECTAS + CONTORNO CONVEXO
        # =========================================================

        ax2.axhline(0, color='black', linewidth=1.5, label="L1: y = 0")
        ax2.axvline(0, color='black', linewidth=1.5, label="L2: x = 0")

        for i, fila in enumerate(restricciones):
            a, b, c = fila
            nombre = f"L{i + 3}"

            tramo = self.OBTENER_TRAMO_RECTA(i, vertices)

            if tramo is not None:
                x_ini, x_fin, y_ini, y_fin = tramo

                if b != 0:
                    x_local = np.linspace(x_ini, x_fin, 100)
                    y_local = (c - a * x_local) / b
                    ax2.plot(x_local, y_local, label=nombre)
                elif a != 0:
                    x_const = c / a
                    ax2.plot([x_const, x_const], [y_ini, y_fin], linestyle='--', label=nombre)

            else:
                if b != 0:
                    y_vals = (c - a * x_vals) / b
                    ax2.plot(x_vals, y_vals, label=nombre)
                elif a != 0:
                    x_const = c / a
                    ax2.axvline(x=x_const, linestyle='--', label=nombre)

        for i, p in enumerate(contorno, start=1):
            ax2.scatter(p["x"], p["y"], s=70)
            ax2.text(p["x"] + 0.1, p["y"] + 0.1, f"C{i}", fontsize=8)

        if len(contorno) >= 3:
            x_cont = [p["x"] for p in contorno] + [contorno[0]["x"]]
            y_cont = [p["y"] for p in contorno] + [contorno[0]["y"]]

            ax2.plot(x_cont, y_cont, linestyle='-', linewidth=2, label="Contorno Convexo")
            ax2.fill(x_cont, y_cont, alpha=0.25)

        ax2.set_title("Rectas + Contorno Convexo")
        ax2.set_xlabel("X")
        ax2.set_ylabel("Y")
        ax2.grid(True)
        ax2.legend(fontsize=8)
        ax2.set_xlim(x_min, x_max)
        ax2.set_ylim(y_min, y_max)

        self.canvas.draw()

    def OBTENER_TRAMO_RECTA(self, indice_recta, vertices, margen=1):
        puntos_recta = []

        for v in vertices:
            if indice_recta in v["interseccion"]:
                puntos_recta.append((v["x"], v["y"]))

        # Si la recta toca 2 o más vértices, limitar tramo
        if len(puntos_recta) >= 2:
            xs = [p[0] for p in puntos_recta]
            ys = [p[1] for p in puntos_recta]

            return (
                min(xs) - margen,
                max(xs) + margen,
                min(ys) - margen,
                max(ys) + margen
            )

        return None
   
    def Mostrar_Datos_Graficos_CONSOLA(self):
        print("\n--- Ecuaciones de las Rectas [Ln] ---")
        print("L1: y = 0 \n L2: x = 0")
        for i, fila in enumerate(self.matriz_obj.matriz):
            a, b, c = fila
            eq = ""
            # Construir la ecuación con signos correctos
            eq += f"{a}x " if a != 0 else ""
            eq += f"+ {b}y " if b > 0 else (f"- {abs(b)}y " if b < 0 else "")
            eq += f"+ {c}" if c > 0 else (f"- {abs(c)}" if c < 0 else "")
            eq += " = 0"
            print(f"L{i + 3}: {eq}")

        print("\n--- Vértices en Intersecciones) ---")
        for i, v in enumerate(self.matriz_obj.vertices, start=1):
            x, y = v["x"], v["y"]
            print(f"V{i}: ({x}, {y})")

        print("\n--- Contorno Convexo ---")
        if len(self.matriz_obj.contorno_convexo) >= 3:
            for i, p in enumerate(self.matriz_obj.contorno_convexo, start=1):
                print(f"C{i}: ({p['x']}, {p['y']})")
        else:
            print("No hay suficientes puntos para formar contorno convexo.")
                
    
if __name__ == "__main__":
    print("--- Sistema de encontrar vertices y contorno convexo ---")
    while True:
        # // Crear Matriz de forma automatica, de m x 3. [0-1]
        m = int(input("Ingrese la cantidad de filas a evaluar en un rango valido de 2 ≤ x ≤ 8: "))
        if 2 <= m <= 8:
            break
        else:
            print("Valor fuera de rango.")

    matriz = Matriz(m)
    matriz.mostrar_matriz()

    app = QApplication(sys.argv)
    ventana = VentanaGrafica(matriz)
    ventana.Mostrar_Datos_Graficos_CONSOLA()
    ventana.show()
    sys.exit(app.exec())