import requests
import urllib.parse
from tabulate import tabulate  # NEW: UI Enhancement
from colorama import Fore, Style, init  # NEW: UI Enhancement

# Initialize colorama for all platforms
init(autoreset=True)

def geocoding(location, key):
    while location == "":
        location = input(f"{Fore.RED}Location cannot be empty. Enter again: ") 

    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})
    
    try:
        replydata = requests.get(url, timeout=10)
        json_data = replydata.json()
        json_status = replydata.status_code
    except Exception as e:
        print(f"{Fore.RED}Network Error: Could not connect to Geocoding API. ({e})")
        return 500, "null", "null", location

    if json_status == 200 and len(json_data.get("hits", [])) > 0:
        hits = json_data["hits"][0]
        lat, lng = hits["point"]["lat"], hits["point"]["lng"]
        name = hits["name"]
        value = hits.get("osm_value", "unknown")
        country = hits.get("country", "")
        state = hits.get("state", "")

        new_loc = f"{name}, {state}, {country}" if state and country else f"{name}, {country}" if country else name
        
        # UI DESIGNER: Added Cyan highlighting for target locations
        print(f"{Fore.CYAN}Target Found: {Fore.WHITE}{new_loc} ({value})")
        return json_status, lat, lng, new_loc
    else:
        print(f"{Fore.RED}Geocode Error: '{location}' not found.")
        return json_status, "null", "null", location

# Configuration
key = "00c741bf-f30c-48ba-aecb-6c31877b5d39"
route_url = "https://graphhopper.com/api/1/route?" 

while True:
    print(f"\n{Fore.YELLOW}{'='*45}")
    print(f"{Fore.YELLOW}{Style.BRIGHT}   GRAPHHOPPER PRO NAVIGATION SYSTEM")
    print(f"{Fore.YELLOW}{'='*45}")

    unit_choice = input(f"{Fore.WHITE}Select units: (1) Metric/KM or (2) Imperial/Miles (q to quit): ")
    if unit_choice.lower() in ["q", "quit"]: break
    use_miles = True if unit_choice == "2" else False

    print(f"\n{Fore.GREEN}Profiles: car | bike | foot")
    vehicle = input(f"{Fore.WHITE}Enter vehicle profile: ").lower()
    if vehicle in ["q", "quit"]: break
    if vehicle not in ["car", "bike", "foot"]:
        vehicle = "car"
        print(f"{Fore.YELLOW}No valid profile. Defaulting to 'car'.")

    loc1 = input(f"{Fore.WHITE}Starting Location: ")
    if loc1.lower() in ["q", "quit"]: break
    orig = geocoding(loc1, key)
    
    loc2 = input(f"{Fore.WHITE}Destination: ")
    if loc2.lower() in ["q", "quit"]: break
    dest = geocoding(loc2, key)

    if orig[0] == 200 and dest[0] == 200 and orig[1] != "null":
        op, dp = f"&point={orig[1]}%2C{orig[2]}", f"&point={dest[1]}%2C{dest[2]}"
        paths_url = route_url + urllib.parse.urlencode({"key": key, "vehicle": vehicle}) + op + dp 
        
        try:
            response = requests.get(paths_url, timeout=10)
            paths_status, paths_data = response.status_code, response.json()
        except:
            print(f"{Fore.RED}Error: Routing API unreachable.")
            continue

        if paths_status == 200:
            path_info = paths_data["paths"][0]
            distance_km = path_info["distance"] / 1000
            distance_mi = distance_km / 1.61
            sec, mins, hr = int(path_info["time"]/1000%60), int(path_info["time"]/1000/60%60), int(path_info["time"]/1000/60/60)

            # UI DESIGNER: Route Summary Box
            summary_data = [
                ["From", orig[3]], ["To", dest[3]], ["Vehicle", vehicle.upper()],
                ["Distance", f"{distance_mi:.2f} mi" if use_miles else f"{distance_km:.2f} km"],
                ["Duration", f"{hr:02d}h:{mins:02d}m:{sec:02d}s"]
            ]
            print(f"\n{Fore.MAGENTA}ROUTE SUMMARY")
            print(tabulate(summary_data, tablefmt="plain"))

            # UI DESIGNER: Directions Table
            table_rows = []
            for instr in path_info["instructions"]:
                d_km = instr["distance"] / 1000
                d_disp = f"{d_km/1.61:.2f} mi" if use_miles else f"{d_km:.2f} km"
                table_rows.append([instr['text'], d_disp])

            print(f"\n{Fore.GREEN}TURN-BY-TURN DIRECTIONS")
            print(tabulate(table_rows, headers=[f"{Fore.YELLOW}Instruction", f"{Fore.YELLOW}Distance"], tablefmt="fancy_grid"))
        else:
            print(f"{Fore.RED}Routing Error {paths_status}: {paths_data.get('message', 'Check route.')}")
