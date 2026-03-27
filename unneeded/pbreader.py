
from google.transit import gtfs_realtime_pb2
import urllib.request
import time
URL = "https://bct.tmix.se/gtfs-realtime/vehicleupdates.pb?operatorIds=47"
POLL_SECONDS = 1

while True:
    try:
        feed = gtfs_realtime_pb2.FeedMessage()
        with urllib.request.urlopen(URL, timeout=15) as response:
            feed.ParseFromString(response.read())

        print(f"--- {time.strftime('%Y-%m-%d %H:%M:%S')} | entities: {len(feed.entity)} ---")
        for entity in feed.entity:
            print(entity)
        print()

        time.sleep(POLL_SECONDS)
    except KeyboardInterrupt:
        print("Stopped.")
        break
    except Exception as error:
        print(f"Fetch error: {error}")
        time.sleep(POLL_SECONDS)
