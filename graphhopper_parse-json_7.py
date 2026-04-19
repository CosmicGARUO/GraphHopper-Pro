import requests
import urllib.parse
# Note: UI Designer will add 'tabulate' and 'colorama' in the next phase

def geocoding(location, key):
    while location == "":
        location = input("Location cannot be empty. Enter the location again: ") 

    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})
    
    # --- LEAD DEV 2: Network Safety ---
    try:
        replydata = requests.get(url, timeout=10)
        json_data = replydata.json()
        json_status = replydata.status_code
    except Exception as e:
        print(f"Network Error: Could not connect to Geocoding API. ({e})")
        return 500, "null", "null", location

    # --- LEAD DEV 2: Validation of Hits ---
    if json_status == 200 and len(json_data.get("hits", [])) > 0:
        hits = json_data["hits"][0]
        lat = hits["point"]["lat"]
        lng = hits["point"]["lng"]
        name = hits["name"]
        value = hits.get("osm_value", "unknown")

        country = hits.get("country", "")
        state = hits.get("state", "")

        if state and country:
            new_loc = f"{name}, {state}, {country}"
        elif country:
            new_loc = f"{name}, {country}"
        else:
            new_loc = name

        print(f"Geocoding API URL for {new_loc} (Type: {value})\n{url}")
        return json_status, lat, lng, new_loc
    else:
        print(f"Geocode Error: '{location}' not found or invalid response. Status: {json_status}")
        return json_status, "null", "null", location

# Configuration
key = "00c741bf-f30c-48ba-aecb-6c31877b5d39"
route_url = "https://graphhopper.com/api/1/route?" 

while True:
    print("\n" + "+" * 45)
    # --- LEAD DEV 1: Unit Preference ---
    unit_choice = input("Select preferred units: (1) Metric/KM or (2) Imperial/Miles (or 'q' to quit): ")
    if unit_choice.lower() in ["q", "quit"]:
        break
    use_miles = True if unit_choice == "2" else False

    print("\nVehicle profiles available: car, bike, foot")
    profile = ["car", "bike", "foot"]
    vehicle = input("Enter a vehicle profile: ").lower()
    
    if vehicle in ["quit", "q"]:
        break
    elif vehicle not in profile:
        vehicle = "car"
        print("No valid profile entered. Defaulting to 'car'.")

    loc1 = input("Starting Location: ")
    if loc1.lower() in ["quit", "q"]: break
    orig = geocoding(loc1, key)
    
    loc2 = input("Destination: ")
    if loc2.lower() in ["quit", "q"]: break
    dest = geocoding(loc2, key)

    print("=" * 50)
    # Ensure both locations were found before attempting route
    if orig[0] == 200 and dest[0] == 200 and orig[1] != "null" and dest[1] != "null":
        op = f"&point={orig[1]}%2C{orig[2]}"
        dp = f"&point={dest[1]}%2C{dest[2]}"
        paths_url = route_url + urllib.parse.urlencode({"key": key, "vehicle": vehicle}) + op + dp 
        
        # --- LEAD DEV 2: Routing Safety ---
        try:
            response = requests.get(paths_url, timeout=10)
            paths_status = response.status_code
            paths_data = response.json()
        except Exception as e:
            print(f"Error: Could not reach Routing API. ({e})")
            continue

        print(f"Routing API Status: {paths_status}\nRouting API URL:\n{paths_url}")
        print("=" * 50)
        print(f"Directions from {orig[3]} to {dest[3]} by {vehicle}")
        print("=" * 50)
        
        if paths_status == 200:
            # --- LEAD DEV 1: Integrated Math ---
            distance_km = paths_data["paths"][0]["distance"] / 1000
            distance_mi = distance_km / 1.61
            
            sec = int(paths_data["paths"][0]["time"] / 1000 % 60)
            mins = int(paths_data["paths"][0]["time"] / 1000 / 60 % 60)
            hr = int(paths_data["paths"][0]["time"] / 1000 / 60 / 60) 

            if use_miles:
                print(f"Total Distance: {distance_mi:.1f} miles")
            else:
                print(f"Total Distance: {distance_km:.1f} km")
                
            print(f"Trip Duration: {hr:02d}:{mins:02d}:{sec:02d}")
            print("=" * 50) 

            # --- LEAD DEV 1: Directions loop with Unit Toggle ---
            for instr in paths_data["paths"][0]["instructions"]:
                dist_km = instr["distance"] / 1000
                if use_miles:
                    dist_display = f"{dist_km / 1.61:.2f} miles"
                else:
                    dist_display = f"{dist_km:.2f} km"
                print(f"{instr['text']} ({dist_display})")
            
            print("=" * 45)
        else:
            # --- LEAD DEV 2: Detailed Error Feedback ---
            msg = paths_data.get("message", "Check points or API limits.")
            print(f"Routing Error {paths_status}: {msg}")
            print("*" * 50)
    else:
        print("Invalid locations. Please check your spelling and try again.")