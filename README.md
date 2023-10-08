# 5ch Script

5chのスクリプト

## インストール
```bash
pip install requests
```
## 使い方
```bash
# スレ立て
python script.py tate https://kes.5ch.net/chiikawa/ 10 msg.txt
# 全てのスレにレス
python script.py resu https://kes.5ch.net/chiikawa/ 100 msg.txt
# 特定のスレのみにレス
python script.py resu https://kes.5ch.net/test/read.cgi/chiikawa/123456789/ 10 msg.txt
# プロキシ(http) プロキシのリスト(http.txt) 終了タイマー(60) 送信の遅延時間(10) ログ
python script.py resu https://kes.5ch.net/chiikawa/ 400 msg.txt -p http -pl http.txt -t 60 -d 10 -l
```
- コマンドライン引数
  - Method
    - tate(スレ立て)
    - resu(レス)
  - URL
    - 全てのスレ https://kes.5ch.net/chiikawa/
    - 特定のスレのみ https://kes.5ch.net/test/read.cgi/chiikawa/123456789/
  - Threads スレッド数
  - Msg_list 送信するメッセージのリスト
- オプション
    - -p --proxy プロキシの種類(http,https,socks4,socks5,socks5h)
    - -pl --proxy_list プロキシのリスト
    - -t --time 終了タイマー
    - -d --delay 送信の遅延時間
    - -l --log ログ

その他設定ハードコード
