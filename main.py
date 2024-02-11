from multiprocessing.pool import ThreadPool as Pool
from time import sleep
from os import system
import threading
import os

try:
    import secp256k1Crypto
except:
    system('pip install secp256k1Crypto')
    import secp256k1Crypto

try:
    import requests
except:
    system('pip install requests')
    import requests

try:
    from Crypto.Hash import keccak
except:
    system('pip install pycryptodome')
    from Crypto.Hash import keccak



with open("key.txt", "r") as file:
    list_key = file.read().split(":")

with open("conf_bot.txt", "r") as file:
    list_conf = file.read().split("/")

lock = threading.Lock()
prog_name = "1"


class Settings():
    count = 0
    no_take_count = 0
    key = list_key[-1]
    token_bot = list_conf[0]
    id_user = list_conf[1]


def makeDir():
    path = 'results'
    if not os.path.exists(path):
        os.makedirs(path)


def get_eth_addr():
    private_key = secp256k1Crypto.PrivateKey()
    private_key_str = private_key.serialize()
    public_key_bytes = private_key.pubkey.serialize(compressed=False)
    public_key_str = public_key_bytes.hex()
    keccak_hash = keccak.new(digest_bits=256)
    keccak_hash.update(public_key_bytes[1:])
    h = keccak_hash.hexdigest()
    address = '0x' + h[-40:]
    return {
        "private_key": private_key_str,
        "public_key": public_key_str,
        "address": address
    }


def get_many_adr():
    list_adr = {}
    for _ in range(20):
        rep = get_eth_addr()
        adr = rep["address"]
        privat_key = rep["private_key"]
        list_adr.update([(f'{adr}', privat_key)])

    return list_adr


def list_adr_join(adress):
    spliter = ","

    return spliter.join(adress)


def check_balance(adress, key):
    try:
        rep = requests.get(
            f"https://api.bscscan.com/api?module=account&action=balancemulti&address={adress}&tag=latest&apikey={key}")
        return rep.json()

    except Exception:
        Settings.key = list_key.pop(0)
        list_key.append(Settings.key)

        msg = f"Ферма {prog_name}. Меняю ключ на {Settings.key}"
        url = f"chat_id={Settings.id_user}&text={msg}"
        #requests.get(f"https://api.telegram.org/bot{Settings.token_bot}/sendMessage", url)


def check():
    while True:
        if (Settings.count * 20) > 100000:
            Settings.no_take_count += Settings.count
            Settings.count = 0
        else:
            pass

        key = Settings.key
        base_address = get_many_adr()  # return adress with privat_key
        only_adress = list_adr_join(list(base_address))  # return list with address
        balances = check_balance(only_adress, key)  # return info about 20 address

        with lock:
            Settings.count += 1
            for money in balances["result"]:

                address = money["account"]
                balance = int(money["balance"])
                privat_key = base_address[address]

                if balance > 0:
                    print(f"!!!! ADDRESS: {address} | BALANCE: {balance} | KEY: {privat_key}")
                    msg = f"{prog_name} нашла ADDRESS: {address} | BALANCE: {balance} | KEY: {privat_key}"
                    url = f"chat_id={Settings.id_user}&text={msg}"
                    requests.get(f"https://api.telegram.org/bot{Settings.token_bot}/sendMessage", url)


                else:
                    print(f"ADDRESS: {address} | BALANCE: {balance} | KEY: {privat_key}")
        sleep(1.7)


def start():
    threads = 10;
    pool = Pool(threads)
    for _ in range(threads):
        pool.apply_async(check, ())
    pool.close()
    pool.join()


if __name__ == "__main__":
    #msg = f"test"
    #url = f"chat_id={Settings.id_user}&text={msg}"
    #requests.get(f"https://api.telegram.org/bot{Settings.token_bot}/sendMessage", url)
    start()
