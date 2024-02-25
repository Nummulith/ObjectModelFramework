from Drawing import Drawing

drawing = Drawing()

def html_label(text):
    ''' html code for cluster header '''
    return f'''<
        <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4">
            <TR>
                <TD><B>{text}</B></TD>
            </TR>
        </TABLE>
    >'''


def add_table(listname, listitems):
    label = f'<TR><TD BGCOLOR="#A9DFBF"><B>{listname}</B></TD></TR>\n'
    for listitem in listitems:
        label += f'<TR><TD BGCOLOR="white" PORT="{listitem}"><FONT POINT-SIZE="12.0">{listitem}</FONT></TD></TR>\n'

    label = f'''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
        {label}
        </TABLE>
    >'''

    drawing.add_item(listname, drawing.item_view(label, shape='plaintext'))

    return listname


def add_item(text):
    drawing.add_item(text,
        node    = drawing.item_view(html_label(text), style = 'filled'),
        cluster = drawing.item_view(html_label(text), style = 'filled', fillcolor = "#add8e6"),
        point   = drawing.item_view("", shape='point', width='0.1')
    )
    return text


s1 = add_item("DataBase")

add_table("Employees", ["id", "first_name", "last_name", "position", "salary"])
add_table("Departments", ["id", "department_name", "manager_id"])
add_table("Customers", ["id", "first_name", "last_name", "address", "phone", "email"])
add_table("Products", ["id", "name", "description", "price", "stock_quantity"])
add_table("Orders", ["id", "customer_id", "order_date", "order_amount", "status"])
add_table("OrderDetails", ["order_id", "product_id", "quantity", "cost"])

drawing.add_parent("Customers", "DataBase")
drawing.add_parent("Products", "DataBase")
drawing.add_parent("Orders", "DataBase")
drawing.add_parent("OrderDetails", "DataBase")
drawing.add_parent("Employees", "DataBase")
drawing.add_parent("Departments", "DataBase")

drawing.add_link("Customers:id", "Orders:customer_id")
drawing.add_link("Products:id", "OrderDetails:product_id")
drawing.add_link("Orders:id", "OrderDetails:order_id")
drawing.add_link("Employees:id", "Departments:manager_id")

drawing.draw("GraphDemo")
