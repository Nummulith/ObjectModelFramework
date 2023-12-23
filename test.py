from graphviz import Digraph

dot = Digraph('cluster_example', format='png')

# Создаем кластер снизу
with dot.subgraph():
    dot.node('bottom_text', label='<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4"><TR><TD ALIGN="CENTER">Bottom Text</TD></TR></TABLE>>', shape='plaintext')


# Создаем кластер сверху
with dot.subgraph(name='cluster_top') as top_cluster:
    top_cluster.node('top_text', label='Top Text', shape='plaintext')

# Связываем кластеры
dot.edge('top_text', 'bottom_text')

# Сохраняем граф в файл
dot.render(filename='cluster_example', format='png', cleanup=True)
