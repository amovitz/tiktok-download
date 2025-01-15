#! /usr/bin/python3

import json, time, requests, os

TTL = 5
OVER = False
TIMEOUT = (10 * 60)

PATH = input("Path to user_data_tiktok.json? [./user_data_tiktok.json]: ")
if PATH == "" or PATH == None:
    PATH = "./user_data_tiktok.json"
if not PATH.endswith("/user_data_tiktok.json"):
    PATH += "/user_data_tiktok.json"

OUT = input("Path to output video files? [./]: ")
if OUT == "" or OUT == None:
    OUT = "./"

f = open(PATH, 'r')
t = f.read()
j = json.loads(t)

print("Date\t\t\tLikes\tLocation")
for v in j["Video"]["Videos"]["VideoList"]:
    print(f"{v['Date']}\t{v['Likes']}\t{v['Location']}", end='')
    u = v['Link']
    o = f"{OUT}/{v['Date']} - {v['Likes']} Likes.mp4"
    if os.path.exists(o):
        if not OVER:
            print("\t\tEXISTS")
            continue
    try:
        with requests.get(u, stream=True, timeout=TIMEOUT) as r:
            r.raise_for_status()
            with open(o, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print("\t\tOK")

        time.sleep(TTL)
    except KeyboardInterrupt:
        print("Exiting...")
        os.remove(o)
        exit(0)
    except:
        print(f"\t\tERROR - {u}")
        try:
            os.remove(o)
        except:
            pass
