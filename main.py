import base64
import json
import os
import random
import sys
import time
from urllib.parse import parse_qs, unquote
import requests
from datetime import datetime, timedelta

BASE_URL = "https://api.miniapp.dropstab.com/api"

def print_(word):
    now = datetime.now().isoformat(" ").split(".")[0]
    print(f"[⚔] | {word}")

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_query():
    try:
        with open('query.txt', 'r') as f:
            queries = [line.strip() for line in f.readlines()]
        return queries
    except FileNotFoundError:
        print("File query.txt not found.")
        return []
    except Exception as e:
        print("Failed get Query :", str(e))
        return []

def parse_query(query: str):
    parsed_query = parse_qs(query)
    parsed_query = {k: v[0] for k, v in parsed_query.items()}
    user_data = json.loads(unquote(parsed_query['user']))
    parsed_query['user'] = user_data
    return parsed_query

def print_delay(delay):
    print()
    while delay > 0:
        now = datetime.now().isoformat(" ").split(".")[0]
        hours, remainder = divmod(delay, 3600)
        minutes, seconds = divmod(remainder, 60)
        sys.stdout.write(f"\r[⚔] | Waiting Time: {round(hours)} hours, {round(minutes)} minutes, and {round(seconds)} seconds")
        sys.stdout.flush()
        time.sleep(1)
        delay -= 1
    print_("\nWaiting Done, Starting....\n")

def make_request(method, url, headers, json=None, data=None, proxy=None):
    retry_count = 0
    while True:
        time.sleep(2)
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, json=json, proxies={"http": proxy, "https": proxy} if proxy else None)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=json, data=data, proxies={"http": proxy, "https": proxy} if proxy else None)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=json, data=data, proxies={"http": proxy, "https": proxy} if proxy else None)
            else:
                raise ValueError("Invalid method.")
            
            if response.status_code >= 400:
                error_data = response.json()
                error_message = error_data.get('message', 'Unknown error occurred')
                print_(f"{error_message}")
                return None
            elif response.status_code >= 200:
                return response
        except requests.RequestException as e:
            print_(f"Request failed: {e}")
            if retry_count >= 4:
                return None
            retry_count += 1
            continue

def load_config():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        return {
            "daily_bonus": config.get("daily_bonus", True),
            "claim_ref": config.get("claim_ref", True),
            "check_tasks": config.get("check_tasks", True),
            "open_order": config.get("open_order", True),
            "use_telegram_header": config.get("use_telegram_header", True),
            "use_protection": config.get("use_protection", True),
            "use_proxy": config.get("use_proxy", False),
            "random_user_agent": config.get("random_user_agent", False),
            "request_delay": config.get("request_delay", [1, 3]),
            "action_delay": config.get("action_delay", [5, 10]),
            "account_delay": config.get("account_delay", [30, 60]),
            "max_retries": config.get("max_retries", 3)
        }
    except FileNotFoundError:
        print_("File config.json tidak ditemukan. Menggunakan konfigurasi default.")
    except json.JSONDecodeError:
        print_("Error membaca file config.json. Menggunakan konfigurasi default.")
    return {
        "daily_bonus": True,
        "claim_ref": True,
        "check_tasks": True,
        "open_order": True,
        "use_telegram_header": True,
        "use_protection": True,
        "use_proxy": False,
        "random_user_agent": False,
        "request_delay": [1, 3],
        "action_delay": [5, 10],
        "account_delay": [30, 60],
        "max_retries": 3
    }

