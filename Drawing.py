from graphviz import Digraph

def ItemView(label = "[Item]", shape = "plaintext", style = 'filled', fillcolor = None, width = 0.1):
    return {
        "label": label,
        "shape": shape,
        "style": style,
        "fillcolor": fillcolor,
        "width": width,
    }

class Drawing:
    def __init__(self):
        self.Items   = {}
        self.Parents = {}
        self.Lists   = {}
        self.Links   = []

    def AddItem(self, id, node = None, cluster = None, point = None):
        if not id in self.Items:
            self.Items[id] = {}

        for name, par in {"node" : node, "cluster" : cluster, "point" : point}.items():
            if par == None: continue

            labeldict = par
            if name == "node" and type(par) == str:
                labeldict = ItemView(par)

            self.Items[id][name] = labeldict

    def AddParent(self, id, parent): self.Parents[id] = parent
    def AddList  (self, id, list  ): self.Lists  [id] = list
    def AddLink  (self, id, link, label = ""): self.Links.append((id, link, label))

    def print(self):
        print("\nDrawing")

        print(f"\tItems  :")
        for i, data in self.Items  .items():
            print(i, end=' ')
        print()

        print(f"\tParents:")
        for i, data in self.Parents.items():
            print(f"{i} -> {data}")

        print(f"\tLists  :")
        for i, data in self.Lists  .items():
            print(i)

        print(f"\tLinks  :")
        for id, link, label in self.Links:
            print(f"{id} --[{label}]--> {link}")

    def DrawRec(self, parent, grandDigraph):
        items = [id for id in self.Items if not id in [chi for chi, par in self.Parents.items() if par in self.Items]] \
            if parent == None \
            else [id for id, par in self.Parents.items() if par == parent]
        
        if len(items) == 0:
            view = self.Items[parent]["node"]
            grandDigraph.node(name=parent, shape=view["shape"], label = view["label"])

        else:
            parContext = None
            parDigraph = None if parent != None else grandDigraph

            for id in items:
                if parDigraph == None:
                    parContext = grandDigraph.subgraph(name = "cluster_" + parent)
                    parDigraph = parContext.__enter__()

                    view = self.Items[parent]["cluster"]
                    # label = f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
                    #             {view["label"]}
                    #             </TABLE>>'''
                    label = view["label"]
                    # print(label.replace("\n", ""))
                    parDigraph.attr(label = label, style = view["style"], fillcolor = view["fillcolor"])

                    if parent in self.Linked:
                        view = self.Items[parent]["point"]
                        parDigraph.node(name=parent, shape=view["shape"], width=view["width"])
                    
                self.DrawRec(id, parDigraph)

            if parContext != None:
                parContext.__exit__(None, None, None)


    def Draw(self, Name):
        dot = Digraph(Name)

        self.Linked = {}
        for id, link, label in self.Links:
            self.Linked[id] = True
            self.Linked[link] = True
            dot.edge(id, link, label = label)

        if len(self.Items) > 0:
            self.DrawRec(None, dot)

        self.Linked = None

        dot.render(Name, format='png', cleanup=True)
        #dot.render(Name, format='svg', cleanup=True)

        #pixmap = QPixmap("Drawing.png")
        #pixmap_item = QGraphicsPixmapItem(pixmap)
        #Graph.scene().addItem(pixmap_item)
        #Graph.fitInView(Graph.scene().sceneRect()) # Autoscaling
