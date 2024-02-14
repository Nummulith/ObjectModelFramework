from graphviz import Digraph

from awsClasses import *

def NodeLabel(obj):
    draw  = type(obj).Draw
    color = type(obj).Color

    res = ""
    if draw & dView: res = res + f'''
        <TR>
            <TD BGCOLOR="{color}" PORT="p0"><B>{obj.GetView()}</B></TD>
        </TR>
    '''
    if draw & dExt : res = res + f'''
        <TR>
            <TD BGCOLOR="white" PORT="p1"><B>{obj.GetExt()}</B></TD>
        </TR>
    '''
    if draw & dIcon: res = res + f'''
        <TR>
            <TD BGCOLOR="white" PORT="p2"><IMG SRC="icons/{type(obj).Icon}.png"/></TD>
        </TR>
    '''
    res = res + f'''
        <TR>
            <TD BGCOLOR="white" PORT="p4"><FONT POINT-SIZE="7.0">{obj.GetClassView()}</FONT></TD>
        </TR>
    '''
    if draw & dId  : res = res + f'''
        <TR>
            <TD BGCOLOR="{color}" PORT="p3"><FONT POINT-SIZE="7.0">{obj.GetId()[-17:]}</FONT></TD>
        </TR>
    '''
    if res == "":
        res = res + f'''
        <TR>
            <TD BGCOLOR="{color}" PORT="p0"><B>{obj.GetId()}</B></TD>
        </TR>
    '''

    return f'''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
        {res}
        </TABLE>
    >'''

def ClusterLabel(obj):
    draw = obj.Draw

    res0 = ""
    if draw & dIcon: res0 = res0 + f'''
        <TD ROWSPAN="3"><IMG SRC="icons/{type(obj).Icon}.png"/></TD>
    '''
        
    if draw & dView: res0 = res0 + f'''
        <TD><B>{obj.GetView()}</B></TD>
    '''
        
    if res0 != "":
        res0 = f'''
    <TR>
        {res0}
    </TR>
    '''

    res1 = ""
    if draw & dExt: res1 = res1 + f'''
    <TR>
        <TD><FONT POINT-SIZE="7.0">{obj.GetExt()}</FONT></TD>
    </TR>
    '''
        
    res1 = res1 + f'''
        <TR>
            <TD><FONT POINT-SIZE="7.0">{obj.GetClassView()}</FONT></TD>
        </TR>
        '''

    if draw & dId: res1 = res1 + f'''
        <TR>
            <TD><FONT POINT-SIZE="7.0">{obj.GetId()[-17:]}</FONT></TD>
        </TR>
        '''

    if res0 == "" and res1 == "":
        res0 = res0 + f'''
        <TR>
            <TD PORT="p0"><B>{obj.GetId()}</B></TD>
        </TR>
    '''

    return f'''<
        <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4">
            {res0}
            {res1}
        </TABLE>
    >'''

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
        items = [id for id in self.Items if not id in self.Parents] \
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
                    parDigraph.attr(label = view["label"], style = view["style"], fillcolor = view["fillcolor"])

                    view = self.Items[parent]["point"]
                    parDigraph.node(name=parent, shape=view["shape"], width=view["width"])
                    
                self.DrawRec(id, parDigraph)

            if parContext != None:
                parContext.__exit__(None, None, None)


    def Draw(self):
        dot = Digraph('AWS_Structure1')

        self.DrawRec(None, dot)

        for id, link, label in self.Links: dot.edge(id, link, label = label)

        dot.render('awsDraw1', format='png', cleanup=True)
        #dot.render('awsDraw1', format='svg', cleanup=True)


def Draw(aws):
    drawing = Drawing()

    hasowned = {}
    owners = {}

    for clss in Classes:
        wrap = aws[clss]

        for id, obj in wrap.Map.items():
            owner = obj.GetOwner(aws)
            if owner != None:
                owners[obj] = owner
                hasowned[owner] = True

    for clss in Classes:
        wrap = aws[clss]
        if not clss.Show: continue

        for id, obj in wrap.Map.items():

            if not obj in hasowned:
                drawing.AddItem(id, ItemView(NodeLabel(obj), shape='plaintext'))

            else:
                drawing.AddItem(id,
                    cluster = ItemView(ClusterLabel(obj), style = 'filled', fillcolor = type(obj).Color),
                    point   = ItemView("", shape='point', width='0.1')
                )

            par = owners[obj] if obj in owners else None
            if par != None:
                drawing.AddParent(id, par.GetId())

            for field in obj.FieldsOfAKind(fOut):
                corr = getattr(obj, field, None)
                if corr == None: continue
                drawing.AddLink(id, corr, field)

            for field in obj.FieldsOfAKind(fIn):
                corr = getattr(obj, field, None)
                if corr == None: continue
                drawing.AddLink(corr, id, field + "<")


    drawing.print()
    drawing.Draw()



    #pixmap = QPixmap("awsDraw.png")
    #pixmap_item = QGraphicsPixmapItem(pixmap)
    #Graph.scene().addItem(pixmap_item)
    #Graph.fitInView(Graph.scene().sceneRect()) # Autoscaling
