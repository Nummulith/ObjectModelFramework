from graphviz import Digraph

from awsClasses import *

class cRoot(cParent):
    def __init__(self):
        super().__init__(None, None, {"Id": "root-" + 17*"0"})

    @staticmethod
    def Fields():
        return {"Id" : (cRoot,True,False,False,False)}

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


def DrawRec(aws, drawing, parent, grandDigraph):
    parId = parent.GetId()
    parContext = None
    parDigraph = None

    for clss in Classes:
        wrap = aws[clss]

        if not clss.Show: continue

        for id, obj in wrap.Map.items():

            if parent == None:
                if hasattr(obj, "_Owner") : continue
            else:
                if (not hasattr(obj, "_Owner") or obj._Owner != parent) : continue

            drawing.AddParent(id, parId)

            if parContext == None:
                parContext = grandDigraph.subgraph(name = "cluster_" + parId)
                parDigraph = parContext.__enter__()

                parDigraph.attr(label = ClusterLabel(parent))
                parDigraph.attr(style = 'filled', fillcolor = type(parent).Color)

                parDigraph.node(name=parId, shape='point', width='0.1')
                
                drawing.AddItem(parId,
                    cluster = ItemView(ClusterLabel(parent), style = 'filled', fillcolor = type(parent).Color),
                    point   = ItemView("", shape='point', width='0.1')
                )

            if len(obj.DrawItems) == 0:
                parDigraph.node(name=id, shape='plaintext', label = NodeLabel(obj))

                drawing.AddItem(id, ItemView(NodeLabel(obj), shape='plaintext'))

            else:
                DrawRec(aws, drawing, obj, parDigraph)

    if parContext != None:
        parContext.__exit__(None, None, None)



def Draw(aws):
    drawing = Drawing()

    root = cRoot()

    for clss in Classes:
        wrap = aws[clss]

        for id, obj in wrap.Map.items():
            owner = obj.GetOwner(aws)
            if owner == None: owner = root

            obj._Owner = owner
            owner.DrawItems.append(obj)

    dot = Digraph('AWS_Structure')
    DrawRec(aws, drawing, root, dot)

    for clss in Classes:
        wrap = aws[clss]

        for id, obj in wrap.Map.items():
            objid = obj.GetId()

            for field in obj.FieldsOfAKind(fOut):
                corr = getattr(obj, field, None)
                if corr == None: continue
                dot.edge(objid, corr, label = field)
                drawing.AddLink(objid, corr, field)

            for field in obj.FieldsOfAKind(fIn):
                corr = getattr(obj, field, None)
                if corr == None: continue
                dot.edge(corr, objid, label = field + "<")
                drawing.AddLink(corr, objid, field + "<")

    dot.render('awsDraw', format='png', cleanup=True)
    #dot.render('awsDraw', format='svg', cleanup=True)


    drawing.print()
    drawing.Draw()



    #pixmap = QPixmap("awsDraw.png")
    #pixmap_item = QGraphicsPixmapItem(pixmap)
    #Graph.scene().addItem(pixmap_item)
    #Graph.fitInView(Graph.scene().sceneRect()) # Autoscaling
