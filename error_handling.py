import requests
import urllib.parse

# ─────────────────────────────────────────────────────────────────────────────
#  GraphHopper Pro  |  Lead Developer 2 Branch  —  feature-error-handling
#  Enhancements:
#    1. Detailed HTTP status code error messages (400, 401, 403, 404, 429...)
#    2. Extended vehicle profile list (scooter, hike, mtb, racingbike, truck)
# ─────────────────────────────────────────────────────────────────────────────

# ── Extended Vehicle Profiles ─────────────────────────────────────────────────
VEHICLE_PROFILES = {
    "1":  {"name": "car",        "label": "🚗  Car"},
    "2":  {"name": "bike",       "label": "🚲  Bike"},
    "3":  {"name": "foot",       "label": "🚶  Walking (Foot)"},
    "4":  {"name": "motorcycle", "label": "🏍️   Motorcycle"},
    "5":  {"name": "scooter",    "label": "🛵  Scooter"},
    "6":  {"name": "hike",       "label": "🥾  Hike (Trails)"},
    "7":  {"name": "mtb",        "label": "🚵  Mountain Bike"},
    "8":  {"name": "racingbike", "label": "🏎️   Racing Bike"},
    "9":  {"name": "truck",      "label": "🚚  Truck"},
}


# ── Detailed Error Handler ────────────────────────────────────────────────────
def handle_status_error(status_code, response_json=None):
    """
    Maps specific GraphHopper API HTTP status codes to
    clear, descriptive user-facing error messages.
    """
    error_map = {
        400: "❌ Error 400 — Invalid Route. Please check your locations or vehicle profile.",
        401: "❌ Error 401 — Invalid API Key. Please check your key and try again.",
        403: "❌ Error 403 — Forbidden. Your API plan may not support this vehicle profile.",
        404: "❌ Error 404 — Endpoint Not Found. The API URL may be incorrect.",
        422: "❌ Error 422 — Unprocessable Request. Route could not be computed.",
        429: "❌ Error 429 — Rate Limit Exceeded. Too many requests. Please wait.",
        500: "❌ Error 500 — Internal Server Error. GraphHopper is experiencing issues.",
        503: "❌ Error 503 — Service Unavailable. GraphHopper may be down. Try later.",
    }

    message = error_map.get(status_code, f"❌ Unexpected Error {status_code}.")
    print(message)

    # Also print any extra detail GraphHopper returns in the response body
    if isinstance(response_json, dict):
        api_msg = response_json.get("message", "")
        hints   = response_json.get("hints", [])
        if hints:
            api_msg += " | Hint: " + hints[0].get("message", "")
        if api_msg:
            print(f"   API says: {api_msg}")


# ── Geocoding Function (original, unchanged logic) ────────────────────────────
def geocoding(location, key):
    while location == "":
        location = input("Enter the location again: ")

    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})
    replydata   = requests.get(url)
    json_data   = replydata.json()
    json_status = replydata.status_code

    if json_status == 200:
        lat   = json_data["hits"][0]["point"]["lat"]
        lng   = json_data["hits"][0]["point"]["lng"]
        name  = json_data["hits"][0]["name"]
        value = json_data["hits"][0]["osm_value"]

        country = json_data["hits"][0].get("country", "")
        state   = json_data["hits"][0].get("state", "")

        if len(state) != 0 and len(country) != 0:
            new_loc = name + ", " + state + ", " + country
        elif len(country) != 0:
            new_loc = name + ", " + country
        else:
            new_loc = name

        print("Geocoding API URL for " + new_loc + " (Location Type: " + value + ")\n" + url)
    else:
        lat     = "null"
        lng     = "null"
        new_loc = location

        # ── Enhanced: use detailed error handler for geocoding failures ──
        handle_status_error(json_status, json_data)

    return json_status, lat, lng, new_loc


# ── Vehicle Profile Selector (new) ────────────────────────────────────────────
def select_vehicle():
    """Display the extended profile menu and return the chosen vehicle string."""
    print("\n+++++++++++++++++++++++++++++++++++++++++++++")
    print(" Vehicle Profiles Available on GraphHopper: ")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    for key, val in VEHICLE_PROFILES.items():
        print(f"  ({key}) {val['label']}")
    print("+++++++++++++++++++++++++++++++++++++++++++++")

    while True:
        choice = input("Enter the number of your vehicle profile: ").strip()

        if choice.lower() in ("quit", "q"):
            return "quit"

        if choice in VEHICLE_PROFILES:
            selected = VEHICLE_PROFILES[choice]
            print(f"\n✅ Profile selected: {selected['label']}\n")
            return selected["name"]
        else:
            print("⚠️  Invalid choice. Please enter a number between 1 and 9 (or 'q' to quit).")


# ── Main Program ──────────────────────────────────────────────────────────────
geocode_url = "https://graphhopper.com/api/1/geocode?"
route_url   = "https://graphhopper.com/api/1/route?"
key         = "00c741bf-f30c-48ba-aecb-6c31877b5d39"

while True:
    # ── Step 1: Extended Vehicle Profile Selection ────────────────────────────
    vehicle = select_vehicle()
    if vehicle == "quit":
        break

    # ── Step 2: Get Start Location ────────────────────────────────────────────
    loc1 = input("Starting Location: ")
    if loc1.lower() in ("quit", "q"):
        break
    orig = geocoding(loc1, key)

    # ── Step 3: Get Destination ───────────────────────────────────────────────
    loc2 = input("Destination: ")
    if loc2.lower() in ("quit", "q"):
        break
    dest = geocoding(loc2, key)

    print("=================================================")

    # ── Step 4: Request Route only if both geocodes succeeded ─────────────────
    if orig[0] == 200 and dest[0] == 200:
        op = "&point=" + str(orig[1]) + "%2C" + str(orig[2])
        dp = "&point=" + str(dest[1]) + "%2C" + str(dest[2])
        paths_url  = route_url + urllib.parse.urlencode({"key": key, "vehicle": vehicle}) + op + dp

        response      = requests.get(paths_url)
        paths_status  = response.status_code
        paths_data    = response.json()

        print("Routing API Status: " + str(paths_status) + "\nRouting API URL:\n" + paths_url)
        print("=================================================")
        print("Directions from " + orig[3] + " to " + dest[3] + " by " + vehicle)
        print("=================================================")

        if paths_status == 200:
            miles = (paths_data["paths"][0]["distance"]) / 1000 / 1.61
            km    = (paths_data["paths"][0]["distance"]) / 1000
            sec   = int(paths_data["paths"][0]["time"] / 1000 % 60)
            min   = int(paths_data["paths"][0]["time"] / 1000 / 60 % 60)
            hr    = int(paths_data["paths"][0]["time"] / 1000 / 60 / 60)

            print("Distance Traveled: {0:.1f} miles / {1:.1f} km".format(miles, km))
            print("Trip Duration:     {0:02d}:{1:02d}:{2:02d}".format(hr, min, sec))
            print("=================================================")

            for each in range(len(paths_data["paths"][0]["instructions"])):
                path     = paths_data["paths"][0]["instructions"][each]["text"]
                distance = paths_data["paths"][0]["instructions"][each]["distance"]
                print("{0} ( {1:.1f} km / {2:.1f} miles )".format(path, distance / 1000, distance / 1000 / 1.61))

            print("=============================================")

        else:
            # ── Enhanced: detailed routing error messages ─────────────────
            handle_status_error(paths_status, paths_data)
            print("*************************************************")
