from fabric import Connection, task
from pprint import pprint
from tabulate import tabulate
import csv
from operator import itemgetter
from colorama import Fore, Style

# import chardet
# import ipdb
# ipdb.set_trace()


CSV = "export.csv"
CMD_CHECK_IP = "ip -br -4 addr | grep eth"
CMD_CHECK_SERVICE_F = "systemctl is-active {}"
TEST_HOST = "nbg42-plsb001-x"
# TEST_HOST = "nbg42-plbvmmz001"
# TEST_HOST = "172.23.111.154"
# TEST_HOST = "localhost"


def print_inventory(inventory):
    columns = [
        "Hostname",
        "MGMT IP",
        "eth0",
        "Service IP",
        "eth1",
        "Service",
        "State",
        "Host",
    ]
    rows = []
    for host, params in inventory.items():
        if params.get("mgmt_ip") != params.get("eth0"):
            params["eth0"] = Fore.RED + str(params.get("eth0")) + Style.RESET_ALL
        if params.get("service_ip") != params.get("eth1"):
            params["eth1"] = Fore.RED + str(params.get("eth1")) + Style.RESET_ALL
        if params.get("service_state") != "active":
            params["service_state"] = (
                Fore.RED + str(params.get("service_state")) + Style.RESET_ALL
            )

        rows.append(
            (
                host,
                params.get("mgmt_ip"),
                params.get("eth0"),
                params.get("service_ip"),
                params.get("eth1"),
                params.get("service"),
                params.get("service_state"),
                params.get("host_state"),
            )
        )
    # rows.sort(key=itemgetter(3, 0))
    print(tabulate(rows, headers=columns, tablefmt="grid", stralign="center"))


def get_inventory_from_csv(csv_file=CSV):
    # with open(csv_file, "rb") as file:
    #     print(chardet.detect(file.read()))
    inventory = {}
    with open(csv_file, encoding="utf-16", newline="") as f:
        data = csv.DictReader(f, dialect="excel", delimiter="\t")
        for row in data:
            if row["Hostname"] is "":
                continue
            inventory[row["Hostname"]] = {
                "service_ip": row["Service IP"],
                "mgmt_ip": row["OAM/MGT IP"],
                "service": row["Service name"],
            }
    return inventory


def run_cmd(conn, cmd):
    try:
        result = conn.run(cmd, hide=True, warn=True)
        result.stdout = result.stdout.strip().splitlines()
        return result
    except Exception as e:
        print(f"Error: {conn.host} is down")


def get_interfaces(result):
    interfaces = {}
    for line in result.stdout:
        print(line)
        for n, param in enumerate(line.split()):
            if n == 0:
                int_name = param
            elif n == 2:
                int_ip = param.split("/")[0]
            elif n > 2:
                int_ip += "\n" + param.split("/")[0]
        interfaces[int_name] = int_ip
    return interfaces


def get_conn(hostname):
    return Connection(hostname, connect_timeout=5)


@task
def test_ip(c):
    conn = get_conn(TEST_HOST)
    ip_cmd_result = run_cmd(conn, CMD_CHECK_IP)
    interfaces = get_interfaces(ip_cmd_result)
    for k, v in interfaces.items():
        print(f"{k} - {v}")


@task
def test_service(c):
    conn = get_conn(TEST_HOST)
    srv_cmd_result = run_cmd(conn, CMD_CHECK_SERVICE_F.format("lisa.service"))
    if srv_cmd_result.ok:
        print("ok")
    else:
        print("failed")

@task
def show_csv(c):
    inventory = get_inventory_from_csv()
    print_inventory(inventory)


@task
def run(c):
    # Load inventory from csv
    inventory = get_inventory_from_csv()
    for host, params in inventory.items():
        print(host)

        # Skip hosts without mgmt_ip
        if not params["mgmt_ip"]:
            continue

        conn = get_conn(params["mgmt_ip"])
        ip_cmd_result = run_cmd(conn, CMD_CHECK_IP)

        # Mark host as down if cmd failed
        if ip_cmd_result is None:
            inventory[host]["host_state"] = "down"
            continue

        interfaces = get_interfaces(ip_cmd_result)
        for int_name, int_ip in interfaces.items():
            inventory[host][int_name] = int_ip

        if params["service"] in ["", "N/A"]:
            print("No service name")
            continue
        srv_cmd_result = run_cmd(conn, CMD_CHECK_SERVICE_F.format(params["service"]))
        if srv_cmd_result is None:
            inventory[host]["host_state"] = "down"
            continue
        print(f"{params['service']}: {srv_cmd_result.stdout[0]}")
        inventory[host]["service_state"] = srv_cmd_result.stdout[0]
    print_inventory(inventory)
