import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import math

# Liste de noms de lieux pour la ville
VILLE_LIEUX = [
    "Gare", "École", "Hôpital", "Mairie", "Parc", "Musée", "Stade", "Marché", "Université", "Cinéma",
    "Banque", "Supermarché", "Pharmacie", "Boulangerie", "Hôtel", "Piscine", "Théâtre", "Café", "Librairie", "Police"
]

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
        self.title("Comparaison Bellman-Ford vs Dijkstra - Cartographie de Ville")
        self.geometry("1100x750")
        self.edges = []
        self.n = 0
        self.positions = {}
        self.lieux = []
        self.last_path = []
        self.last_distances = None
        self.last_target = None
        self.last_source = None
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(frame, text="Nombre de lieux (sommets) :").pack()
        self.n_entry = ttk.Entry(frame)
        self.n_entry.insert(0, "8")
        self.n_entry.pack()

        ttk.Label(frame, text="Nombre de routes (arêtes) :").pack()
        self.m_entry = ttk.Entry(frame)
        self.m_entry.insert(0, "14")
        self.m_entry.pack()

        ttk.Label(frame, text="Lieu de départ :").pack()
        self.source_entry = ttk.Entry(frame)
        self.source_entry.insert(0, "0")
        self.source_entry.pack()

        ttk.Label(frame, text="Lieu d'arrivée :").pack()
        self.target_entry = ttk.Entry(frame)
        self.target_entry.insert(0, "1")
        self.target_entry.pack()

        self.negative_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Routes à poids négatifs (Bellman-Ford seulement)", variable=self.negative_var).pack()

        ttk.Button(frame, text="Générer la carte", command=self.generate_graph).pack(pady=5)
        ttk.Button(frame, text="Comparer", command=self.compare_algorithms).pack(pady=5)
        self.animate_button = ttk.Button(frame, text="Animer le trajet optimal", command=self.animate_path, state=tk.DISABLED)
        self.animate_button.pack(pady=5)

        self.result_text = tk.Text(frame, height=15, width=40)
        self.result_text.pack(pady=10)

        # Zone de dessin du graphe
        self.canvas = tk.Canvas(self, width=750, height=700, bg="#f5f5dc")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)

    def generate_graph(self):
        try:
            n = int(self.n_entry.get())
            m = int(self.m_entry.get())
            if n > len(VILLE_LIEUX):
                messagebox.showerror("Erreur", f"Maximum {len(VILLE_LIEUX)} lieux supportés.")
                return
            if m < n-1 or m > n*(n-1):
                raise ValueError
        except ValueError:
            messagebox.showerror("Erreur", "Paramètres invalides.")
            return
        self.n = n
        self.lieux = VILLE_LIEUX[:n]
        self.edges = []
        edges = set()
        # Positions aléatoires façon plan de ville
        self.positions = {}
        taken = []
        for i in range(n):
            while True:
                x = random.randint(80, 700)
                y = random.randint(80, 650)
                if all((abs(x-x2) > 60 or abs(y-y2) > 60) for (x2, y2) in taken):
                    self.positions[i] = (x, y)
                    taken.append((x, y))
                    break
        # Générer un arbre couvrant pour assurer la connexité
        nodes = list(range(n))
        random.shuffle(nodes)
        for i in range(1, n):
            u = nodes[i]
            v = nodes[random.randint(0, i-1)]
            weight = random.randint(-10, 20) if self.negative_var.get() else random.randint(1, 20)
            self.edges.append((u, v, weight))
            edges.add((u, v))
        # Ajouter des routes supplémentaires
        while len(self.edges) < m:
            u, v = random.sample(range(n), 2)
            if (u, v) not in edges:
                weight = random.randint(-10, 20) if self.negative_var.get() else random.randint(1, 20)
                self.edges.append((u, v, weight))
                edges.add((u, v))
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Carte de ville générée avec succès !\n")
        self.draw_graph()

    def draw_graph(self, distances=None):
        self.canvas.delete("all")
        n = self.n
        # Dessiner les routes
        for u, v, w in self.edges:
            x1, y1 = self.positions[u]
            x2, y2 = self.positions[v]
            self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, width=3, fill="#888888")
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            self.canvas.create_rectangle(mx-15, my-12, mx+15, my+12, fill="#fff8dc", outline="#888888")
            self.canvas.create_text(mx, my, text=str(w), fill="#003366", font=("Arial", 10, "bold"))
        # Dessiner les lieux
        for i in range(n):
            x, y = self.positions[i]
            color = "#b3e6b3"  # vert clair
            if distances is not None:
                color = "#ffaaaa" if distances[i] == float('inf') else "#aaffaa"
            self.canvas.create_oval(x-28, y-28, x+28, y+28, fill=color, outline="#333333", width=3)
            self.canvas.create_rectangle(x-32, y+30, x+32, y+60, fill="#f5f5dc", outline="#333333")
            label = f"{self.lieux[i]}\n({i})"
            self.canvas.create_text(x, y, text=label, font=("Arial", 11, "bold"), fill="#222222")
            if distances is not None:
                d = distances[i]
                dist_label = f"{d if d != float('inf') else '∞'}"
                self.canvas.create_text(x, y+45, text=f"Dist: {dist_label}", font=("Arial", 10), fill="#003366")
        # Légende
        self.canvas.create_rectangle(10, 10, 220, 70, fill="#fff8dc", outline="#888888")
        self.canvas.create_text(115, 30, text="Lieux = sommets\nRoutes = arêtes\nPoids = distance/temps", font=("Arial", 10))

    def compare_algorithms(self):
        if not self.edges or self.n == 0:
            messagebox.showerror("Erreur", "Veuillez d'abord générer la carte.")
            return
        try:
            source = int(self.source_entry.get())
            if not (0 <= source < self.n):
                raise ValueError
            target = int(self.target_entry.get())
            if not (0 <= target < self.n):
                raise ValueError
        except ValueError:
            messagebox.showerror("Erreur", "Lieu de départ ou d'arrivée invalide.")
            return
        self.result_text.delete(1.0, tk.END)
        # Bellman-Ford
        bf_dist, bf_pred, bf_time, bf_relax = bellman_ford(self.edges, self.n, source)
        if bf_dist is None:
            self.result_text.insert(tk.END, "Cycle négatif détecté par Bellman-Ford !\n")
            self.last_path = []
            self.animate_button.config(state=tk.DISABLED)
        else:
            self.result_text.insert(tk.END, f"Bellman-Ford :\nTemps : {bf_time:.6f} s\nRelaxations : {bf_relax}\nDistances : {bf_dist}\n\n")
            # Récupérer le chemin
            path = self.get_path(bf_pred, source, target)
            self.last_path = path
            self.last_distances = bf_dist
            self.last_source = source
            self.last_target = target
            if path and bf_dist[target] != float('inf'):
                self.animate_button.config(state=tk.NORMAL)
            else:
                self.animate_button.config(state=tk.DISABLED)
        # Dijkstra
        if self.negative_var.get():
            self.result_text.insert(tk.END, "Dijkstra ne supporte pas les poids négatifs.\n")
        else:
            dj_dist, dj_pred, dj_time, dj_relax = dijkstra(self.edges, self.n, source)
            self.result_text.insert(tk.END, f"Dijkstra :\nTemps : {dj_time:.6f} s\nRelaxations : {dj_relax}\nDistances : {dj_dist}\n")
        # Affichage graphique des distances Bellman-Ford
        if bf_dist:
            self.draw_graph(distances=bf_dist)

    def get_path(self, pred, source, target):
        path = []
        cur = target
        while cur is not None and cur != source:
            path.append(cur)
            cur = pred[cur]
        if cur == source:
            path.append(source)
            path.reverse()
            return path
        return []

    def animate_path(self):
        if not self.last_path or not self.last_distances or self.last_target is None:
            return
        self.draw_graph(distances=self.last_distances)
        path = self.last_path
        for i in range(len(path)-1):
            self.after(i*700, lambda i=i: self.highlight_edge(path[i], path[i+1]))
            self.after(i*700, lambda i=i: self.highlight_node(path[i]))
        self.after((len(path)-1)*700, lambda: self.highlight_node(path[-1]))

    def highlight_edge(self, u, v):
        x1, y1 = self.positions[u]
        x2, y2 = self.positions[v]
        self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, width=6, fill="#ff6600", tags="anim")

    def highlight_node(self, node):
        x, y = self.positions[node]
        self.canvas.create_oval(x-28, y-28, x+28, y+28, fill="#ffff00", outline="#ff6600", width=5, tags="anim")
        label = f"{self.lieux[node]}\n({node})"
        if self.last_distances:
            d = self.last_distances[node]
            label += f"\n{d if d != float('inf') else '∞'}"
        self.canvas.create_text(x, y, text=label, font=("Arial", 11, "bold"), tags="anim")

if __name__ == "__main__":
    app = App()
    app.mainloop() 