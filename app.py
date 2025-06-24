from flask import Flask, request, jsonify, render_template_string
from google.cloud import bigquery
from google.oauth2 import service_account
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/etc/secrets/gcp_key.json"
app = Flask(name)

# Authenticate with service account
key_path = "/etc/secrets/gcp_key.json"  # secure path on Render
credentials = service_account.Credentials.from_service_account_file("/etc/secrets/gcp_key.json")
client = bigquery.Client(credentials=credentials, project=credentials.project_id)


# HTML form
html_form = """
<!DOCTYPE html>
<html>
<head>
  <title>Heart Disease Prediction</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 600px;
      margin: auto;
      padding: 20px;
      background: #f4f4f4;
    }
    h2 {
      text-align: center;
    }
    form {
      background: white;
      padding: 20px;
      border-radius: 10px;
    }
    label {
      display: block;
      margin-top: 15px;
    }
    input {
      width: 100%;
      padding: 8px;
      margin-top: 5px;
    }
    button {
      margin-top: 20px;
      width: 100%;
      padding: 10px;
      background-color: #007bff;
      color: white;
      border: none;
      border-radius: 5px;
    }
    .result {
      margin-top: 20px;
      font-weight: bold;
      text-align: center;
    }
  </style>
</head>
<body>

<h2>Heart Disease Prediction</h2>

<form id="predictForm">
  <label>Age:</label>
  <input type="number" name="age" required>

  <label>Sex (1 = Male, 0 = Female):</label>
  <input type="number" name="sex" required>

  <label>Chest Pain Type (cp):</label>
  <input type="number" name="cp" required>

  <label>Resting Blood Pressure (trestbps):</label>
  <input type="number" name="trestbps" required>

  <label>Cholesterol (chol):</label>
  <input type="number" name="chol" required>

  <label>Fasting Blood Sugar (fbs):</label>
  <input type="number" name="fbs" required>

  <label>Rest ECG (restecg):</label>
  <input type="number" name="restecg" required>

  <label>Max Heart Rate (thalach):</label>
  <input type="number" name="thalach" required>

  <label>Exercise-Induced Angina (exang):</label>
  <input type="number" name="exang" required>

  <label>Oldpeak (ST Depression):</label>
  <input type="number" step="0.1" name="oldpeak" required>

  <label>Slope:</label>
  <input type="number" name="slope" required>

  <label>CA (Major Vessels Colored):</label>
  <input type="number" name="ca" required>

  <label>Thal:</label>
  <input type="number" name="thal" required>

  <button type="submit">Predict</button>
</form>

<div class="result" id="result"></div>

<script>
document.getElementById("predictForm").addEventListener("submit", async function(event) {
  event.preventDefault();

  const form = event.target;
  const data = {};

  for (const input of form.elements) {
    if (input.name) {
      data[input.name] = parseFloat(input.value);
    }
  }

  const response = await fetch("/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
  });

  const result = await response.json();
  document.getElementById("result").innerText =
    result.predicted_target !== undefined
      ? Prediction: ${result.predicted_target}
      : Error: ${result.error};
});
</script>

</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(html_form)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    query = f"""
    SELECT
      *
    FROM
      ML.PREDICT(
        MODEL assignproject1-463813.heart.heart_disease_model,
        (
          SELECT
            {data['age']} AS age,
            {data['sex']} AS sex,
            {data['cp']} AS cp,
            {data['trestbps']} AS trestbps,
            {data['chol']} AS chol,
            {data['fbs']} AS fbs,
            {data['restecg']} AS restecg,
            {data['thalach']} AS thalach,
            {data['exang']} AS exang,
            {data['oldpeak']} AS oldpeak,
            {data['slope']} AS slope,
            {data['ca']} AS ca,
            {data['thal']} AS thal
        )
    )
    """
    try:
        query_job = client.query(query)
        results = [dict(row) for row in query_job]
        return jsonify(results[0])
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if name == "main":
    app.run(debug=True)