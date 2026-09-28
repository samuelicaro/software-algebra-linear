# Software de Álgebra Linear
# Autores: Gabriel Braga, João Paulo Dias, Jean Kaio, Kairo Nogueira e Samuel Ícaro.

import math
import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def matriz_escala(sx, sy, inversa=False):
    if inversa:
        sx, sy = 1 / sx, 1 / sy
    return [[sx, 0], [0, sy]]


def matriz_rotacao(angulo, inversa=False):
    if inversa:
        angulo = -angulo
    a = math.radians(angulo)
    c, s = math.cos(a), math.sin(a)
    return [[c, -s], [s, c]]


def matriz_reflexao(eixo):
    eixo = eixo.lower()
    if eixo == "x":
        return [[1, 0], [0, -1]]
    if eixo == "y":
        return [[-1, 0], [0, 1]]
    raise ValueError("Eixo deve ser 'x' ou 'y'.")


def multiplicar(a, b):
    resultado = [[0, 0], [0, 0]]
    for i in range(2):
        for j in range(2):
            for k in range(2):
                resultado[i][j] += a[i][k] * b[k][j]
    return resultado


def compor(matrizes):
    resultado = [[1, 0], [0, 1]]
    for m in matrizes:
        resultado = multiplicar(m, resultado)
    return resultado


def aplicar(matriz, ponto):
    x, y = ponto
    return (matriz[0][0] * x + matriz[0][1] * y,
            matriz[1][0] * x + matriz[1][1] * y)


def transformar(pontos, matriz):
    xs = [p[0] for p in pontos]
    ys = [p[1] for p in pontos]
    cx = (min(xs) + max(xs)) / 2
    cy = (min(ys) + max(ys)) / 2

    novos = []
    for x, y in pontos:
        nx, ny = aplicar(matriz, (x - cx, y - cy))
        novos.append((nx + cx, ny + cy))
    return novos


def para_numero(texto):
    return float(texto.strip().replace(",", "."))


def ler_pontos(texto):
    pontos = []
    for trecho in texto.split(";"):
        if not trecho.strip():
            continue
        partes = trecho.split()
        if len(partes) != 2:
            raise ValueError(f"Ponto inválido: '{trecho.strip()}'. Use 'x y'.")
        pontos.append((para_numero(partes[0]), para_numero(partes[1])))
    if not pontos:
        raise ValueError("Insira pelo menos um ponto.")
    return pontos


