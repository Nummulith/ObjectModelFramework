from graphviz import Digraph
import random

# Создаем объект Digraph
dot = Digraph('AWS_Structure', format='png')

# Размеры квадрата
rows = 4
columns = 4

# Добавляем Subnet как кластер и задаем ему имя
for i in range(1, rows + 1):

    with dot.subgraph(name='cluster_subnet' + str(random.randint(1, 2))) as subnet:
        subnet.attr(label='Subnet Cluster')  # Задаем имя кластера
        subnet.attr(style='filled', fillcolor='#D4E6F1')  # Цветной фон кластера

        with subnet.subgraph() as row:
            row.attr(rank='same')
            for j in range(1, columns + 1):
                index = (i - 1) * columns + j
                row.node(f'EC2_{index}', shape='plaintext', label=f'''<
                    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
                        <TR><TD BGCOLOR="#A9DFBF" PORT="p1">EC2 {index}</TD></TR>
                        <TR><TD BGCOLOR="white" PORT="p2"><IMG SRC="Res_Amazon-EC2_Instance_48.png"/></TD></TR>
                    </TABLE>>''')

# Добавляем связи (10 случайных связей)
for _ in range(10):
    source_index = random.randint(1, rows * columns)
    target_index = random.randint(1, rows * columns)

    # Проверяем, чтобы source_index и target_index не совпадали
    while source_index == target_index:
        target_index = random.randint(1, rows * columns)

    dot.edge(f'EC2_{source_index}:p1', f'EC2_{target_index}:p1')

# Сохраняем диаграмму в файл
dot.render('aws_structure', format='png', cleanup=True)
