from flask import Flask, render_template_string, request
import os
from dotenv import load_dotenv
import requests

# Load API credentials from .env file
load_dotenv()
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")

app = Flask(__name__)

# Get access token
def get_amadeus_access_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_API_KEY,
        "client_secret": AMADEUS_API_SECRET
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json().get("access_token")

# Get flight offers
def get_flight_offers(token, origin, destination):
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {
        "originLocationCode": origin.upper(),
        "destinationLocationCode": destination.upper(),
        "departureDate": "2025-08-30",
        "adults": 1,
        "max": 3
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print("❌ Amadeus error:", response.text)
        return []

    data = response.json().get("data", [])
    routes = []

    for offer in data:
        itinerary = offer["itineraries"][0]
        duration = itinerary["duration"]
        price = offer["price"]["total"]
        segments = itinerary["segments"]
        path = " → ".join([seg["departure"]["iataCode"] for seg in segments] + [segments[-1]["arrival"]["iataCode"]])

        routes.append({
            "path": path,
            "time": duration.replace("PT", "").lower(),
            "cost": f"€{price}"
        })

    return routes

# Clean HTML templates
form_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Flight Search</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 40px; }
        input, button { padding: 10px; margin: 10px; font-size: 16px; }
    </style>
</head>
<body>
    <h2>Fastest Paths Finder</h2>
    <form action="/results" method="post">
        From (IATA code): <input type="text" name="source" required><br>
        To (IATA code): <input type="text" name="destination" required><br>
        <button type="submit">Search</button>
    </form>
</body>
</html>
"""

result_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Flight Results</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 40px; }
        table { margin: auto; border-collapse: collapse; }
        th, td { border: 1px solid #999; padding: 10px 20px; }
        a { display: inline-block; margin-top: 20px; text-decoration: none; color: #0066cc; }
    </style>
</head>
<body>
    <h2>Route Results</h2>
    <p><strong>From:</strong> {{ from_city }}</p>
    <p><strong>To:</strong> {{ to_city }}</p>

    {% if routes %}
    <h3>Available Travel Options:</h3>
    <table>
        <tr><th>Route</th><th>Time</th><th>Cost</th></tr>
        {% for route in routes %}
        <tr>
            <td>{{ route.path }}</td>
            <td>{{ route.time }}</td>
            <td>{{ route.cost }}</td>
        </tr> 
        {% endfor %}
    </table>
    {% else %}
    <p><strong>No routes found or an error occurred.</strong></p>
    {% endif %}

    <a href="/">Search Again</a>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(form_html)

@app.route('/results', methods=['POST'])
def results():
    source = request.form['source']
    destination = request.form['destination']
    token = get_amadeus_access_token()
    routes = get_flight_offers(token, source, destination)

    return render_template_string(result_html, from_city=source, to_city=destination, routes=routes)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
