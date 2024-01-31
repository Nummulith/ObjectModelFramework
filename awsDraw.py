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

def DrawRec(aws, par):
    for clss in Classes:
        wrap = aws[clss]

        if not clss.Show: continue

        for id, obj in wrap.Map.items():

            if par == None:
                if hasattr(obj, "_Owner") : continue
            else:
                if (not hasattr(obj, "_Owner") or obj._Owner != par) \
                : continue

            if not hasattr(par, "_Digraph") or par._Digraph == None:
                name = "cluster_" + obj.GetId()[-17:]
                par._Context = par._Owner._Digraph.subgraph(name=name)
                par._Digraph = par._Context.__enter__()
                label = ClusterLabel(par)
#                print(f"> {id} -> {label}")
                par._Digraph.attr(label=label)
                par._Digraph.attr(style = 'filled', fillcolor = type(par).Color)

                par._Digraph.node(name=par.GetId(), shape='point', width='0.1')
            
            
            if len(obj.items) == 0:
                label = NodeLabel(obj)
#                print(f"> {id} -> {label}")
                par._Digraph.node(name=obj.GetId(), shape='plaintext', label=label)
            else:
                DrawRec(aws, obj)

            #print(f"{par}.{par.GetId()} -> {obj}.{obj.GetId()} ")
    
    if hasattr(par, "_Context"):
        par._Context.__exit__(None, None, None)
        par._Context = None

    if hasattr(par, "_Digraph"):
        par._Digraph = None


def Draw(aws):
    root = cRoot()

    for clss in Classes:
        wrap = aws[clss]

        for id, obj in wrap.Map.items():
            owner = obj.GetOwner(aws)
            if owner == None:
                owner = root

            obj._Owner = owner
            owner.items.append(obj)

    dot = Digraph('AWS_Structure') #, format='png'

    root._Digraph = dot

    DrawRec(aws, root)


    for clss in Classes:
        wrap = aws[clss]

        for id, obj in wrap.Map.items():
            objid = obj.GetId()

            for field in obj.FieldsOfAKind(fOut):
                corr = getattr(obj, field, None)
                if corr == None: continue
                dot.edge(objid, corr, label = field)

            for field in obj.FieldsOfAKind(fIn):
                corr = getattr(obj, field, None)
                if corr == None: continue
                dot.edge(corr, objid, label = field + "<")


    dot.render('awsDraw', format='png', cleanup=True)
    dot.render('awsDraw', format='svg', cleanup=True)

    #pixmap = QPixmap("awsDraw.png")
    #pixmap_item = QGraphicsPixmapItem(pixmap)
    #Graph.scene().addItem(pixmap_item)
    #Graph.fitInView(Graph.scene().sceneRect()) # Autoscaling
