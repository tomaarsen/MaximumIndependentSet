
# Note that normally I would use
#from typing import Callable, Set
# But the import is more time-consuming than the algorithm in most cases
# so I chose to disable it, and replace the typing in function definitions
# by their quote-wrapped variant.

def memoize(f: "Callable[['Graph', Set['Vertex']], int]") -> "Callable[['Graph', Set['Vertex']], int]":
    """
    Decorator for Graph._hash_b(). 
    
    :param f: Decorated function
    :type f: Callable[['Graph', Set['Vertex']], int]
    
    :returns: Wrapper function
    """
    cache={}

    def wrapped(self, vertices: "Set['Vertex']") -> int:
        """
        Wrapper function for Graph._hash_b().
        Will cache results of the decorated function, 
        and only compute the value using the function 
        if the result has not yet been cached.
        
        :param vertices: Set of Vertex instances.
        :type vertices: Set['Vertex']
        
        :returns: Returns cached value calculated using `vertices`
                  if one exists. Otherwise calculates value
                  using Graph._hash_b().
        :rtype: int
        """
        frozen_vert = frozenset(vertices)
        if frozen_vert in cache:
            return cache[frozen_vert]
        else:
            result = f(self, vertices)
            cache[frozen_vert] = result
            return result
    return wrapped

class Graph(object):
    """
    Graph houses a set of vertices, as well as information 
    regarding the number of nodes, edges and bins.
    It's a data structure used in an algorithm to decide 
    whether the number of bins can be placed on the graph,
    without two bins ever being placed adjacent to each other.
    
    __slots__ reserves space for the declared attributes 
    and prevents the automatic creation of __dict__ and 
    __weakref__ for each instance.
    Using it may speed up accesses of these attributes.
    """
    __slots__ = ['vertices', 'n', 'm', 'b', 'cur']

    def __init__(self, *args, **kwargs) -> None:
        """
        Construct a Graph instance.

        vertices: Set of Vertex instances in the graph.
        n       : Integer, number of nodes in the graph.
        m       : Integer, number of nodes in the graph.
        b       : Integer, number of bins to be placed in the graph.
        cur     : Integer, current number of bins placed.
        """
        super().__init__(*args, **kwargs)
        self.vertices = {}
        self.n = None
        self.m = None
        self.b = None
        self.cur = 0

    def parse_input(self) -> None:
        """
        Parse STDIN input in the form of
            8 7 4
            1 2
            1 4
            2 3
            2 5
            4 5
            5 6
            5 7
            6 7
        For the first row, the values "8 7 4" correspond 
        to n, m and b respectively.

        For the subsequent rows, the two values correspond
        to an edge between the nodes identified by the two
        integers.
        """
        # Get number of streets, intersections and bins (respectively)
        n, m, b = input().split()

        # Convert to integer and store as class attributes
        self.n = int(n)
        self.m = int(m)
        self.b = int(b)

        # Get list of Vertices (Intersections), identified by an id
        vertices = [Vertex(i) for i in range(self.m)]

        for _ in range(self.n):
            # Get input on edges (streets)
            i, j = input().split()
            # Turn to integer and adjust from 1..m to 0..m-1
            i = int(i) - 1
            j = int(j) - 1
            # Add Edges
            vertices[i].add_edge(vertices[j])
            vertices[j].add_edge(vertices[i])

        # Convert to set and store as class attributes
        self.vertices = set(vertices)

    def hash_b(self) -> str:
        """
        :returns: Returns "possible" if the number of bins that can be placed on the graph
        is larger or equal to the amount of bins to be placed on the graph, 
        and return "impossible" otherwise.
        Uses inner function Graph._hash_b() to calculate the number of bins that can be placed
        :rtype: str
        """
        return "possible" if self._hash_b(self.vertices.copy()) >= self.b else "impossible"

    @memoize
    def _hash_b(self, vertices: "Set['Vertex']") -> int:
        """
        hash_b or #B refers to the maximum number of bins that can be placed within `vertices`
        while satisfying the non-adjacency condition.

        :returns: Returns number of bins that can be placed in `vertices` while satisfying
        the non-adjacency constraint.
        :rtype: int
        
        :param vertices: Set of Vertex instances.
        :type vertices: Set['Vertex'] 

        (1)
        When the set of vertices is empty, then the number of bins that can be placed
        on these vertices is 0, as there are no vertices to place bins on.

        When the set of vertices contains one Vertex, then we can always place a bin on 
        that Vertex. So, the number of bins we can place is always 1 in this case.

        For both of these cases, when the length of the set of vertices is less than
        or equal to 1, we can simply return the length of the set of vertices.
        """
        if len(vertices) <= 1:
            return len(vertices)
        """
        (2)
        We pop a single vertex from our set. We know this is always possible as we have
        removed all cases where the set is empty in the previous step.
        We end up with an arbitrary Vertex from the set, `picked`, and this element
        is removed from vertices.
        """
        picked = vertices.pop()
        
        """
        In order to calculate the number that can be placed, with some arbitrarily 
        chosen Vertex (called `picked`), we will consider two cases.

        Case 1:
            `picked` gets a bin, and hence its neighbours cannot.
        
        Case 2:
            `picked` does not get a bin, and hence it neighbours can.
        
        We will test these two cases, and return the largest between the two cases.
        We start with the first case, as it will generally recurse with a smaller set than
        the second case, and hence reach one of the base cases faster than the second case.

        (3)
        Here we perform case 1. We give the `picked` Vertex a bin, and have to recurse using all 
        other vertices that may also receive a bin. As only vertices not adjacent to `picked` 
        can still be picked, we recurse with `vertices - picked.neighbours`.

        Note that we also increment self.cur by 1, to update the bins placed excluding
        the #B calculated with `vertices - picked.neighbours`.
        We will decrement this value again after the recursion, so that self.cur is always the
        number of bins placed, excluding the current vertices.
        """
        self.cur += 1
        first = 1 + self._hash_b(vertices - picked.neighbours)
        """
        Simply going with double recursion to get to the highest number of bins is quite
        inefficient. Luckily, we can ignore some cases, improving efficiency greatly.
        
        (4)
        If the #B from before the current set of vertices (self.cur) and the #B from the  
        current set of vertices, with `picked` fixed to have a bin (first) is greater than
        the amount of bins to be placed, then we have found a case where we can
        place all the bins. In this case we can return `first` and stop recursing.
        """
        if first + self.cur > self.b:
            return first
        self.cur -= 1
        """
        (5)
        There are some cases where we know the second case cannot result in more bins placed.
        The largest value the second case can return is equivalent to the size of the set
        of vertices, when all vertices are nonadjacent. So, if the result of the first
        case is already equal to or larger than the size of the set of remaining vertices, 
        then there is no way for the second case to get a higher value.
        Hence, we can discard all cases where `first >= len(vertices)`.
        
        (6)
        If there is no overlap between the `picked` their neighbours and `vertices`, then
        giving `picked` a bin like done in the first case places no further restrictions
        on the rest of the vertices. Hence, in this case the first case will always return
        a value exactly 1 higher than the second case.
        
        If there is overlap between the `picked` their neighbours and `vertices` of exactly 
        one Vertex, then the second case has an upper bound of `first`, as 
        `self._hash_b(vertices) == self._hash_b(vertices - picked.neighbours)` or 
        `self._hash_b(vertices) == self._hash_b(vertices - picked.neighbours) + 1`.
        Because the first case adds a 1, the second case either results a value one lower 
        than `first`, or `first` itself. 

        Because we only care about the second case if its result is larger than `first`,
        we can discard these cases. Hence we can discard all cases where 
        `len(picked.neighbours.intersection(vertices)) <= 1`.
        """
        if first >= len(vertices) or len(picked.neighbours.intersection(vertices)) <= 1:
            return first
        """
        (7)
        Finally, after pruning a lot of unnecessary cases, we can actually compute the 
        second case. Because for the second case we decide that `picked` will not get a 
        bin, all neighbours of it are still allowed to get a bin. Hence, we can recurse 
        simply with `vertices`. Note that `picked` is no longer in `vertices`.

        (8)
        Then, we simply return the max between the result from the first case and
        the result from the second case.
        """
        return max(first, self._hash_b(vertices))

