"""
app.py
ALPHA -- Flask backend: serves the frontend and exposes a /route API
that the voice-controlled frontend calls. Supports routing from the
user's real live GPS location, or from a named starting point.
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from navigation import find_route, find_route_from_coords, find_nearest_landmark, START_POINT
from campus_data import CAMPUS_LOCATIONS

app = Flask(__name__)
CORS(app)


def find_landmarks_in_text(text: str):
    """Returns every known landmark mentioned in the text, in order."""
    text = text.lower()
    matches = []

    for landmark_name in sorted(CAMPUS_LOCATIONS, key=len, reverse=True):
        idx = text.find(landmark_name)
        if idx != -1:
            already_covered = any(landmark_name in existing for existing in matches)
            if not already_covered:
                matches.append(landmark_name)

    return matches


@app.route("/")
def home():
    return render_template("index.html", landmarks=CAMPUS_LOCATIONS)


@app.route("/route", methods=["POST"])
def route():
    data = request.get_json()
    spoken_text = data.get("command", "")
    user_lat = data.get("user_lat")
    user_lon = data.get("user_lon")

    # ---------- Special command: "how far" queries the active trip's distance ----------
    if "how far" in spoken_text.lower():
        return jsonify({
            "special_command": "distance_query",
            "spoken_reply": "__USE_CLIENT_SIDE_DISTANCE__"  # placeholder, replaced on the frontend
        })

    found_landmarks = find_landmarks_in_text(spoken_text)
    gps_available = user_lat is not None and user_lon is not None
    ...

    # ---------- Case 1: GPS is on -- ALWAYS route from the user's real position ----------
    if gps_available:
        if not found_landmarks:
            return jsonify({"error": "Sorry, I didn't recognize that destination."}), 400

        # Even if the user names two locations (e.g. "from X to Y"), GPS
        # always wins as the starting point -- we only use the LAST
        # named landmark as the destination.
        destination = found_landmarks[-1]
        user_coords = (float(user_lat), float(user_lon))

        result = find_route_from_coords(user_coords, destination)
        if "error" in result:
            return jsonify(result), 400

        result["spoken_reply"] = (
            f"ALPHA here. Using your current location. Heading to {destination.title()}. "
            f"It is about {int(result['distance_meters'])} meters away."
        )
        return jsonify(result)

    # ---------- Case 2: no GPS -- fall back to named start/destination ----------
    if len(found_landmarks) >= 2:
        origin, destination = found_landmarks[0], found_landmarks[1]
    elif len(found_landmarks) == 1:
        origin, destination = START_POINT, found_landmarks[0]
    else:
        return jsonify({"error": "Sorry, I didn't recognize that destination."}), 400

    result = find_route(origin, destination)
    if "error" in result:
        return jsonify(result), 400

    result["spoken_reply"] = (
        f"ALPHA here. GPS unavailable — heading from {origin.title()} to {destination.title()}. "
        f"It is about {int(result['distance_meters'])} meters away."
    )
    return jsonify(result)


@app.route("/whereami", methods=["POST"])
def whereami():
    """Tells the user which landmark they're currently closest to."""
    data = request.get_json()
    user_lat = data.get("user_lat")
    user_lon = data.get("user_lon")

    if user_lat is None or user_lon is None:
        return jsonify({"error": "No location provided."}), 400

    nearest_name, distance = find_nearest_landmark((float(user_lat), float(user_lon)))
    return jsonify({
        "nearest_landmark": nearest_name,
        "distance_meters": distance,
        "spoken_reply": f"You are currently about {int(distance)} meters from {nearest_name.title()}."
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)