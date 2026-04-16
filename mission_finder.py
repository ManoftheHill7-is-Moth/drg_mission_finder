# big thanks to rolfosian for creating https://doublexp.net/
# find their repository here: https://github.com/rolfosian/drgmissions/

import urllib.request
from datetime import date, timedelta
import json

BASE_URL = "http://doublexp.net/static/json/bulkmissions"
REMOVE_CHAR = "'[]"
mission = []

# change this function to filter for different missions
def print_whales(data):
    for k, v in data.items():
        if type(v) is not dict or "Biomes" not in v.keys():
            continue
        for biome, missions in v["Biomes"].items():
            for m in missions:
                if biome in ["Azure Weald", "Fungus Bogs"]:
                    if m["PrimaryObjective"] == "Mining Expedition":
                        if m["SecondaryObjective"] not in ["Hollomite", "Dystrum"]:
                            if "Lithophage Outbreak" in m.get("MissionWarnings", []):
                                if m.get("MissionMutator", None) == "Double XP":
                                    if m["Complexity"] == "3": # [1-3]
                                        if m["Length"] == "3": # [1-3]                            
                                            if m["included_in"] == "s6": # "s0" is unseasoned and 5, "s1" is 1 and 2, "s3" is 3 and 4 
                                                mission.append(f"A WHITE WHALE!, {k}, {m["included_in"]}, {biome}, {m["PrimaryObjective"]}, {m["SecondaryObjective"]}, Length {m["Length"]}, Complexity {m["Complexity"]}, {m.get("MissionWarnings", [])}, {m.get("MissionMutator", [])}, {m["CodeName"]}")
        
search_days = 2 # change to set how many days into the future to look (0 is today, 1 is tomorrow, etc.)
start_date = date.today() # datetime(2026, 1, 1)
end_date = start_date + timedelta(days=search_days)
current_date = start_date

if search_days < 0:
    print(f"ERROR: search_days != {search_days}! It must be an integer <= 0!") 
    exit()  

if search_days != 1: 
    print(f"Searching {search_days} days in the future for matches...")
else:
    print(f"Searching {search_days} day in the future for matches...") 

while current_date <= end_date:
    date_str = current_date.isoformat() # YYYY-MM-DD
    file_path = f"data/{date_str}.json"
    url = f"{BASE_URL}/{date_str}.json"
    try:
        # attempt to read data file from computer
        with open(file_path, 'r') as f:
                data = json.load(f)
                print(f"Loading '/{file_path}'")
                print_whales(data)
    except FileNotFoundError:
        print(f"Missing '/data/{date_str}.json', grabbing from {url}")
        try:
            # attempt to read data file from http://doublexp.net/static/json/bulkmissions/"date_str".json
            with urllib.request.urlopen(url, timeout=10) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                raw = response.read().decode(charset)
                data = json.loads(raw)
                print_whales(data)

                # save data file to computer
                try:
                    with open(file_path, 'w') as f:
                        json.dump(data, f)
                        print(f"Saving to {file_path}")
                except Exception as e:
                    print(f"ERROR saving to file: ({e})")

        except Exception as e:
            print(f"ERROR fetching from URL: ({e})")
            print(f"Failed to search days {current_date} to {end_date}")
            break
    
    current_date += timedelta(days=1)

matched = f"matched from {start_date} to {current_date - timedelta(days=1)}"
if mission == []:
    print(f"No missions {matched}")
    print(f"No changes to 'search_results.txt'")
    print(f"The next search could save over this file! Rename it or risk it being lost!")
else:
    mission_count = len(mission)
    if mission_count != 1:  
        mission_message = f"{mission_count} missions {matched}"
    else:
        mission_message = f"{mission_count} mission {matched}"     
    print(mission_message)

    # cleans matched mission text before saving
    mission_clean = []
    table = str.maketrans("", "", REMOVE_CHAR)   
    for m in mission:
        m_clean = str(m).translate(table)
        m_cleaner = m_clean.replace(" ,", "") # removes middle space and comma
        m_cleanest = m_cleaner.strip(", ") # removes end comma and space
        mission_clean.append(m_cleanest)
        print(f"{m_cleanest}")
    mission_clean.insert(0, f"{mission_message}")
    
    with open('search_results.txt', 'w') as f:
        json.dump(mission_clean, f, indent=1)
        print(f"Saved matches to 'search_results.txt'")
        print(f"The next search could save over this file! Rename it or risk it being lost!")
