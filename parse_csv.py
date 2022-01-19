import csv
from pprint import pprint

'''Сравнивает наличие hostname/ip из csv файла в файле hosts_tmp
'''
def parse_inventory(csv_file):
    with open(csv_file, encoding="utf-16", newline="") as f:
        data = csv.DictReader(f, dialect="excel", delimiter="\t")
        result = []
        for i in data:
            result.append(i)
        return result
    
            
def parse_hosts(hosts_file):
    with open(hosts_file, 'r') as f:
        lines = f.readlines()
    result = [list(line.split()) for line in lines]
    return result


def main():
    hosts = parse_hosts('hosts_tmp')
    inv = parse_inventory('inv.csv')   
    check_lines = [host for host in inv if host['Status'] == 'VM deployed']
    result = []
    for i in check_lines:
        appearence = False
        for host in hosts[3:]:
            if i['Hostname'] in host and i['OAM/MGT IP'] in host:
                appearence = True
        if not appearence:
            result.append(i)
    return result


if __name__ == "__main__":
    pprint(main())
