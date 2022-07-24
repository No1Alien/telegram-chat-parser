"""
file:         telegram-chat-group-join-parser.py
author:       Artur Rodrigues Rocha Neto
email:        artur.rodrigues26@gmail.com
github:       https://github.com/keizerzilla
created:      23/12/2020
modified:     24/07/2022
modified by:  No1Alien

description:  Script to parse group members join history from telegram chats.
requirements: Python 3.x
"""

import re
import sys
import csv
import json
from datetime import datetime
import pytz

columns = [
           "msg_id",
           "actor",
           "actor_id",
           "date",
           "action",
           "members",
           "hkt",
          ]

null_name_counter = 0

def parse_telegram_to_csv(jdata):
    
    if jdata.get("name") is None:
        global null_name_counter 
        null_name_counter += 1
        chat_name = f"UnnamedChat-{null_name_counter}"
    else:
        chat_name = re.sub(r'[\W_]+', u'', jdata.get("name"), flags=re.UNICODE)
    output_filepath = f"{chat_name}.csv"

    
    with open(output_filepath, "w", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, columns, dialect="unix", quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        
        for message in jdata["messages"]:

            if message["type"] != "service":
                continue

            if (message["action"] != "join_group_by_link") and (message["action"] != "invite_members"):
                continue
            

            msg_id = message["id"]
            actor = message["actor"]
            actor_id = message["actor_id"]
            date = message["date"].replace("T", " ")
            dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            eutz = pytz.timezone("Europe/Berlin")
            eu_dt = eutz.localize(dt, is_dst=None)
            hkt = pytz.timezone("Asia/Hong_Kong")
            hkt_dt = eu_dt.astimezone(hkt)

            action = message["action"]
            if (message["action"] == "invite_members"):
                members = message["members"]
            else:
                members = message["actor"]
            
            row = {
                "msg_id"          : msg_id,
                "actor"           : actor,
                "actor_id"        : actor_id,
                "date"            : date,
                "action"          : action,
                "members"         : members,
                "hkt"             : hkt_dt,
            }
            
            writer.writerow(row)

    print(chat_name, "OK!")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("ERROR: incorrect number of arguments!")
        print("How to use it:")
        print("    python3 telegram-chat-group-join-parser.py <chat_history_json>")
        print("Example:")
        print("    python3 telegram-chat-group-join-parser.py movies_group.json")
        sys.exit()

    backup_filepath = sys.argv[1]
    
    with open(backup_filepath, "r", encoding="utf-8") as input_file:
        contents = input_file.read()
        jdata = json.loads(contents)
        
        if "chats" not in jdata:
            parse_telegram_to_csv(jdata)
        else:
            for chat in jdata["chats"]["list"]:
                parse_telegram_to_csv(chat)
        
