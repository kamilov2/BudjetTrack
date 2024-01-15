# import uuid


# generated_uuid = uuid.uuid4()
# print(generated_uuid)

# import random

# def generate_shtrix():
#     letters = [chr(random.randint(65, 90)) for _ in range(2)]  
#     numbers = [str(random.randint(0, 9)) for _ in range(6)]  

#     passport_series = ''.join(letters + numbers)
#     return passport_series

# passport_series = generate_shtrix()
# print(passport_series)


# from fluxy.validate import Validator

# result = Validator.validate_passport_number("AD1965018")
# print(result)
# import math

# n = int(input())
# result = math.ceil(n / 10)
# print(result)


# from django.core.management.utils import get_random_secret_key

# print(get_random_secret_key())

# import random 

# name = ['genius', 'unic', 'hypermind', 'sharp', 'rashidevs', 'techtita', 'expro' ]
# print(random.choice(name))

import socket
from scapy.all import ARP, Ether, srp
from scapy.layers.http import HTTPRequest
from scapy.all import sniff

def scan(ip):
    arp_request = ARP(pdst=ip)

    ether = Ether(dst="ff:ff:ff:ff:ff:ff")

    packet = ether/arp_request

    result = srp(packet, timeout=3, verbose=0)[0]

    devices_list = []
    for sent, received in result:
        devices_list.append({'ip': received.psrc, 'mac': received.hwsrc})

    return devices_list

def get_device_name(ip):
    try:
        device_name, _, _ = socket.gethostbyaddr(ip)
        return device_name
    except socket.herror:
        return None

def packet_callback(packet):
    if HTTPRequest in packet:
        url = packet[HTTPRequest].Host + packet[HTTPRequest].Path
        print(f"Visited URL: {url}")

def print_device_info(device):
    device_name = get_device_name(device['ip'])
    print(f"IP Address: {device['ip']}, MAC Address: {device['mac']}, Device Name: {device_name}")

def main():
    target_ip = "192.168.43.21/24"
    devices = scan(target_ip)

    for device in devices:
        print_device_info(device)

    # Run HTTP traffic monitoring
    sniff(prn=packet_callback, store=0, filter="tcp port 80 or port 8080")

if __name__ == "__main__":
    main()
