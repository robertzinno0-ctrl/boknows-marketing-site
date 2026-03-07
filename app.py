from flask import Flask, render_template, request, jsonify, redirect
import json, os, datetime, requests, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

GHL_API_KEY = os.environ.get("GHL_API_KEY", "")
GHL_LOCATION_ID = os.environ.get("GHL_LOCATION_ID", "")

SMTP_USER = "boknowsmarketingus@gmail.com"
SMTP_PASS = "dfuu rgsa vmlk fakr"
ALERT_EMAIL = "boknowsmarketingus@gmail.com"

def send_lead_email(data):
    try:
        msg = MIMEMultipart()
        msg["From"]    = SMTP_USER
        msg["To"]      = ALERT_EMAIL
        msg["Subject"] = f"🔥 New Lead — {data.get('service','BKM')} — {data.get('name','')}"
        body = f"""New Lead Received!

Name:    {data.get('name','')}
Phone:   {data.get('phone','')}
Email:   {data.get('email','')}
Company: {data.get('company','')}
Service: {data.get('service','')}
State:   {data.get('state','')} {data.get('zip','')}
Message: {data.get('message','')}
Source:  {data.get('source','')}
Time:    {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p ET')}
"""
        msg.attach(MIMEText(body, "plain"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, ALERT_EMAIL, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Email error: {e}")

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
    send_lead_text(data)
    send_lead_email(data)
    return render_template("thank_you.html", name=data["name"].split()[0])

@app.route("/mortgage-leads")
def mortgage_leads():
    return render_template("mortgage_leads.html")

@app.route("/get-quote")
def mortgage_capture():
    return render_template("mortgage_capture.html")

@app.route("/api/capture_mortgage_lead", methods=["POST"])
def capture_mortgage_lead():
    data = {
        "name":    request.form.get("first_name","") + " " + request.form.get("last_name",""),
        "email":   request.form.get("email",""),
        "phone":   request.form.get("phone",""),
        "state":   request.form.get("state",""),
        "zip":     request.form.get("zip",""),
        "service": "Mortgage Lead",
        "message": f"Goal: {request.form.get('goal','')} | Home Value: {request.form.get('home_value','')} | Credit: {request.form.get('credit','')} | State: {request.form.get('state','')} {request.form.get('zip','')}",
        "source":  "Mortgage Capture Page",
        "company": "",
    }
    save_lead(data)
    push_to_ghl(data)
    send_lead_text(data)
    send_lead_email(data)
    return jsonify({"success": True})

@app.route("/api/mortgage_lead_inquiry", methods=["POST"])
def mortgage_lead_inquiry():
    data = {
        "name":          request.form.get("first_name","") + " " + request.form.get("last_name",""),
        "email":         request.form.get("email",""),
        "phone":         request.form.get("phone",""),
        "company":       request.form.get("company",""),
        "package":       request.form.get("package",""),
        "target_states": request.form.get("target_states",""),
        "service":       "Mortgage Leads",
        "message":       f"Package: {request.form.get('package','')} | States: {request.form.get('target_states','')}",
    }
    save_lead(data)
    push_to_ghl(data)
    send_lead_text(data)
    send_lead_email(data)
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5051, debug=False)

def send_lead_text(data):
    send_lead_email(data)
    try:
        import sys
        sys.path.insert(0, '/Users/robertzinno/.openclaw/workspace/boknowshouses-leads')
        from twilio_sms import send_sms
        msg = f"🔥 NEW LEAD — Bo Knows Marketing\nName: {data.get('name','')}\nPhone: {data.get('phone','')}\nCompany: {data.get('company','')}\nService: {data.get('service','')}"
        send_sms(msg)
    except Exception as e:
        print(f"SMS error: {e}")
