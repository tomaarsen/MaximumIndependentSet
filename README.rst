Maximum Independent Set
=======================

This repository holds a solution to a problem, which can be
reconstructed as a maximum independent set problem, which I was tasked
to solve. Two versions of the code are provided - one with comments, and
one without. The remainder of this README is a section of the report I
wrote for this problem and my corresponding solution. Note that the
initial report was written in LaTeX and now converted to Markdown so
Github can display it. This means that e.g. line numbers will not make
as much sense.

--------------

Problem
-------

I was tasked with solving a specific algorithmic problem, inspired by a
real life scenario. The problem was introduced as follows:

    The municipal administration of Nijmegen wants to keep the city
    clean and neat. In order to do this, they want to place garbage bins
    on as many street intersections as possible. This means the garbage
    collectors have to make more stops on their daily routes, something
    they are not happy about. After discussion between the city and the
    garbage collectors a compromise has been reached: the city will
    place as many garbage bins as possible, but if two intersections are
    adjacent to each other at most one of them will have a garbage bin.
    They have asked [sic] if it is possible to place all the bins in the
    city.

The constraint specifying that two adjacent intersections may not both
have a garbage bin will be referred to as the non-adjacency constraint
from now on.

Input
~~~~~

Input to the program is given via **stdin**, in the following format:

::

    8 7 4
    1 2
    1 4
    2 3
    2 5
    4 5
    5 6
    5 7
    6 7

The first line contains integers :math:`n\ (1 \leq n \leq 200)`,
:math:`m\ (1 \leq m \leq 100)` and :math:`b\ (1 \leq b \leq 20)`. These
values correspond to the number of streets, intersections and bins to be
placed respectively. All subsequent lines correspond to a street that
exists between the intersections identified by the given integers.

Output
~~~~~~

Output should be given via **stdout**. The program should either output
``possible`` or ``impossible``, depending on whether it's possible for
:math:`b` bins to be placed on the :math:`m` intersections, without
breaking the condition stating that two bins may never be placed on
adjacent intersections.

Problem Transformation
----------------------

In order to start looking for solutions to this problem, we must first
consider potential data structures to represent the given information.
%Several representations exist, each with their own up- and downsides.

Maximum number of bins
~~~~~~~~~~~~~~~~~~~~~~

If we consider: :math:`G = (V, E)`, with :math:`V` as the set of
intersections and :math:`E` as the set of streets connecting these
intersections, :math:`\#b(G)` as the number of bins that can be placed
on graph G without breaking the non-adjacency constraint, :math:`Adj[v]`
as the set of neighbours of some vertex v, then the following must hold:

.. math::


   \#b((V, E)) = 
   \begin{cases}
   \quad \text{iff a bin is placed on arbitrary vertex }p\text{:}\\
   1 + \#b((V - p - Adj[p], E- \{(x, y) | x \in E \land y \in E \land x \in \{p\} \cup Adj[p] \land y \in \{p\} \cup Adj[p]\}))\\
   \quad \text{iff no bin is placed on arbitrary vertex }p\text{:}\\
   \#b((V - p, E - \{(p, y) | y \in E\} - \{(x, p) | x \in E\}))\\
   \quad \text{iff no arbitrary vertex }p\text{ exists:}\\
   0
   \end{cases}

 In words, the number of bins that can be placed on the graph without
breaking the non-adjacency constraint is either: \* the number of bins
that can be placed on the subgraph excluding arbitrary vertex :math:`p`
and its neighbours, plus one, **iff** we choose :math:`p` to have a bin.
We can plus one because we have given :math:`p` a bin in this case. \*
the number of bins that can be placed on the subgraph excluding
arbitrary vertex :math:`p`, **iff** we choose :math:`p` to not have a
bin. We simply reduce the set we recurse with in this case. \* zero, if
there are no vertices.

At this point it becomes apparent that working with the
:math:`G = (V, E)` representation is going to be unnecessarily
inefficient in an algorithm, as we would have to update :math:`E` for
all recursive calls. However, this is not needed. We know that the only
use for E in the previous equation is in :math:`Adj[v]`, to find the set
of adjacent vertices for some vertex :math:`v`. If we consider :math:`U`
to be a set of vertices that only existed in a supergraph of :math:`V`,
then the following holds:

.. math:: \forall p:V, V - Adj[p] = V - (Adj[p] \cup \{u | u \in U \land u \notin V\})

 So, if we keep the vertices that should no longer be considered within
E, then :math:`Adj[p]` may return more vertices, but as none of these
vertices are in :math:`V`, there is no difference between reducing E and
not doing so. This saves us a step. So, we can use a set representation,
where :math:`G = \{v_0, v_1, ..., v_m\}`, and
:math:`\forall v:G, Adj[v]` is defined to be the set of adjacent
vertices for the initial graph. This allows us to simplify
:math:`\#b(G)` greatly:

