#! /usr/bin/python3

import json, time, requests, os

TTL = 5  # Time to wait between successful downloads
OVER = False  # Whether to overwrite existing files
TIMEOUT = (10 * 60)  # Timeout duration for requests (10 minutes)

MAX_RETRIES = 5  # Maximum retry attempts for failed downloads

PATH = input("Path to user_data_tiktok.json? [./user_data_tiktok.json]: ")
if PATH == "" or PATH == None:
    PATH = "./user_data_tiktok.json"
if not PATH.endswith("/user_data_tiktok.json"):
    PATH += "/user_data_tiktok.json"

OUT = input("Path to output video files? [./]: ")
if OUT == "" or OUT == None:
    OUT = "./"

# Load the JSON file
with open(PATH, 'r') as f:
    t = f.read()
    j = json.loads(t)

print("Date\t\t\tLikes\tLocation")

# List to store failed download attempts
failed_downloads = []

# First pass: Try to download all files, add failed ones to failed_downloads
for v in j["Video"]["Videos"]["VideoList"]:
    print(f"{v['Date']}\t{v['Likes']}\t{v['Location']}", end='')
    u = v['Link']
    o = f"{OUT}/{v['Date']} - {v['Likes']} Likes.mp4"

    if os.path.exists(o):
        if not OVER:
            print("\t\tEXISTS")
            continue

    success = False
    try:
        with requests.get(u, stream=True, timeout=TIMEOUT) as r:
            r.raise_for_status()  # Will raise HTTPError for bad status codes
            with open(o, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print("\t\tOK")
        success = True

    except requests.exceptions.RequestException as e:
        print(f"\t\tERROR - {u}")
        print(f"Error details: {e}")
        failed_downloads.append(v)  # Add to failed_downloads list

    except KeyboardInterrupt:
        print("Exiting...")
        os.remove(o)
        exit(0)

    if not success:
        print(f"\t\tFAILED - Added to retry list.")
    
    # Add a small sleep between successful downloads to avoid overloading the server
    time.sleep(TTL)

# Retry the failed downloads after the first pass
retries = 0
while retries < MAX_RETRIES and failed_downloads:
    print(f"\nRetrying failed downloads (Attempt {retries + 1}/{MAX_RETRIES})...")

    # List to keep track of successful downloads in this round
    successful_this_round = []

    for v in failed_downloads[:]:
        print(f"{v['Date']}\t{v['Likes']}\t{v['Location']}", end='')
        u = v['Link']
        o = f"{OUT}/{v['Date']} - {v['Likes']} Likes.mp4"

        success = False
        try:
            with requests.get(u, stream=True, timeout=TIMEOUT) as r:
                r.raise_for_status()  # Will raise HTTPError for bad status codes
                with open(o, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print("\t\tOK")
            success = True

        except requests.exceptions.RequestException as e:
            print(f"\t\tERROR - {u}")
            print(f"Error details: {e}")

        if success:
            successful_this_round.append(v)

        # Add a small sleep between retries to avoid overloading the server
        time.sleep(TTL)

    # Remove successful downloads from failed_downloads
    for v in successful_this_round:
        failed_downloads.remove(v)

    retries += 1

# Final summary
if failed_downloads:
    print("\nSome downloads failed after multiple attempts:")
    for v in failed_downloads:
        print(f"{v['Date']}\t{v['Likes']}\t{v['Location']}")
else:
    print("\nAll downloads were successful.")