class Vertex(object):
    """
    Vertex houses information about a single Vertex
    in a Graph.
    
    __slots__ reserves space for the declared attributes 
    and prevents the automatic creation of __dict__ and 
    __weakref__ for each instance.
    Using it may speed up accesses of these attributes.
    """
    __slots__ = ["vid", "neighbours"]

    def __init__(self, vid: int, *args, **kwargs) -> None:
        """
        Construct a Vertex instance.

        :param vid: Integer identifying this Vertex: Vertex IDentification.
        :type vid: int

        vid       : Integer identifying this Vertex.
        neighbours: Set of vertices adjacent to this Vertex.
        """
        super().__init__(*args, **kwargs)
        self.vid = vid
        self.neighbours = set()

    def add_edge(self, edge: "Vertex") -> None:
        """
        Add an edge between this Vertex and `edge` by
        adding `edge` to the `neighbours` set.

        :param edge: Vertex adjacent to the this Vertex.
        :type edge: Vertex
        """
        self.neighbours.add(edge)

    def __hash__(self) -> int:
        """
        The implementation of this function overrides the standard implementation
        which attempts to hash the attributes of the instance. Returning this Vertex's 
        identification allows this class (instance) to be hashed more efficiently, 
        without losing usefulness.

        Without overriding this standard implementation, 

        :returns: This Vertex's identification: self.id
        :rtype: int
        """
        return self.vid

if __name__ == "__main__":
    g = Graph()
    g.parse_input()
    print(g.hash_b())