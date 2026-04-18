# big thanks to rolfosian for creating https://doublexp.net/
# find their repository here: https://github.com/rolfosian/drgmissions/

import urllib.request, json, os
from datetime import date, timedelta

BASE_URL = "http://doublexp.net/static/json/bulkmissions"
REMOVE_CHAR = "'[]"
mission = []

# change this function to filter for different missions
def print_whales(data):
    for k, val in data.items():
            # skip invalid entries
            if not isinstance(val, dict) or "Biomes" not in val:
                continue
                
            for biome, missions in val["Biomes"].items():
                if biome not in ["Azure Weald", "Fungus Bogs"]:
                    continue 

                for m in missions:
                    is_match = (
                        m.get("PrimaryObjective") == "Mining Expedition" and
                        m.get("SecondaryObjective") not in ["Hollomite", "Dystrum"] and
                        "Lithophage Outbreak" in m.get("MissionWarnings", []) and
                        m.get("MissionMutator") == "Double XP" and
                        m.get("Complexity") == "3" and # [1-3]
                        m.get("Length") == "3" and # [1-3]
                        "s6" in m.get("included_in") # "s0" is unseasoned and 5, "s1" is 1 and 2, "s3" is 3 and 4     
                    )
                
                if is_match:
                    mission.append(
                        f"A WHITE WHALE!, {k}, {m['included_in']}, {biome}, "
                        f"{m['PrimaryObjective']}, {m['SecondaryObjective']}, "
                        f"Length {m['Length']}, Complexity {m['Complexity']}, "
                        f"{m.get('MissionWarnings', [])}, {m.get('MissionMutator', [])}, "
                        f"{m['CodeName']}"
                    )

search_days = 2 # change to set how many days into the future to look (0 is today, 1 is tomorrow, etc.)
start_date = date.today() # datetime(2026, 1, 1)
end_date = start_date + timedelta(days=search_days)
current_date = start_date

if search_days < 0:
    print(f"ERROR: search_days {search_days}! It must be an integer >= 0!") 
    exit() 

print(f"Searching {search_days} day{'s' if search_days != 1 else ''} in the future for matches...")

while current_date <= end_date:
    date_str = current_date.isoformat() # YYYY-MM-DD
    file_path = f"data/{date_str}.json"
    url = f"{BASE_URL}/{date_str}.json"
    data = None

    # try fetching from computer
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                print(f"Loading '/{file_path}'")
                
        except Exception as e:
            print(f"Corrupt local file '/{file_path}': {e}")

    # try fetching from http://doublexp.net/static/json/bulkmissions/"date_str".json
    if data is None:
        print(f"Missing '/{file_path}', fetching from {url}")
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                raw = response.read().decode(response.headers.get_content_charset() or "utf-8")
                data = json.loads(raw)
            
            # save to computer
            os.makedirs("data", exist_ok=True) # ensure folder exists
            with open(file_path, 'w') as f:
                json.dump(data, f)
                print(f"Saving '/{file_path}'")
                
        except Exception as e:
            print(f"STOPPING: Could not fetch {date_str}.json. Error: {e}")
            print(f"Failed to search days {current_date} to {end_date}")
            break

    if data:
        print_whales(data)

    current_date += timedelta(days=1)

matched = f"matched from {start_date} to {current_date - timedelta(days=1)}"
if not mission:
    print(f"No missions {matched}")
    print(f"No changes to 'search_results.txt'")
else:
    mission_count = len(mission)  
    mission_message = f"{mission_count} mission{'s' if mission_count != 1 else ''} {matched}"
    print(mission_message)

    # cleans matched mission text before saving
    mission_clean = []
    table = str.maketrans('', '', REMOVE_CHAR)   
    for m in mission:
        m_clean = str(m).translate(table).replace(" ,", '').strip(", ") # removes '[] and specific commas and spaces
        mission_clean.append(m_clean)
        print(f"{m_clean}")
    mission_clean.append(mission_message)
    
    with open("search_results.txt", 'w') as f:
        f.write("\n".join(mission_clean))
        print(f"Saved matches to 'search_results.txt'")
print(f"The next search could save over this file! Rename it or risk it being lost!")