def load_proxies():
    try:
        with open('proxy.txt', 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print_("File proxy.txt tidak ditemukan.")
        return []

class Ether:

    def __init__(self, config):
        self.config = config
        self.header = self.get_header()
        self.proxies = load_proxies() if self.config["use_proxy"] else []
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]

    def get_header(self):
        if self.config["use_telegram_header"]:
            return {
                "accept": "application/json",
                "accept-language": "en-US,en;q=0.9",
                "content-type": "application/json",
                "user-agent": "TelegramBot (like TwitterBot)",
                "sec-ch-ua": '"Telegram iOS";v="10.1.0", "iOS";v="16.2", "iPhone"',
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": '"iOS"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "Referer": "https://mdkefjwsfepf.dropstab.com/",
                "Referrer-Policy": "strict-origin-when-cross-origin"
            }
        else:
            return {
                "accept": "application/json",
                "accept-language": "en-US,en;q=0.9",
                "content-type": "application/json",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "sec-ch-ua": '"Not_A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
                "sec-ch-ua-mobile": "?0",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "Referer": "https://mdkefjwsfepf.dropstab.com/",
                "Referrer-Policy": "strict-origin-when-cross-origin"
            }

    def protect_request(self, method, url, headers, json=None, data=None):
        if self.config["use_protection"]:
            time.sleep(random.uniform(self.config["request_delay"][0], self.config["request_delay"][1]))
            
            if self.config["random_user_agent"]:
                headers["user-agent"] = random.choice(self.user_agents)
            
            proxy = random.choice(self.proxies) if self.proxies else None
            
            for _ in range(self.config["max_retries"]):
                try:
                    response = make_request(method, url, headers, json, data, proxy)
                    if response is not None:
                        return response
                except Exception as e:
                    print_(f"Error during request: {e}")
                    time.sleep(random.uniform(1, 3))
            
            print_("Max retries reached. Request failed.")
            return None
        else:
            return make_request(method, url, headers, json, data)

    def get_token(self, query):
        url = "https://api.miniapp.dropstab.com/api/auth/login"
        headers = self.header
        payload = {"webAppData": query}
        print_("Generate Token....")
        try:
            response = self.protect_request('post', url, headers=headers, json=payload)
            if response is not None:
                data = response.json()
                token = data["jwt"]["access"]["token"]
                return token
        except Exception as e:
            print_(f"Error Detail : {e}")

    def get_user_info(self, token):
        url = "https://api.miniapp.dropstab.com/api/user/current"
        headers = {
            **self.header,
            'authorization': f"Bearer {token}"
        }
        try:
            response = self.protect_request('get', url, headers=headers)
            if response is not None:
                data = response.json()
                return data
        except Exception as e:
            print_(f"Error Detail : {e}")

    def daily_bonus(self, token):
        url = "https://api.miniapp.dropstab.com/api/bonus/dailyBonus"
        headers = {
            **self.header,
            'authorization': f"Bearer {token}"
        }
        try:
            response = self.protect_request('post',url, headers=headers)
            if response is not None:
                data = response.json()
                result = data.get('result',False)
                if result:
                    print_(f"Daily login Done. Streaks: {data['streaks']}")
                else:
                    print_("Daily Bonus Claimed")
        except Exception as e:
            print_(f"Error Detail : {e}")

    def check_tasks(self, token):
        url = "https://api.miniapp.dropstab.com/api/quest"
        headers = {
            **self.header,
            'authorization': f"Bearer {token}"
        }
        try:
            response = self.protect_request('get',url, headers=headers)
            if response is not None:
                tasks = response.json()
                for task in tasks:
                    name = task.get('name','')
                    quests = task.get('quests',[])
                    print_(f"== Title Task : {name} ==")
                    for quest in quests:
                        claimAllowed = quest.get('claimAllowed',False)
                        name = quest.get('name','')
                        reward = quest.get('reward',0)
                        print_(f"Checking task {name} | Reward {reward}")
                        if claimAllowed:
                            self.claim_task(token, quest["id"], name)
                        else:
                            self.verify_task(token, quest["id"], name)
        except Exception as e:
            print_(f"Error Detail : {e}")

    def verify_task(self, token, task_id, name):
        url = f'https://api.miniapp.dropstab.com/api/quest/{task_id}/verify'
        headers = {
            **self.header,
            'authorization': f"Bearer {token}"
        }
        response = self.protect_request('put',url, headers=headers)
        if response is not None:
            data = response.json()
            print_(f"Verification Task {name} : {data.get('status','')}")

    def claim_task(self, token, task_id, name):
        url = f"https://api.miniapp.dropstab.com/api/quest/{task_id}/claim"
        headers = {
            **self.header,
            'authorization': f"Bearer {token}"
        }
        response = self.protect_request('put',url, headers=headers)
        if response is not None:
            data = response.json()
            print_(f"Claim Task {name} : {data.get('status','')}")

    def claim_ref(self, token):
        print_('Claim Reff Reward')
        url = 'https://api.miniapp.dropstab.com/api/refLink/claim'
        headers = {
            **self.header,
            'authorization': f"Bearer {token}"
        }
        response = self.protect_request('post',url, headers=headers)
        if response is not None:
            data = response.json()
            totalReward = data.get('totalReward',0)
            print_(f"Reff claim Done, Reward : {totalReward}")

    def get_order(self, token):
        url = 'https://api.miniapp.dropstab.com/api/order'
        headers = {
            **self.header,
            'authorization': f"Bearer {token}"
        }
        response = self.protect_request('get',url, headers=headers)
        if response is not None:
            data = response.json()
            return data
    
    def get_coins(self,token, randoms):
        url = 'https://api.miniapp.dropstab.com/api/order/coins'
        headers = {
            **self.header,
            'authorization': f"Bearer {token}"
        }
        response = self.protect_request('get',url, headers=headers)
        if response is not None:
            data = response.json()
            return data
    
    def get_detail_coin(self, token, id):
        url = f'https://api.miniapp.dropstab.com/api/order/coinStats/{id}'
        headers = {
            **self.header,
            'authorization': f"Bearer {token}"
        }
        response = self.protect_request('get',url, headers=headers)
        if response is not None:
            data = response.json()
            return data
        
