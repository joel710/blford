import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import math

# --- Algorithmes ---
def bellman_ford(edges, n, source):
    distances = [float('inf')] * n
    distances[source] = 0
    predecessor = [None] * n
    n_relax = 0
    start = time.time()
    for _ in range(n - 1):
        for u, v, w in edges:
            n_relax += 1
            if distances[u] + w < distances[v]:
                distances[v] = distances[u] + w
                predecessor[v] = u
    # Vérification des cycles négatifs
    for u, v, w in edges:
        if distances[u] + w < distances[v]:
            return None, None, None, None  # Cycle négatif détecté
    end = time.time()
    return distances, predecessor, end - start, n_relax

def dijkstra(edges, n, source):
    import heapq
    graph = [[] for _ in range(n)]
    for u, v, w in edges:
        graph[u].append((v, w))
    distances = [float('inf')] * n
    distances[source] = 0
    predecessor = [None] * n
    visited = set()
    heap = [(0, source)]
    n_relax = 0
    start = time.time()
    while heap:
        dist, u = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)
        for v, w in graph[u]:
            n_relax += 1
            if distances[u] + w < distances[v]:
                distances[v] = distances[u] + w
                predecessor[v] = u
                heapq.heappush(heap, (distances[v], v))
    end = time.time()
    return distances, predecessor, end - start, n_relax

# --- Interface graphique ---
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Comparaison Bellman-Ford vs Dijkstra")
        self.geometry("1000x700")
        self.edges = []
        self.n = 0
        self.positions = {}
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(frame, text="Nombre de sommets :").pack()
        self.n_entry = ttk.Entry(frame)
        self.n_entry.insert(0, "6")
        self.n_entry.pack()

        ttk.Label(frame, text="Nombre d'arêtes :").pack()
        self.m_entry = ttk.Entry(frame)
        self.m_entry.insert(0, "10")
        self.m_entry.pack()

        ttk.Label(frame, text="Sommet de départ :").pack()
        self.source_entry = ttk.Entry(frame)
        self.source_entry.insert(0, "0")
        self.source_entry.pack()

        self.negative_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Poids négatifs (Bellman-Ford seulement)", variable=self.negative_var).pack()

        ttk.Button(frame, text="Générer un graphe", command=self.generate_graph).pack(pady=5)
        ttk.Button(frame, text="Comparer", command=self.compare_algorithms).pack(pady=5)

        self.result_text = tk.Text(frame, height=15, width=40)
        self.result_text.pack(pady=10)

        # Zone de dessin du graphe
        self.canvas = tk.Canvas(self, width=600, height=600, bg="white")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)

    def generate_graph(self):
        try:
            n = int(self.n_entry.get())
            m = int(self.m_entry.get())
            if m < n-1 or m > n*(n-1):
                raise ValueError
        except ValueError:
            messagebox.showerror("Erreur", "Paramètres invalides.")
            return
        self.n = n
        self.edges = []
        edges = set()
        # Générer un arbre couvrant pour assurer la connexité
        nodes = list(range(n))
        random.shuffle(nodes)
        for i in range(1, n):
            u = nodes[i]
            v = nodes[random.randint(0, i-1)]
            weight = random.randint(-10, 20) if self.negative_var.get() else random.randint(1, 20)
            self.edges.append((u, v, weight))
            edges.add((u, v))
        # Ajouter des arêtes supplémentaires
        while len(self.edges) < m:
            u, v = random.sample(range(n), 2)
            if (u, v) not in edges:
                weight = random.randint(-10, 20) if self.negative_var.get() else random.randint(1, 20)
                self.edges.append((u, v, weight))
                edges.add((u, v))
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Graphe généré avec succès !\n")
        self.draw_graph()

    def draw_graph(self, distances=None):
        self.canvas.delete("all")
        n = self.n
        r = 250
        cx, cy = 300, 300
        angle_step = 2 * math.pi / n if n > 0 else 0
        self.positions = {}
        for i in range(n):
            angle = i * angle_step
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            self.positions[i] = (x, y)
        # Dessiner les arêtes
        for u, v, w in self.edges:
            x1, y1 = self.positions[u]
            x2, y2 = self.positions[v]
            self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST)
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            self.canvas.create_text(mx, my, text=str(w), fill="blue")
        # Dessiner les sommets
        for i in range(n):
            x, y = self.positions[i]
            color = "lightblue"
            if distances is not None:
                color = "#ffaaaa" if distances[i] == float('inf') else "#aaffaa"
            self.canvas.create_oval(x-25, y-25, x+25, y+25, fill=color, outline="black")
            label = f"{i}"
            if distances is not None:
                d = distances[i]
                label += f"\n{d if d != float('inf') else '∞'}"
            self.canvas.create_text(x, y, text=label, font=("Arial", 12, "bold"))

    def compare_algorithms(self):
        if not self.edges or self.n == 0:
            messagebox.showerror("Erreur", "Veuillez d'abord générer un graphe.")
            return
        try:
            source = int(self.source_entry.get())
            if not (0 <= source < self.n):
                raise ValueError
        except ValueError:
            messagebox.showerror("Erreur", "Sommet de départ invalide.")
            return
        self.result_text.delete(1.0, tk.END)
        # Bellman-Ford
        bf_dist, bf_pred, bf_time, bf_relax = bellman_ford(self.edges, self.n, source)
        if bf_dist is None:
            self.result_text.insert(tk.END, "Cycle négatif détecté par Bellman-Ford !\n")
        else:
            self.result_text.insert(tk.END, f"Bellman-Ford :\nTemps : {bf_time:.6f} s\nRelaxations : {bf_relax}\nDistances : {bf_dist}\n\n")
        # Dijkstra
        if self.negative_var.get():
            self.result_text.insert(tk.END, "Dijkstra ne supporte pas les poids négatifs.\n")
        else:
            dj_dist, dj_pred, dj_time, dj_relax = dijkstra(self.edges, self.n, source)
            self.result_text.insert(tk.END, f"Dijkstra :\nTemps : {dj_time:.6f} s\nRelaxations : {dj_relax}\nDistances : {dj_dist}\n")
        # Affichage graphique des distances Bellman-Ford
        if bf_dist:
            self.draw_graph(distances=bf_dist)

if __name__ == "__main__":
    app = App()
    app.mainloop() 