"""
Drawing Module

This module provides a class, Drawing, for generating diagrams with nodes and relationships
  using the Graphviz engine. It simplifies the process of creating graphical representations
  of objects, their hierarchy, and relationships.

Class:
- `Drawing`: Manages the creation and rendering of diagrams.

Methods:
- `add_item(node_id, node=None, cluster=None, point=None)`:
      Add an item to the diagram with the specified attributes.
- `add_parent(node_id, parent)`: Add a parent-child relationship between items.
- `add_list(node_id, lst)`: Represent a list of items associated with an object in the diagram.
- `add_link(node_id, link, label="")`: Add a link between two items with an optional label.

Usage:
- ...

Author: Pavel ERESKO
"""


from graphviz import Digraph

class Drawing:
    ''' Class that provide drawing structure of nodes with parent, list, and links relations '''
    def __init__(self):
        self.items   = {}
        self.parents = {}
        self.lists   = {}
        self.links   = []

        self.linked = None

    def item_view(self,
        label = "[Item]", shape = "plaintext", style = 'filled', fillcolor = None, width = 0.1
    ):
        ''' Parameter passing function '''
        return {
            "label": label, "shape": shape, "style": style, "fillcolor": fillcolor, "width": width,
        }

    def add_item(self, node_id, node = None, cluster = None, point = None):
        ''' Add node with html representation '''
        if not node_id in self.items:
            self.items[node_id] = {}

        for name, par in {"node" : node, "cluster" : cluster, "point" : point}.items():
            if par is None:
                continue

            labeldict = par
            if name == "node" and isinstance(par, str):
                labeldict = self.item_view(par)

            self.items[node_id][name] = labeldict

    def add_parent(self, node_id, parent):
        ''' Add parent relation '''
        self.parents[node_id] = parent

    def add_list(self, node_id, node_list):
        ''' Add list relation '''
        self.lists[node_id] = node_list

    def add_link(self, node_id, link, label = ""):
        ''' Add link relation '''
        self.links.append((node_id, link, label))

    def print(self):
        ''' Print nodes and relations added '''
        print("\nDrawing")

        print("\tItems  :")
        for i, data in self.items  .items():
            print(i, end=' ')
        print()

        print("\tParents:")
        for i, data in self.parents.items():
            print(f"{i} -> {data}")

        print("\tLists  :")
        for i, data in self.lists  .items():
            print(i)

        print("\tLinks  :")
        for node_id, link, label in self.links:
            print(f"{node_id} --[{label}]--> {link}")

    def draw_rec(self, parent, grand_digraph):
        ''' Recursively draws the nodes '''
        items = [node_id for node_id in self.items if not node_id in
                    [chi for chi, par in self.parents.items() if par in self.items]
                ] if parent is None \
                  else [node_id for node_id, par in self.parents.items() if par == parent]

        if len(items) == 0:
            view = self.items[parent]["node"]
            grand_digraph.node(name=parent, shape=view["shape"], label = view["label"])

        else:
            par_context = None
            par_digraph = None if parent is not None else grand_digraph

            for node_id in items:
                if par_digraph is None:
                    par_context = grand_digraph.subgraph(name = "cluster_" + parent)
                    par_digraph = par_context.__enter__()

                    view = self.items[parent]["cluster"]

                    # label = f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
                    #             {view["label"]}
                    #             </TABLE>>'''
                    label = view["label"]
                    # print(label.replace("\n", ""))

                    par_digraph.attr(
                        label = label,
                        style = view["style"],
                        fillcolor = view["fillcolor"]
                    )

                    if parent in self.linked:
                        view = self.items[parent]["point"]
                        par_digraph.node(name=parent, shape=view["shape"], width=view["width"])

                self.draw_rec(node_id, par_digraph)

            if par_context is not None:
                par_context.__exit__(None, None, None)


    def draw(self, name):
        ''' Draws the structure of nodes with all the relations '''
        dot = Digraph(name)

        self.linked = {}
        for node_id, link, label in self.links:
            self.linked[node_id] = True
            self.linked[link] = True
            dot.edge(node_id, link, label = label)

        if len(self.items) > 0:
            self.draw_rec(None, dot)

        self.linked = None


        with open('Y3A\\render\\Y3A.txt', 'w') as file:
            file.write(dot.source)


        try:
            # dot.render(name, format='png', cleanup=True)
            # dot.render(name, format='svg', cleanup=True)

            #pixmap = QPixmap("Drawing.png")
            #pixmap_item = QGraphicsPixmapItem(pixmap)
            #Graph.scene().addItem(pixmap_item)
            #Graph.fitInView(Graph.scene().sceneRect()) # Autoscaling

            svg_str = dot.pipe(format='svg').decode('utf-8')
        except Exception as e:
            print(f"Draw error: {str(e)}")
            return ""

        svg_str = '\n'.join(svg_str.split('\n')[3:])

        return svg_str
