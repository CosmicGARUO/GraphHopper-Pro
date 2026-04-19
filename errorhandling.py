import requests

# ─────────────────────────────────────────────
#  GraphHopper Pro  |  Lead Developer 2 Branch
#  Feature: Error Handling & Extended Profiles
# ─────────────────────────────────────────────

API_KEY = "YOUR_API_KEY_HERE"
BASE_URL = "https://graphhopper.com/api/1/route"

# ── Extended Vehicle Profile Menu ──────────────────────────────────────────────
VEHICLE_PROFILES = {
    "1": {"name": "car",        "label": "🚗 Car"},
    "2": {"name": "bike",       "label": "🚲 Bike"},
    "3": {"name": "foot",       "label": "🚶 Walking (Foot)"},
    "4": {"name": "motorcycle", "label": "🏍️  Motorcycle"},
    "5": {"name": "scooter",    "label": "🛵 Scooter"},
    "6": {"name": "hike",       "label": "🥾 Hike (Trails)"},
    "7": {"name": "mtb",        "label": "🚵 Mountain Bike"},
    "8": {"name": "racingbike", "label": "🏎️  Racing Bike"},
    "9": {"name": "truck",      "label": "🚚 Truck"},
}


def display_profiles():
    """Print the extended vehicle profile table."""
    print("\n" + "═" * 42)
    print("   SELECT A VEHICLE PROFILE")
    print("═" * 42)
    for key, val in VEHICLE_PROFILES.items():
        print(f"   ({key}) {val['label']}")
    print("═" * 42)


def get_vehicle_profile() -> str:
    """Prompt user to choose a vehicle profile with validation."""
    display_profiles()
    while True:
        choice = input("Enter your choice (1-9): ").strip()
        if choice in VEHICLE_PROFILES:
            selected = VEHICLE_PROFILES[choice]
            print(f"\n✅ Profile selected: {selected['label']}\n")
            return selected["name"]
        else:
            print("⚠️  Invalid choice. Please enter a number between 1 and 9.")


def get_coordinates(location_label: str) -> tuple:
    """
    Ask the user for lat/lon of a location.
    Validates that input is a proper float and not empty/special characters.
    """
    print(f"\n📍 Enter coordinates for: {location_label}")
    while True:
        try:
            lat_input = input("   Latitude  (e.g. 14.6760): ").strip()
            if not lat_input or not all(c in "0123456789.-" for c in lat_input):
                raise ValueError("Contains invalid characters.")
            lat = float(lat_input)

            lon_input = input("   Longitude (e.g. 121.0437): ").strip()
            if not lon_input or not all(c in "0123456789.-" for c in lon_input):
                raise ValueError("Contains invalid characters.")
            lon = float(lon_input)

            if not (-90 <= lat <= 90):
                raise ValueError("Latitude must be between -90 and 90.")
            if not (-180 <= lon <= 180):
                raise ValueError("Longitude must be between -180 and 180.")

            return lat, lon

        except ValueError as e:
            print(f"   ⚠️  Invalid input — {e} Please try again.")


def handle_status_error(status_code: int, response_json: dict):
    """
    ── Enhancement: Detailed HTTP Status Code Handling ──
    Maps specific GraphHopper API error codes to clear user messages.
    """
    error_map = {
        400: "❌ Error 400 — Invalid Route. Please check your coordinates or vehicle profile.",
        401: "❌ Error 401 — Invalid API Key. Please update your API_KEY in the script.",
        403: "❌ Error 403 — Forbidden. Your API plan may not support this vehicle profile.",
        404: "❌ Error 404 — Endpoint Not Found. Check the API URL.",
        422: "❌ Error 422 — Unprocessable Request. The server could not compute a route with these parameters.",
        429: "❌ Error 429 — Rate Limit Exceeded. Too many requests. Please wait and try again.",
        500: "❌ Error 500 — Internal Server Error. GraphHopper service is experiencing issues.",
        503: "❌ Error 503 — Service Unavailable. GraphHopper may be down. Try again later.",
    }

    # Try to extract GraphHopper's own message from response body
    api_message = ""
    if isinstance(response_json, dict):
        api_message = response_json.get("message", "")
        hints = response_json.get("hints", [])
        if hints:
            api_message += " | Hint: " + hints[0].get("message", "")

    user_message = error_map.get(status_code, f"❌ Unexpected Error {status_code}.")
    print(f"\n{user_message}")
    if api_message:
        print(f"   API says: {api_message}")


def get_route(start: tuple, end: tuple, vehicle: str) -> dict | None:
    """
    Call the GraphHopper Routing API and return parsed JSON,
    or None if the request failed.
    """
    params = {
        "point":    [f"{start[0]},{start[1]}", f"{end[0]},{end[1]}"],
        "vehicle":  vehicle,
        "locale":   "en",
        "calc_points": "true",
        "key":      API_KEY,
    }

    print("\n⏳ Fetching route from GraphHopper API...")

    try:
        response = requests.get(BASE_URL, params=params)
        response_json = {}

        # Try to parse JSON even on error responses (GraphHopper sends JSON errors)
        try:
            response_json = response.json()
        except Exception:
            pass

        # ── Detailed Status Code Handling ─────────────────────────────────
        if response.status_code == 200:
            return response_json
        else:
            handle_status_error(response.status_code, response_json)
            return None

    except requests.exceptions.ConnectionError:
        print("❌ Connection Error — No internet connection or GraphHopper is unreachable.")
        return None
    except requests.exceptions.Timeout:
        print("❌ Timeout Error — The request took too long. Please try again.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Unexpected Request Error: {e}")
        return None


def display_results(data: dict, vehicle: str):
    """Parse and display route results cleanly."""
    try:
        paths = data.get("paths", [])
        if not paths:
            print("⚠️  No route paths returned by the API.")
            return

        path      = paths[0]
        distance  = path["distance"] / 1000         # metres → km
        time_ms   = path["time"]                    # milliseconds
        time_min  = time_ms / 60000
        time_h    = int(time_min // 60)
        time_m    = int(time_min % 60)

        print("\n" + "═" * 42)
        print("   🗺️  ROUTE RESULTS")
        print("═" * 42)
        print(f"   Vehicle  : {vehicle.upper()}")
        print(f"   Distance : {distance:.2f} km  ({distance * 0.621371:.2f} miles)")
        print(f"   Duration : {time_h}h {time_m}m")
        print("═" * 42 + "\n")

    except (KeyError, IndexError, TypeError) as e:
        print(f"❌ Failed to parse route data: {e}")


def main():
    print("╔══════════════════════════════════════════╗")
    print("║        GraphHopper Pro  — Route Planner  ║")
    print("║        Lead Developer 2 Branch           ║")
    print("╚══════════════════════════════════════════╝")

    # Step 1 — Choose vehicle profile (extended list)
    vehicle = get_vehicle_profile()

    # Step 2 — Get start and end coordinates
    start = get_coordinates("START point")
    end   = get_coordinates("END point")

    # Step 3 — Call API with detailed error catching
    data = get_route(start, end, vehicle)

    # Step 4 — Display results
    if data:
        display_results(data, vehicle)
    else:
        print("\n🔁 Please fix the error above and run the script again.\n")


if __name__ == "__main__":
    main()