class App:
    def __init__(self, janela):
        self.janela = janela
        janela.title("Software de Álgebra Linear")
        janela.geometry("960x700")

        self.fila = []
        self.inversa = tk.BooleanVar(value=False)

        self.montar_interface()
        self.mostrar_parametros()
        self.plotar()

    def montar_interface(self):
        tk.Label(self.janela, text="Bem vindo ao Software Vetorial!",
                 font=("Calibri", 20)).pack(pady=(8, 0))
        tk.Label(self.janela,
                 text="Desenvolvido pelos alunos: Gabriel Braga, João Paulo Dias,\n"
                      "Jean Kaio, Kairo Nogueira e Samuel Ícaro.",
                 font=("Calibri", 10)).pack()

        corpo = tk.Frame(self.janela)
        corpo.pack(fill="both", expand=True, padx=10, pady=10)

        self.painel = tk.Frame(corpo)
        self.painel.pack(side="left", fill="y", padx=(0, 10))

        area_grafico = tk.Frame(corpo)
        area_grafico.pack(side="right", fill="both", expand=True)

        self.montar_painel()
        self.montar_grafico(area_grafico)

    def montar_painel(self):
        tk.Label(self.painel, text="Pontos (x y; x y; ...)").pack(anchor="w")
        self.entrada_pontos = tk.Entry(self.painel, width=32)
        self.entrada_pontos.insert(0, "0 0; 4 0; 4 3")
        self.entrada_pontos.pack(anchor="w")
        tk.Button(self.painel, text="Plotar pontos",
                  command=self.plotar).pack(anchor="w", pady=(4, 12))

        tk.Label(self.painel, text="Transformação").pack(anchor="w")
        self.tipo = ttk.Combobox(self.painel, state="readonly",
                                 values=("Escala", "Rotação", "Reflexão"))
        self.tipo.current(0)
        self.tipo.bind("<<ComboboxSelected>>", lambda e: self.mostrar_parametros())
        self.tipo.pack(anchor="w")

        self.frame_escala = tk.Frame(self.painel)
        self.entrada_sx = self.criar_campo(self.frame_escala, "sx", "2")
        self.entrada_sy = self.criar_campo(self.frame_escala, "sy", "2")

        self.frame_rotacao = tk.Frame(self.painel)
        self.entrada_angulo = self.criar_campo(self.frame_rotacao, "Ângulo (graus)", "90")

        self.frame_reflexao = tk.Frame(self.painel)
        self.entrada_eixo = self.criar_campo(self.frame_reflexao, "Eixo (x ou y)", "x")

        tk.Checkbutton(self.painel, text="Aplicar inversa",
                       variable=self.inversa).pack(anchor="w", pady=(6, 0))
        tk.Button(self.painel, text="Adicionar à lista",
                  command=self.adicionar).pack(anchor="w", pady=4)

        tk.Label(self.painel, text="Transformações (aplicadas em ordem)"
                 ).pack(anchor="w", pady=(10, 0))
        self.lista = tk.Listbox(self.painel, height=6, width=34, exportselection=False)
        self.lista.pack(anchor="w")

        botoes = tk.Frame(self.painel)
        botoes.pack(anchor="w", pady=4)
        tk.Button(botoes, text="Remover selecionada",
                  command=self.remover).pack(side="left")
        tk.Button(botoes, text="Limpar",
                  command=self.limpar).pack(side="left", padx=(6, 0))

        tk.Button(self.painel, text="Aplicar todas",
                  font=("Calibri", 12),
                  command=self.aplicar).pack(anchor="w", pady=(10, 0))

    def criar_campo(self, pai, rotulo, padrao):
        tk.Label(pai, text=rotulo).pack(anchor="w")
        entrada = tk.Entry(pai, width=12)
        entrada.insert(0, padrao)
        entrada.pack(anchor="w")
        return entrada

    def montar_grafico(self, pai):
        figura = Figure(figsize=(5, 4), dpi=100)
        self.ax = figura.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(figura, master=pai)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def mostrar_parametros(self):
        self.frame_escala.pack_forget()
        self.frame_rotacao.pack_forget()
        self.frame_reflexao.pack_forget()

        escolhido = {
            "Escala": self.frame_escala,
            "Rotação": self.frame_rotacao,
            "Reflexão": self.frame_reflexao,
        }[self.tipo.get()]
        escolhido.pack(anchor="w", after=self.tipo)

    def montar_transformacao(self):
        tipo = self.tipo.get()
        inversa = self.inversa.get()

        if tipo == "Escala":
            sx = para_numero(self.entrada_sx.get())
            sy = para_numero(self.entrada_sy.get())
            descricao = f"Escala (sx={sx:g}, sy={sy:g})"
            matriz = matriz_escala(sx, sy, inversa)
        elif tipo == "Rotação":
            ang = para_numero(self.entrada_angulo.get())
            descricao = f"Rotação {ang:g}°"
            matriz = matriz_rotacao(ang, inversa)
        else:
            eixo = self.entrada_eixo.get().strip().lower()
            descricao = f"Reflexão em {eixo}"
            matriz = matriz_reflexao(eixo)

        if inversa and tipo != "Reflexão":
            descricao += " (inversa)"

        return descricao, matriz

    def adicionar(self):
        try:
            self.fila.append(self.montar_transformacao())
        except (ValueError, ZeroDivisionError) as erro:
            messagebox.showerror("Entrada inválida", str(erro))
            return
        self.atualizar_lista()

    def remover(self):
        selecionadas = self.lista.curselection()
        if selecionadas:
            del self.fila[selecionadas[0]]
            self.atualizar_lista()

    def limpar(self):
        self.fila.clear()
        self.atualizar_lista()

    def atualizar_lista(self):
        self.lista.delete(0, "end")
        for i, (descricao, _) in enumerate(self.fila, start=1):
            self.lista.insert("end", f"{i}. {descricao}")

    def plotar(self):
        try:
            pontos = ler_pontos(self.entrada_pontos.get())
        except ValueError as erro:
            messagebox.showerror("Entrada inválida", str(erro))
            return
        self.desenhar(pontos, [])

    def aplicar(self):
        try:
            pontos = ler_pontos(self.entrada_pontos.get())
        except ValueError as erro:
            messagebox.showerror("Entrada inválida", str(erro))
            return

        if not self.fila:
            messagebox.showinfo("Aviso", "Adicione pelo menos uma transformação à lista.")
            return

        matriz = compor([m for _, m in self.fila])
        self.desenhar(pontos, transformar(pontos, matriz))

    def desenhar(self, originais, transformados):
        ax = self.ax
        ax.clear()
        ax.axhline(0, color="gray", linewidth=0.8)
        ax.axvline(0, color="gray", linewidth=0.8)

        for pontos, cor, nome in ((originais, "tab:blue", "Original"),
                                  (transformados, "tab:red", "Transformada")):
            if pontos:
                fechado = pontos + [pontos[0]]
                ax.plot([p[0] for p in fechado], [p[1] for p in fechado],
                        marker="o", color=cor, label=nome)

        ax.set_aspect("equal", adjustable="datalim")
        ax.grid(True, alpha=0.3)
        ax.legend()
        self.canvas.draw()


def main():
    janela = tk.Tk()
    App(janela)
    janela.mainloop()


if __name__ == "__main__":
    main()
