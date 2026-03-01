from flask import Flask, render_template, request, jsonify, redirect
import json, os, datetime, requests
GHL_API_KEY = os.environ.get("GHL_API_KEY", "")
GHL_LOCATION_ID = os.environ.get("GHL_LOCATION_ID", "")

app = Flask(__name__)

LEADS_FILE = os.path.join(os.path.dirname(__file__), "data", "leads.json")
os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)

def save_lead(data):
    leads = []
    if os.path.exists(LEADS_FILE):
        with open(LEADS_FILE) as f:
            leads = json.load(f)
    data["submitted_at"] = datetime.datetime.now().isoformat()
    leads.append(data)
    with open(LEADS_FILE, "w") as f:
        json.dump(leads, f, indent=2)

def push_to_ghl(data):
    try:
        headers = {"Authorization": f"Bearer {GHL_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "firstName":   data.get("name", "").split()[0],
            "lastName":    " ".join(data.get("name", "").split()[1:]),
            "email":       data.get("email", ""),
            "phone":       data.get("phone", ""),
            "locationId":  GHL_LOCATION_ID,
            "tags":        ["Bo Knows Marketing", "Website Lead", data.get("service", "General")],
            "customField": [{"key": "company", "field_value": data.get("company", "")}],
            "source":      "Bo Knows Marketing Website",
        }
        r = requests.post("https://rest.gohighlevel.com/v1/contacts/", headers=headers, json=payload, timeout=10)
        return r.status_code == 200
    except:
        return False

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/industries")
def industries():
    return render_template("industries.html")

@app.route("/pricing")
def pricing():
    return render_template("pricing.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/ai")
def ai_services():
    return render_template("ai_services.html")

@app.route("/ai-demo")
def ai_demo():
    return render_template("ai_demo.html")

@app.route("/submit", methods=["POST"])
def submit():
    data = {
        "name":    request.form.get("name", ""),
        "email":   request.form.get("email", ""),
        "phone":   request.form.get("phone", ""),
        "company": request.form.get("company", ""),
        "service": request.form.get("service", ""),
        "message": request.form.get("message", ""),
    }
    save_lead(data)
    push_to_ghl(data)
    return render_template("thank_you.html", name=data["name"].split()[0])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5051, debug=False)