def key_bot():
    header = """
╔══════════════ ETHERDROP BOT ══════════════╗
║              Bot Automation               ║
║         Developed by @ItbaArts_Dev        ║
╚═══════════════════════════════════════════╝
    """
    print(header)
    
    def post_order(self, token, payload):
        url = 'https://api.miniapp.dropstab.com/api/order'
        headers = {
            **self.header,
            'authorization': f"Bearer {token}"
        }
        response = self.protect_request('post',url, headers=headers, json=payload)
        if response is not None:
            data = response.json()
            list_periods = data.get('periods',[])
            for data in list_periods:
                period = data.get('period',[])
                hours = period.get('hours')
                order = data.get('order',{})
                if len(order) > 0:
                    shorts = "Long"
                    if order.get('short'):
                        shorts = "Short"
                    coin = order.get('coin')
                    print_(f"Open {shorts} in {coin.get('symbol')} at Price {coin.get('price')} time {hours} Hours")
                    break

def main():
    key_bot()
    config = load_config()
    input_coin = input("random choice coin y/n (BTC default)  : ").strip().lower()
    input_order = input("open order l(long), s(short), r(random)  : ").strip().lower()
    while True:
        start_time = time.time()
        delay = 1*3710
        clear_terminal()
        key_bot() 
        queries = load_query()
        sum = len(queries)
        ether = Ether(config)
        for index, query in enumerate(queries, start=1):
            print_(f"Account {index}/{sum}")
            token = ether.get_token(query)
            if token is not None:
                user_info = ether.get_user_info(token)
                print_(f"TGID : {user_info.get('tgId','')} | Username : {user_info.get('tgUsername','None')} | Balance : {user_info.get('balance',0)}")
                
                if config["daily_bonus"]:
                    ether.daily_bonus(token)
                    time.sleep(random.uniform(config["action_delay"][0], config["action_delay"][1]))
                
                if config["claim_ref"]:
                    ether.claim_ref(token)
                    time.sleep(random.uniform(config["action_delay"][0], config["action_delay"][1]))
                
                if config["open_order"]:
                    data_order = ether.get_order(token)
                    if data_order is not None:
                        totalScore = data_order.get('totalScore',0)
                        results = data_order.get('results',{})
                        print_(f"Result Game : {results.get('orders',0)} Order | {results.get('wins',0)} Wins | {results.get('loses',0)} Loses | {results.get('winRate',0.0)} Winrate")
                        list_periods = data_order.get('periods',[])
                        detail_coin = ether.get_coins(token, input_order)
                        for list in list_periods:
                            period = list.get('period',{})
                            unlockThreshold = period.get('unlockThreshold',0)
                            detail_order = list.get('order',{})
                            id = period.get('id',1)
                            if totalScore >= unlockThreshold:
                                status = [True, False]
                                if input_coin =='y':
                                    coins = random.choice(detail_coin)
                                else:
                                    coins = detail_coin[0]

                                if input_order == 'l':
                                    status_order = status[1]
                                elif input_order == 's':
                                    status_order = status[0]
                                else:
                                    status_order = random.choice(status)
                                if detail_order is None:
                                    coin_id = coins.get('id')
                                    payload = {'coinId': coin_id, 'short': status_order, 'periodId': id}
                                    ether.post_order(token=token, payload=payload)
                        
                if config["check_tasks"]:
                    ether.check_tasks(token)
                    time.sleep(random.uniform(config["action_delay"][0], config["action_delay"][1]))

            # Delay antar akun
            if index < sum:  # Tidak perlu delay setelah akun terakhir
                account_delay = random.uniform(config["account_delay"][0], config["account_delay"][1])
                print_(f"Menunggu {account_delay:.2f} detik sebelum akun berikutnya...")
                time.sleep(account_delay)

        end_time = time.time()
        total = delay - (end_time-start_time)
        print_delay(total)

if __name__ == "__main__":
     main()
