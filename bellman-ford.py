def bellman_ford(graph, start):
    distance = {node: float('inf') for node in graph}
    distance[start] = 0

    for _ in range(len(graph) - 1):
        for u in graph:
            for v, weight in graph[u]:
                if distance[u] + weight < distance[v]:
                    distance[v] = distance[u] + weight

    # Vérification des cycles négatifs
    for u in graph:
        for v, weight in graph[u]:
            if distance[u] + weight < distance[v]:
                raise ValueError("Le graphe contient un cycle de poids négatif")

    return distance

# Exemple d'utilisation
graph = {
    'A': [('B', 4), ('C', 2)],
    'B': [('C', -3), ('D', 2)],
    'C': [('D', 3)],
    'D': [('B', 1)]
}

print(bellman_ford(graph, 'A'))
