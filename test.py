import xml.etree.ElementTree as ET

def PlainQuery(tree, path, pref = ".//", res = [], parfields = None):
    this, _, next = path.partition("/")

    xpath_query = pref + this

    result = tree.findall(xpath_query)

    for item in result:
        fields = {} if parfields == None else parfields.copy()
        
        for child in item:
            fields[child.tag] = child.text

        if next:
            PlainQuery(item, next, "./", res, fields)
        else:
            res.append(fields)
    
    return res



# Ваш XML-документ
xml_data = '''
<root>
    <list_item>
        <Description>Provides AWS Backup permission (одинаковое описание для двух строк)</Description>
        <RoleInfo>
            <RoleName>AWSBackupDefaultServiceRole0</RoleName>
            <Service>backup.amazonaws.com</Service>
        </RoleInfo>
        <RoleInfo>
            <RoleName>AWSBackupDefaultServiceRole1</RoleName>
            <Service>backup.amazonaws.com</Service>
        </RoleInfo>
    </list_item>
    <list_item>
        <Description>Provides Cloud9 SSM access</Description>
        <RoleInfo>
            <RoleName>AWSCloud9SSMAccessRole</RoleName>
            <Service>cloud9.amazonaws.com</Service>
        </RoleInfo>
    </list_item>
</root>
'''

# Преобразование XML-строки в объект ElementTree
root = ET.fromstring(xml_data)
tree = ET.ElementTree(root)

res = PlainQuery(tree, "list_item/RoleInfo")
print(res)

pass