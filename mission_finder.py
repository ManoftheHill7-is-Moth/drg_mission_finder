# big thanks to rolfosian for creating https://doublexp.net/
# find their repository here: https://github.com/rolfosian/drgmissions/

import urllib.request, json, os
from datetime import date, datetime, timedelta

DATA_FORMAT = False # uses drg_missions_YYYY.json when False and YYYY-MM-DD.json when True
LOCAL_TIME_ZONE = False # use UTC when False and local time zone when True
BASE_URL = "http://doublexp.net/static/json/bulkmissions"
REMOVE_CHAR = "'[]"
mission = []

# change this function to filter for different missions
def print_whales(data):
    for k, val in data.items():
            # skip invalid entries
            if not isinstance(val, dict) or "Biomes" not in val:
                continue

            if not LOCAL_TIME_ZONE:
                time_zone = k # UTC
            else:
                time_zone = datetime.fromisoformat(k).astimezone(None).isoformat() # convert UTC to local time zone
                
            for biome, missions in val["Biomes"].items():
                if biome not in ["Azure Weald", "Fungus Bogs"]:
                    continue 

                for m in missions:
                    is_match = (
                        #m.get("PrimaryObjective") == "Mining Expedition" and
                        m.get("SecondaryObjective") not in ["Hollomite", "Dystrum"] and
                        "Core Corruption" in m.get("MissionWarnings", []) and
                        m.get("MissionMutator") == "Double XP" and
                        m.get("Complexity") == "3" and # [1-3]
                        m.get("Length") == "3" and # [1-3]
                        "s6" in m.get("included_in") # "s0" is unseasoned and 5, "s1" is 1 and 2, "s3" is 3 and 4     
                    )
                
                    if is_match:
                        mission.append(
                            f"A WHITE WHALE!, {time_zone}, {m['included_in']}, {biome}, "
                            f"{m['PrimaryObjective']}, {m['SecondaryObjective']}, "
                            f"Length {m['Length']}, Complexity {m['Complexity']}, "
                            f"{m.get('MissionWarnings', [])}, {m.get('MissionMutator', [])}, "
                            f"{m['CodeName']}"
                        )

def read_local_file(file_path):
    if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    print(f"Loading '/{file_path}'")
                    
            except Exception as e:
                print(f"Corrupt local file '/{file_path}': {e}")
    else:
        data = None

    return(data)

if not DATA_FORMAT:
    search_year = 2027 # change to select the year to search through
    file_path = f"data/drg_missions_{search_year}.json"

    # fetch from computer
    data = read_local_file(file_path)

    if data:
        print_whales(data)
    else:
        print(f"Missing '/{file_path}'")
        exit()

    matched = f"matched in {search_year}"
else:
    search_days = 2 # change to set how many days into the future to look (0 is today, 1 is tomorrow, etc.)
    start_date = date.today()
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

        # try fetching from computer
        data = read_local_file(file_path)

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

    actual_days = (current_date - start_date).days
    searched = f"({actual_days} day{'s' if actual_days != 1 else ''})"
    matched = f"matched from {start_date} to {current_date - timedelta(days=1)} {searched}"

if not mission:
    print(f"No missions {matched}")
else:
    mission_count = len(mission)  
    mission_message = f"{mission_count} mission{'s' if mission_count != 1 else ''} {matched}"

    # cleans matched mission text before saving
    mission_clean = []
    table = str.maketrans('', '', REMOVE_CHAR)
    mission_clean.append(mission_message)  
    for m in mission:
        m_clean = str(m).translate(table).replace(" ,", '').replace("aB", "a B").strip(", ") # removes "'[]", specific commas and spaces, and adds a space inbetween "ApocaBlooms"
        mission_clean.append(m_clean)
        print(f"{m_clean}")
    print(mission_message)

    # saves matches as text file
    datetimestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_result = f"search_results_{datetimestamp}.txt"
    with open(file_result, 'w') as f:
        f.write("\n".join(mission_clean))
        print(f"Saved match{'es' if mission_count != 1 else ''} to '{file_result}'")
        print("Consider renaming this file to better match its contents")
