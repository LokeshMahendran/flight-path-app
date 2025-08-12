from flask import Flask, render_template_string, request

app = Flask(__name__)

# HTML Templates as strings
form_html = """
<!DOCTYPE html>
<html>
<head><title>Flight Search</title></head>
<body>
    <h2>Fastest Paths Finder ✈️</h2>
    <form action="/results" method="post">
        From: <input type="text" name="source" required><br><br>
        To: <input type="text" name="destination" required><br><br>
        <button type="submit">Search</button>
    </form>
</body>
</html>
"""

result_html = """
<!DOCTYPE html>
<html>
<head><title>Results</title></head>
<body>
    <h2>Route Results 🚀</h2>
    <p>From: {{ from_city }}</p>
    <p>To: {{ to_city }}</p>

    <h3>Available Travel Options:</h3>
    <table border="1" cellpadding="8">
        <tr><th>Route</th><th>Time</th><th>Cost</th></tr>
        {% for route in routes %}
        <tr>
            <td>{{ route.path }}</td>
            <td>{{ route.time }}</td>
            <td>{{ route.cost }}</td>
        </tr>
        {% endfor %}
    </table>

    <br><a href="/">Search Again</a>
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

    routes = [
        {"path": f"{source} → Dubai → {destination}", "time": "15h", "cost": "₹45,000"},
        {"path": f"{source} → Mumbai → London → {destination}", "time": "18h", "cost": "₹38,000"},
        {"path": f"{source} → Delhi → Paris → {destination}", "time": "20h", "cost": "₹41,000"},
    ]

    return render_template_string(result_html, from_city=source, to_city=destination, routes=routes)

if __name__ == '__main__':
    app.run(debug=True)