.. math::


   \#b(G) = 
   \begin{cases}
   \quad \text{iff a bin is placed on arbitrary vertex }p\text{:}\\
   1 + \#b(G - p - Adj[p])\\
   \quad \text{iff no bin is placed on arbitrary vertex }p\text{:}\\
   \#b(G - p)\\
   \quad \text{iff no arbitrary vertex }p\text{ exists:}\\
   0
   \end{cases}

Because we want to maximize :math:`\#b(G)`, we can compare the results
from both options to decide whether we want to place a bin on :math:`p`.
We can simply choose the higher value of the two:

.. math::


   \#b(G) = 
   \begin{cases}
   \quad \text{iff arbitrary vertex }p\text{ exists:}\\
   max(1 + \#b(G - p - Adj[p]), \#b(G - p))\\
   \quad \text{iff no arbitrary vertex }p\text{ exists:}\\
   0
   \end{cases}

 At this point the concept has been reduced such that only few set
difference operations are required, however it is still quite
inefficient as it uses multiple recursion. The worst case scenario for
this equation would be :math:`m` vertices, without any edges. So,
:math:`\forall v:G, Adj[v] = \emptyset`, which means the parameter for
both recursive calls is :math:`G - p`, and hence the equation would have
:math:`O(2^m)` time complexity.

Some of these cases may be discarded, and we can use strategies to
improve the running time of this concept. I will go over my optimization
steps in the following section.

Optimization
------------

In this section I will start with the following code sample, which was
shown to be correct in the previous section. Over the course of this
section I will improve this code sample by pruning some cases.

.. code:: python

    >   def hash_b(self, vertices: "Set['Vertex']") -> int:
    >       if len(vertices) == 0:
    >           return 0
    >       picked = vertices.pop()
    >       return max(1 + self.hash_b(vertices - picked.neighbours), 
    >                  self.hash_b(vertices))

The recursive call in the first parameter of the ``max`` function will
be referred to as the first case, and the second recursive call will be
referred to as the second case from now on.

Base Case pruning
~~~~~~~~~~~~~~~~~

We can extend our base case ``if len(vertices) == 0: return 0`` by the
case where vertices contains just one vertex. In this case, we can
always place a bin on this vertex, and never recurse further. Hence, if
``len(vertices) == 1``, then we should return 1. We can combine this
with the existing base case to:

.. code:: python

        def hash_b(self, vertices: "Set['Vertex']") -> int:
    >       if len(vertices) <= 1:
    >           return len(vertices)
            picked = vertices.pop()
            return max(1 + self.hash_b(vertices - picked.neighbours), 
                       self.hash_b(vertices))

Early Termination
~~~~~~~~~~~~~~~~~

The algorithm will go through all recursive cases, even if we would
already be able to conclusively say that placing :math:`b` bins is
possible halfway through. We want to avoid this, and stop immediately
when we know we can place :math:`b` bins. We can do this by incrementing
a class attribute ``self.cur`` before recursing via the first case, and
decrementing afterwards. This way, this ``self.cur`` attribute will
always be the value that gets added to the result of the current
``hash_b`` call, to get the final amount of bins that can be placed.
Using this ``self.cur``, we can at any point calculate the return value
of the initial call to ``hash_b``, and find out if we can stop all
recursion right now. If the value resulting from the first case plus
this ``self.cur`` is larger than the amount of bins to be placed, then
we can stop all recursions and return:

.. code:: python

        def hash_b(self, vertices: "Set['Vertex']") -> int:
            if len(vertices) <= 1:
                return len(vertices)
            picked = vertices.pop()
    >       self.cur += 1
    >       first = 1 + self.hash_b(vertices - picked.neighbours)
    >       if first + self.cur > self.b:
    >           return first
    >       self.cur -= 1
    >       return max(first, self.hash_b(vertices))

Note that only the first case can increment the result, so this method
of pruning only works for this case, and not the second.

Halfway Pruning
~~~~~~~~~~~~~~~

Not always do we need to calculate the second case. We only care about
this case when its result may be larger than ``first``. Hence, all cases
where we can conclusively say that it will not be can be discarded. The
best case scenario for the second case is if all remaining vertices are
nonadjacent. In this case the result will be equal to the length of the
set of vertices. If ``first`` is already larger than or equal to the
length of the set of vertices, then ``max(first, second)`` is equivalent
to ``first``. So, we won't need to calculate the second case anymore.

.. code:: python

        def hash_b(self, vertices: "Set['Vertex']") -> int:
            if len(vertices) <= 1:
                return len(vertices)
            picked = vertices.pop()
            self.cur += 1
            first = 1 + self.hash_b(vertices - picked.neighbours)
            if first + self.cur > self.b:
                return first
            self.cur -= 1
    >       if first >= len(vertices):
    >           return first
            return max(first, self.hash_b(vertices))

Few Neighbour Pruning
~~~~~~~~~~~~~~~~~~~~~

If ``picked`` has no neighbours still in ``vertices``, then the set used
to recurse in the first case will be the same set as the one used in the
second case. The difference is that the first case results in a value
exactly 1 higher than the second case. In this case, we should ignore
the second case. Moreso, if ``picked`` has exactly one neighbour still
in ``vertices``, then the second case recurses with a set exactly one
vertex larger. Hence, the recursive call from the second case can result
in a value 1 higher than the recursive case from the first case.
However, because 1 is added to the recursive call for the first case,
the result from the second case has an upper bound of ``first``. Because
we only care about the maximum of the two values, we can ignore the
second case when ``picked`` has exactly one neighbour still in
``vertices``.

.. code:: python

        def hash_b(self, vertices: "Set['Vertex']") -> int:
            if len(vertices) <= 1:
                return len(vertices)
            picked = vertices.pop()
            self.cur += 1
            first = 1 + self.hash_b(vertices - picked.neighbours)
            if first + self.cur > self.b:
                return first
            self.cur -= 1
    >       if len(picked.neighbours.intersection(vertices)) <= 1 or first >= len(vertices):
    >           return first
            return max(first, self.hash_b(vertices))

Note that this pruning step is triggered more often than the **Halfway
Pruning** pruning method, and hence is placed at the start of the ``or``
in the ``if``-statement.

Memoization
~~~~~~~~~~~

By far the largest optimization technique used is memoization. The input
and output of every call to ``hash_b`` is stored in a cache, and the
output from the cache is returned rather than computing the result using
the function, if possible. This technique is so useful here is because
it's common for ``hash_b`` to be called with the same set of vertices
multiple times.

However, it's not as useful for both cases. For instance, during my
testing using both provided and generated samples, the second case was
responsible for calculating and storing 40.8% of everything that was
cached, but was only responsible for 8.6% of all cache uses. Because of
this, it may be worthwhile to only cache the first case. The second case
could then either be allowed to use the cache but not store values in
the cache, or completely avoid caching altogether.

My testing showed speed improvements near 2-3% for not caching the
second case. This would also allow the algorithm to use a decent amount
less memory. However, the results were not consistent enough for me to
stop caching the second case.

How exactly memoization is implemented is best shown in the program as a
whole.

The #B Algorithm
----------------

.. code:: python

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

In section **3 Optimization** I have already shown why and how the
``hash_b`` function itself works, so here I'll go over some other
implementation choices I've made.

Initialization
~~~~~~~~~~~~~~

On line 74 of the program, we create a Graph object. Some class
attributes are initialized for it:

.. code:: python

    self.vertices = {} # Set of Vertex instances in the graph.
    self.n = None      # Integer, number of nodes in the graph.
    self.m = None      # Integer, number of nodes in the graph.
    self.b = None      # Integer, number of bins to be placed.
    self.cur = 0       # Integer, current number of bins placed.

The ``self.n``, ``self.n`` and ``self.b`` correspond directly to the
:math:`n`, :math:`m` and :math:`b` from the problem. ``self.vertices``
is the set of vertices for the total graph. After it is filled once, it
will no longer be edited. ``self.cur`` will constantly change, as it's
incremented before some recursive calls, and decremented after.

Input Parsing
~~~~~~~~~~~~~

Before the algorithm can start, we need to store the data we receive via
**stdin**. Graph has a ``parse_input()`` method that does exactly that:

.. code:: python

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

For a refresher of what the input looks like, see section **1.2 Input**.
First, (line 26), we extract :math:`n`, :math:`m` and :math:`b` from the
first line of the input. We convert these to integers, and create a list
of :math:`m` vertices, each identified by some integer ranging from
:math:`0` to :math:`m-1`. For now, this vid (vertex id) corresponds to
the index of the ``vertices`` list. For all :math:`n` edges/streets, we
take the integers identifying which vertices/intersections are
connected: :math:`i` and :math:`j`. These values range from :math:`1` to
:math:`m`, so we subtract 1 after converting them to integers, so they
range from :math:`0` to :math:`m-1`, just like our ``vertices`` list. We
add an edge to both of the vertices. Or rather, we add the vertex
identified by :math:`j` to the set of neighbours of the vertex
identified by :math:`i`, and vice versa. Because we would like to use
set operations in the #B algorithm itself, we convert the list of
vertices to a set.

Other Choices
~~~~~~~~~~~~~

Each class uses a ``__slots__`` list. This list reserves space for the
declared attributes and prevents the automatic creation of ``__dict__``
and ``__weakref__`` for each instance. Using it may speed up accesses of
these attributes. Memoization is implemented as a decorator, which means
every call of ``hash_b`` actually calls the ``wrapped`` function inside
of ``memoize``. This way it's easy to enable or disable caching. The
``Vertex`` class has a custom implementation of ``__hash__``. This
overrides the standard implementation, which may try to perform some
more complex calculation to derive a hash. We want this method to be as
light as possible, as in ``memoize``, the set of vertices is converted
to a ``frozenset`` and hashed before being used for the cache. This
hashing of a frozenset will call the ``__hash__`` method of all elements
of the set, and hence also on the ``Vertex`` objects in our case.

--------------

Contributing
~~~~~~~~~~~~

I am not taking contributions for this repository, as it is designed as
an archive.

License
~~~~~~~

This project is licensed under the MIT License - see the LICENSE.md file
for details.


