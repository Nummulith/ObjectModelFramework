from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QVBoxLayout, QWidget
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap

from graphviz import Digraph

from AWSclasses import *

class cRoot(cParent):
    def __init__(self, Data):
        super().__init__(Data, None, 0, {"Id": "root-" + 17*"0"})

    @staticmethod
    def Fields():
        return {"Id" : (cRoot,True,False,False,False)}


class MyWidget(QWidget):
    def __init__(self):
        super(MyWidget, self).__init__()
        loadUi('AWS-graph.ui', self)

        self.Graph.setScene(QGraphicsScene(self))

        self.bDraw.clicked.connect(self.Draw)

        self.Draw()

    def NodeLabel(self, obj):
        draw  = type(obj).Draw
        color = type(obj).Color

        res = ""
        if draw[0]: res = res + f'''
                <TR>
                    <TD BGCOLOR="{color}" PORT="p0"><B>{obj.GetView()}</B></TD>
                </TR>
        '''
        if draw[1]: res = res + f'''
                 <TR>
                     <TD BGCOLOR="white" PORT="p1"><B>{obj.GetExt()}</B></TD>
                 </TR>
        '''
        if draw[2]: res = res + f'''
                <TR>
                    <TD BGCOLOR="white" PORT="p2"><IMG SRC="icons/{type(obj).Icon}.png"/></TD>
                </TR>
        '''
        if draw[3]: res = res + f'''
                <TR>
                    <TD BGCOLOR="{color}" PORT="p3"><FONT POINT-SIZE="7.0">{obj.GetId()[-17:]}</FONT></TD>
                </TR>
        '''
        
        return f'''<
            <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
            {res}
            </TABLE>
        >'''

    def ClusterLabel(self, obj):
        draw = obj.Draw

        res0 = ""
        if draw[2]: res0 = res0 + f'''
                    <TD ROWSPAN="3"><IMG SRC="icons/{type(obj).Icon}.png"/></TD>
        '''
        if draw[0]: res0 = res0 + f'''
                    <TD><B>{obj.GetView()}</B></TD>
        '''
        res0 = f'''
                <TR>
                    {res0}
                </TR>
        '''

        res1 = ""
        if draw[1]: res1 = res1 + f'''
                <TR>
                    <TD><FONT POINT-SIZE="7.0">{obj.GetExt()}</FONT></TD>
                </TR>
        '''
        if draw[3]: res1 = res1 + f'''
                <TR>
                    <TD><FONT POINT-SIZE="7.0">{obj.GetId()[-17:]}</FONT></TD>
                </TR>
        '''

        return f'''<
            <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4">
                {res0}
                {res1}
            </TABLE>
        >'''

    def DrawRec(self, par):
        for clss, list in self.Data.items():
            if not clss.Show: continue

            for id, obj in list.items():
                if par == None:
                    if hasattr(obj, "_Owner") : continue
                else:
                    if (not hasattr(obj, "_Owner") or obj._Owner != par) \
                    : continue
                        #and obj != par \

                if not hasattr(par, "_Digraph"):
                    name = "cluster_" + obj.GetId()[-17:]
                    par._Context = par._Owner._Digraph.subgraph(name=name)
                    par._Digraph = par._Context.__enter__()
#                    par._Digraph.attr(label='cluster\n' + par.GetId()) # + par.GetId()
                    par._Digraph.attr(label=self.ClusterLabel(par)) # + par.GetId()
                    par._Digraph.attr(style = 'filled', fillcolor = type(par).Color)

                    par._Digraph.node(name=par.GetId(), shape='point', width='0.1')
                
                
                if len(obj.items) == 0:
                    par._Digraph.node(name=obj.GetId(), shape='plaintext', label=self.NodeLabel(obj))
                else:
                    self.DrawRec(obj)

                #print(f"{par}.{par.GetId()} -> {obj}.{obj.GetId()} ")
        
        if hasattr(par, "_Context"):
            par._Context.__exit__(None, None, None)
            par._Context = None

        if hasattr(par, "_Digraph"):
            par._Digraph = None


    def Draw(self):
        
        self.Data = {}

        root = cRoot(self.Data)
        cParent.LoadObjects(self.Data, cInternetGateway)
        cParent.LoadObjects(self.Data, cVpc        )
        cParent.LoadObjects(self.Data, cSubnet     )
        cParent.LoadObjects(self.Data, cReservation)
        cParent.LoadObjects(self.Data, cNATGateway )
        cParent.LoadObjects(self.Data, cNetworkAcl )
        cParent.LoadObjects(self.Data, cRouteTable )
        cParent.LoadObjects(self.Data, cSecurityGroup)
        cParent.LoadObjects(self.Data, cNetworkInterface)
#        cParent.LoadObjects(self.Data, cS3)

        

        for clss, lst in self.Data.items():
            for id, obj in lst.items():
                owner = obj.GetOwner(self.Data)
                if owner == None:
                    owner = root

                # if obj.ParentField != None:
                #     parcl = clss.Fields()[obj.ParentField][fType]
                #     if hasattr(obj, obj.ParentField):
                #         if obj.ParentField == "_Parent":
                #             owner = obj._Parent
                #         else:
                #             parid = getattr(obj, obj.ParentField)
                #             owner = self.Data[parcl][parid]

                obj._Owner = owner
                owner.items.append(obj)

        dot = Digraph('AWS_Structure', format='png')

        root._Digraph = dot

        self.DrawRec(root)


        for clss, lst in self.Data.items():
            for id, obj in lst.items():
                objid = obj.GetId()

                for field in obj.FieldsOfAKind(fIn):
                    corr = getattr(obj, field, None)
                    if corr == None: continue
                    dot.edge(objid, corr, label = field)

                for field in obj.FieldsOfAKind(fOut):
                    corr = getattr(obj, field, None)
                    if corr == None: continue
                    dot.edge(corr, objid, label = field + "<")

#        for bod in dot.body:
#            print(bod)

        # Сохраняем диаграмму в файл
        dot.render('AWS-graph', format='png', cleanup=True)

        #pixmap = QPixmap("AWS-graph.png")
        #pixmap_item = QGraphicsPixmapItem(pixmap)
        #self.Graph.scene().addItem(pixmap_item)

        #self.Graph.fitInView(self.Graph.scene().sceneRect()) # Autoscaling

#        self.close()


if __name__ == '__main__':
    app = QApplication([])
    widget = MyWidget()
#    widget.show()
#    app.exec_()
