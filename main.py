from pytz import utc
from apscheduler.schedulers.blocking import BlockingScheduler
import requests
import subprocess
import json
import os
from datetime import datetime, timedelta

equake_data = []
equake_id_set = set()

def cleanup():
    now = datetime.now()
    interval = timedelta(hours=48)
    flag = False
    for equake in list(equake_data):
        equake_time = datetime.utcfromtimestamp(equake["properties"]["time"] / 1000)
        equake_id_set.add(equake["id"])
        if now - equake_time > interval:
            equake_data.remove(equake)
            flag = True

    if flag is True:
        save_equake()

    print("save data")
    return False

def read_equake():
    if not os.path.exists("data.txt"):
        return

    flag = False
    with open('data.txt') as f:
        data = json.load(f)
        now = datetime.now()
        interval = timedelta(hours=48)
        for equake in list(data):
            equake_time = datetime.utcfromtimestamp(equake["properties"]["time"] / 1000)
            equake_id_set.add(equake["id"])
            if now - equake_time > interval:
                data.remove(equake)
                flag = True

    if flag is True:
        save_equake()

def save_equake():
    with open('data.txt', "w") as f:
        json.dump(equake_data, f)

def parse_equake(equake):
    equake_id = equake["id"]

    properties = equake["properties"]
    title = properties["title"]
    time = properties["time"] / 1000
    place = properties["place"]
    mag = properties["mag"]
    url = properties["url"]
    alert = properties["alert"]

    geometry = equake["geometry"]["coordinates"]
    longitude = geometry[0]
    latitude = geometry[1]
    depth = geometry[2]

    if mag > 5.5 and equake_id not in equake_id_set:
        equake_id_set.add(equake_id)
        equake_data.append(equake)
        body = \
            "Location: " + str(longitude) + "," + str(latitude) +\
            "\nDepth: " + str(depth) + " Km" +\
            "\nTime: " + datetime.utcfromtimestamp(time).isoformat() +\
            "\nPlace: " + place +\
            "\nAlert: " + alert +\
            "\nDetail: <a href=\"" + url +"\">" + url +"</a>"
        # print(title)
        # print(body)
        subprocess.run(["notify-send", "-u", "critical", "--app-name=Equake",
                        "-i", "earthquake-notification", title, body])
        return True
    return False


def custom_request():
    endtime = datetime.now().isoformat()
    start_time = datetime.now() - timedelta(hours=1)
    start_time = start_time.isoformat()
    minmag = 5.5
    # "alertlevel": "orange"

    params = {
        "format": "geojson",
        "starttime": start_time,
        "endtime": endtime,
        "minmagnitude": minmag,
    }
    try:
        data = requests.get(url="https://earthquake.usgs.gov/fdsnws/event/1/query?", params=params).json()
        flag = False
        for equake in data["features"]:
            if parse_equake(equake):
                flag = True
        if flag:
            save_equake()
        return False
    except requests.exceptions.Timeout:
        # Maybe set up for a retry, or continue in a retry loop
        pass
    except requests.exceptions.TooManyRedirects:
        # Tell the user their URL was bad and try a different one
        pass
    except requests.exceptions.HTTPError as err:
        pass
    except requests.exceptions.RequestException as e:
        pass
    return False

read_equake()
custom_request()
cleanup()

scheduler = BlockingScheduler(timezone=utc)
scheduler.add_job(custom_request, 'interval', seconds=120)
scheduler.add_job(cleanup, 'interval', seconds=86400)
scheduler.start()
