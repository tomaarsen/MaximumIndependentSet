
def memoize(f: "Callable[['Graph', Set['Vertex']], int]") -> "Callable[['Graph', Set['Vertex']], int]":
    cache={}

    def wrapped(self, vertices: "Set['Vertex']") -> int:
        frozen_vert = frozenset(vertices)
        if frozen_vert in cache:
            return cache[frozen_vert]
        else:
            result = f(self, vertices)
            cache[frozen_vert] = result
            return result
    return wrapped

class Graph(object):
    __slots__ = ['vertices', 'n', 'm', 'b', 'cur']

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.vertices = {}
        self.n = None
        self.m = None
        self.b = None
        self.cur = 0

    def parse_input(self) -> None:
        n, m, b = input().split()
        self.n = int(n)
        self.m = int(m)
        self.b = int(b)

        vertices = [Vertex(i) for i in range(self.m)]

        for _ in range(self.n):
            i, j = input().split()
            i = int(i) - 1
            j = int(j) - 1
            vertices[i].add_edge(vertices[j])
            vertices[j].add_edge(vertices[i])

        self.vertices = set(vertices)

    def hash_b(self) -> str:
        return "possible" if self._hash_b(self.vertices) >= self.b else "impossible"

    @memoize
    def _hash_b(self, vertices: "Set['Vertex']") -> int:
        if len(vertices) <= 1:
            return len(vertices)
        picked = vertices.pop()
        self.cur += 1
        first = 1 + self._hash_b(vertices - picked.neighbours)
        if first + self.cur > self.b:
            return first
        self.cur -= 1
        if len(picked.neighbours.intersection(vertices)) <= 1 or first >= len(vertices):
            return first
        return max(first, self._hash_b(vertices))

class Vertex(object):
    __slots__ = ["vid", "neighbours"]

    def __init__(self, vid: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.vid = vid
        self.neighbours = set()

    def add_edge(self, edge: "Vertex") -> None:
        self.neighbours.add(edge)

    def __hash__(self) -> int:
        return self.vid

if __name__ == "__main__":
    g = Graph()
    g.parse_input()
    print(g.hash_b())