import tkinter as tk
import sys
from tkinter import filedialog, messagebox


class HashiGameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hashiwokakero - Interfaz")

        # Variables del juego
        self.grid_size = 0
        self.board = []
        self.initial_board = []
        self.cell_size = 60
        self.selected_island = None
        self.connections = {}
        self.connections_count = {}
        self.connections_drawn = {}
        self.bridges_coords = []

        # Sección de botones
        self.frame_buttons = tk.Frame(root)
        self.frame_buttons.pack(pady=10)

        tk.Button(self.frame_buttons, text="Cargar tablero", command=self.load_board).pack(side="left", padx=10)
        tk.Button(self.frame_buttons, text="Jugador Humano", command=self.activate_human_player).pack(side="left", padx=10)
        tk.Button(self.frame_buttons, text="Jugador Sintético", command=self.connect_ai_player).pack(side="left", padx=10)

        # Canvas
        self.canvas = tk.Canvas(root, bg="white", width=600, height=600)
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.on_click)

    def load_board(self, file_path=None):
        # Carga el tablero desde un archivo de texto
        if file_path:
            path = file_path
        else:
            # Si no se pasa archivo, abre el diálogo normalmente
            path = filedialog.askopenfilename(
                title="Selecciona el archivo del tablero",
                filetypes=[("Archivos de texto", "*.txt")]
            )
            if not path:
                return

        try:
            with open(path, "r") as f:
                lines = f.read().strip().splitlines()

            n_rows, n_cols = map(int, lines[0].split(","))
            self.grid_size = n_rows
            self.board = [list(map(int, list(line.strip()))) for line in lines[1:]]
            self.initial_board = [row[:] for row in self.board]

            # Limpia estructuras de estado
            self.connections.clear()
            self.connections_count.clear()
            self.connections_drawn.clear()
            self.bridges_coords.clear()

            # Inicializa contadores de puentes usados
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if self.board[i][j] > 0:
                        self.connections_count[(i, j)] = 0

            self.draw_board()
            messagebox.showinfo("Éxito", f"Tablero '{path}' cargado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el tablero: {e}")

    def draw_board(self):
        #Tablero
        self.canvas.delete("all")
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x = j * self.cell_size + 30
                y = i * self.cell_size + 30
                num = self.initial_board[i][j]
                if num > 0:
                    self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill="SkyBlue1", outline="black")
                    self.canvas.create_text(x, y, text=str(num), font=("Arial", 14, "bold"))
                else:
                    self.canvas.create_rectangle(x - 25, y - 25, x + 25, y + 25, outline="#ddd")

    def activate_human_player(self):
        #Modo humano
        messagebox.showinfo("Modo Humano", "Haz clic en dos islas para conectar un puente (máx. 2).")
        self.selected_island = None

    def connect_ai_player(self):
        #Modo sintético
        messagebox.showinfo("Jugador Sintético", "Conexión establecida (aún no implementado).")

    def on_click(self, event):
        # click modo humano
        if not self.board:
            return

        i = event.y // self.cell_size
        j = event.x // self.cell_size
        if i >= self.grid_size or j >= self.grid_size:
            return

        if self.board[i][j] > 0:
            x = j * self.cell_size + 30
            y = i * self.cell_size + 30

            if not self.selected_island:
                # Selecciona la primera isla
                self.selected_island = (i, j, x, y)
                self.canvas.create_oval(x - 25, y - 25, x + 25, y + 25, outline="red", width=2)
            else:
                i1, j1, x1, y1 = self.selected_island
                i2, j2 = i, j

                # Validaciones
                if i1 == i2 and j1 == j2:
                    self.selected_island = None
                    return

                if i1 != i2 and j1 != j2:
                    messagebox.showwarning("Inválido", "No se permiten conexiones diagonales.")
                    self.selected_island = None
                    return

                # Verifica ruta libre (islas intermedias y cruces)
                if not self.path_clear(i1, j1, i2, j2):
                    messagebox.showwarning("Inválido", "Hay otra isla o puente en el camino.")
                    self.selected_island = None
                    return

                key = tuple(sorted([(i1, j1), (i2, j2)]))
                current_count = self.connections.get(key, 0)

                # Verifica capacidad de las islas (no permitir exceder el número inicial)
                if self.connections_count.get((i1, j1), 0) >= self.initial_board[i1][j1]:
                    messagebox.showwarning("Inválido", "La primera isla ya alcanzó su límite de puentes.")
                    self.selected_island = None
                    return
                if self.connections_count.get((i2, j2), 0) >= self.initial_board[i2][j2]:
                    messagebox.showwarning("Inválido", "La segunda isla ya alcanzó su límite de puentes.")
                    self.selected_island = None
                    return

                # Verifica máximo 2 puentes entre las mismas islas
                if current_count >= 2:
                    messagebox.showwarning("Inválido", "Ya hay 2 puentes entre estas islas.")
                    self.selected_island = None
                    return

                # Si ya había líneas dibujadas para este par, las eliminamos antes de redibujar
                if key in self.connections_drawn:
                    for line_id in self.connections_drawn[key]:
                        self.canvas.delete(line_id)

                offset = 5
                drawn_ids = []

                # Dibuja según orientación y conteo previo
                if i1 == i2:
                    if current_count == 0:
                        line = self.canvas.create_line(x1, y1, x, y, width=4, fill="gray")
                        drawn_ids = [line]
                    elif current_count == 1:
                        # Segundo puente: dos líneas paralelas
                        line1 = self.canvas.create_line(x1, y1 - offset, x, y - offset, width=4, fill="gray")
                        line2 = self.canvas.create_line(x1, y1 + offset, x, y + offset, width=4, fill="gray")
                        drawn_ids = [line1, line2]

                elif j1 == j2:
                    if current_count == 0:
                        line = self.canvas.create_line(x1, y1, x, y, width=4, fill="gray")
                        drawn_ids = [line]
                    elif current_count == 1:
                        line1 = self.canvas.create_line(x1 - offset, y1, x - offset, y, width=4, fill="gray")
                        line2 = self.canvas.create_line(x1 + offset, y1, x + offset, y, width=4, fill="gray")
                        drawn_ids = [line1, line2]

                self.connections_drawn[key] = drawn_ids

                # Actualización del contador lógico
                self.connections[key] = current_count + 1
                self.connections_count[(i1, j1)] += 1
                self.connections_count[(i2, j2)] += 1

                # Guarda la posición lógica del puente para evitar cruces
                if i1 == i2:
                    c1, c2 = sorted([j1, j2])
                    self.bridges_coords.append(("H", i1, c1, c2))
                elif j1 == j2:
                    r1, r2 = sorted([i1, i2])
                    self.bridges_coords.append(("V", j1, r1, r2))

                # Si la isla completa sus puentes se pone en verde
                if self.connections_count[(i1, j1)] == self.initial_board[i1][j1]:
                    self.mark_completed(i1, j1)
                if self.connections_count[(i2, j2)] == self.initial_board[i2][j2]:
                    self.mark_completed(i2, j2)

                self.selected_island = None

    def path_clear(self, i1, j1, i2, j2):
        # 1) Revisa que no haya islas entre medio
        if i1 == i2:
            step = 1 if j2 > j1 else -1
            for j in range(j1 + step, j2, step):
                if self.board[i1][j] > 0:
                    return False
        elif j1 == j2:
            step = 1 if i2 > i1 else -1
            for i in range(i1 + step, i2, step):
                if self.board[i][j1] > 0:
                    return False

        # 2) Revisa que no se cruce con otros puentes existentes
        if i1 == i2:
            row = i1
            c1, c2 = sorted([j1, j2])
            for (orient, fixed, start, end) in self.bridges_coords:
                if orient == "V":
                    if start < row < end and c1 < fixed < c2:
                        return False
        elif j1 == j2:
            col = j1
            r1, r2 = sorted([i1, i2])
            for (orient, fixed, start, end) in self.bridges_coords:
                if orient == "H":
                    if start < col < end and r1 < fixed < r2:
                        return False

        return True

    def mark_completed(self, i, j):
        #Islas completas resaltadas
        x = j * self.cell_size + 30
        y = i * self.cell_size + 30
        self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill="lightpink", outline="black")
        self.canvas.create_text(x, y, text=":)", font=("Arial", 14, "bold"))


if __name__ == "__main__":
    root = tk.Tk()
    app = HashiGameUI(root)

    # En caso de que el usuario quiera cargar el txt directo
    if len(sys.argv) > 1:
        archivo = sys.argv[1]
        app.load_board(archivo)
    else:
        messagebox.showinfo(
            "Modo manual",
            "No se pasó archivo por parámetro.\nPuedes usar el botón 'Cargar tablero'."
        )

    root.mainloop()
