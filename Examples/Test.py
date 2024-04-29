from awsClasses import PAR, bt
import requests

def Test0(aws):
    instance_id = 'i-06c51f4f542763747'

    # Создайте объект клиента SSM
    ssm_client = bt('ssm')

    # Запустите команду на экземпляре и получите CommandId
    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName='AWS-RunShellScript',
        Parameters={'commands': ['systemctl is-active apache2']}
    )

    command_id = response['Command']['CommandId']

    waiter = ssm_client.get_waiter('command_executed')

    # Определите максимальное время ожидания в секундах (например, 300 секунд)
    max_wait_time = 300

    # try:
    waiter.wait(
        InstanceId=instance_id,
        CommandId=command_id,
        WaiterConfig={
            'Delay': 15,  # Интервал проверки статуса (в секундах)
            'MaxAttempts': max_wait_time // 15  # Максимальное количество попыток
        }
    )
    # except WaiterError as e:
    #     print(f"Waiter failed: {e}")


def Test1(aws):

    # Создайте объект клиента SSM
    ssm_client = boto3.client('ssm')

    # Укажите ID вашего EC2-инстанса
    instance_id = 'your_instance_id'

    # Определите команду, которую вы хотите выполнить (проверка статуса Apache)
    command = 'systemctl is-active apache2'

    # Отправьте команду на экземпляр
    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName='AWS-RunShellScript',
        Parameters={'commands': [command]}
    )

    # Получите идентификатор команды для проверки статуса выполнения
    command_id = response['Command']['CommandId']

    # Дождитесь завершения выполнения команды
    ssm_client.get_command_invocation(
        CommandId=command_id,
        InstanceId=instance_id
    )

def Test3(aws):
    url = "http://18.192.62.22/"
    response = requests.get(url)

    if response.status_code == 200:
        html_content = response.text
        print(html_content)
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

def Test2(aws):
    print("(---")

    aws.save()

    # objs = aws.EC2_SecurityGroup.fetch("sg-031f7e69b595ae094", None, True)
    
    # objs = aws.EC2_SecurityGroup_Rule.fetch(None, None, True)
    objs = aws.EC2_SecurityGroup_Rule.objects()

    for grr in objs:
        if not grr.IsEgress and grr.IpProtocol == "tcp" and grr.FromPort == 80:
            print(f"{grr.GroupId} \\ {grr.IsEgress} {grr.IpProtocol} / {grr.FromPort} -> {grr.ToPort}")
            sg = grr['GroupId']
        else:
            aws.EC2_SecurityGroup_Rule.release(grr.get_id())

    # key_pair_name = "Pavel"

    # objs = aws.EC2_KeyPair.fetch(
    #     filter = {"KeyNames" : (["key-" + key_pair_name], PAR.PAR)},
    #     create_par = {"name": key_pair_name}
    # )
    objs = aws.EC2_KeyPair.objects()

    for obj in objs:
        print(f"{obj.KeyPairId} - {obj.KeyName}")

    # objs = aws.EC2_Instance.fetch(
    #     {"instance-state-name" : (['running'], PAR.FILTER)}
    # )
    # objs = aws.EC2_Instance.fetch({"key-name" : ([key_pair_name], PAR.FILTER)})
    objs = aws.EC2_Instance.fetch("i-0091b120c539d10e8")
    # objs = aws.EC2_Instance.objects()

    # for obj in objs:
    #     cur_key_pair_name = obj["KeyPairId"].KeyName if hasattr(obj, "KeyPairId") else "-"
    #     print(f"{obj.Tag_Name} : {cur_key_pair_name} - {obj.PublicIpAddress}")

    print("---)")

def Test3(aws):
    print("(---")

    objs = aws.EC2_SecurityGroup.fetch(None, None, True)
    for obj in objs:
        ec2 = obj["ParentId"]
        sg  = obj["GroupId"]
        sgrs = aws.EC2_SecurityGroup_Rule.fetch(f"{obj.GroupId}|*", None, True)

        for sgr in sgrs:
            if sgr.FromPort != 80:
                continue
            
            print(f"{ec2.InstanceId} - {getattr(ec2, "PublicIpAddress", "x")} - {ec2.Tag_Name} - {sg.VpcId} - {obj.GroupName} - {sgr.FromPort}")

    print("---)")

def Test4(aws):
    print("(---")

    objs = aws.AWS_AvailabilityZone.fetch()
    for obj in objs:
        print(f"{obj.ZoneId} - {obj.ZoneName}")
    

    objs = aws.EC2_Subnet.fetch(None, None, True)
    for obj in objs:
        print(f"{obj} - {obj}")

    print("---)")

def Test(aws):
    print("(---")

    objs = aws.ELB_Listener.fetch()
    for obj in objs:
        print(f"{obj}")

    print("---)")
