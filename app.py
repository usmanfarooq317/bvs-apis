from flask import Flask, render_template_string, request, redirect, url_for, session
import requests, json

app = Flask(__name__)
app.secret_key = "supersecret"
app.config["SESSION_TYPE"] = "filesystem"

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IBM/RSA BVS-API Dashboard</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f4f7f9;
    color: #333;
    line-height: 1.6;
  }
  .container { max-width: 1000px; margin: 40px auto; padding: 20px; }
  h1, h2, h3 { color: #222; }
  h1 { text-align: center; margin-bottom: 30px; }
  .card {
    background: #fff;
    border-radius: 12px;
    padding: 25px 20px;
    margin-bottom: 25px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    transition: transform 0.2s;
  }
  .card:hover { transform: translateY(-3px); }
  .card h3 { margin-bottom: 15px; }
  label { font-weight: 600; margin-bottom: 5px; display: block; color: #555; }
  input, select, button, textarea {
    width: 100%;
    padding: 12px;
    margin-bottom: 15px;
    border-radius: 8px;
    border: 1px solid #ccc;
    font-size: 14px;
  }
  input:focus, select:focus, textarea:focus { outline: none; border-color: #4a90e2; }
  button {
    background-color: #4a90e2;
    color: white;
    border: none;
    font-weight: 600;
    cursor: pointer;
    transition: 0.2s;
  }
  button:hover { background-color: #357ABD; }

  .response-box {
    background: #f0f4ff;
    padding: 15px;
    border-radius: 10px;
    margin-top: 10px;
    overflow-x: auto;
  }
  .response-box h4 {
    margin-bottom: 8px;
    font-size: 16px;
    color: #222;
  }
  pre {
    font-family: monospace;
    font-size: 13px;
    white-space: pre-wrap;
    word-break: break-word;
    color: #111;
  }

  .loading {
    text-align: center;
    font-size: 18px;
    color: #4a90e2;
    margin-top: 20px;
    font-weight: bold;
  }

  @media (max-width: 600px) {
    .container { padding: 10px; }
  }
</style>
<script>
function showLoading() {
    document.getElementById("loading").style.display = "block";
}
</script>
</head>
<body>
<div class="container">
  <h1>🔐 IBM/RSA API Dashboard</h1>

  <div class="card">
    <h3>Run All APIs</h3>
    <form method="POST" action="/run_all" onsubmit="showLoading()">
      <label for="user">Mobile Number</label>
      <input type="text" id="user" name="user" value="923431664399" readonly>
      <button type="submit">🚀 Run All APIs</button>
    </form>
    <div id="loading" class="loading" style="display:none;">Processing... Please wait ⏳</div>
  </div>

  {% if final_response %}
    {% for api_name, api_resp in final_response.items() %}
    <div class="card">
      <h3>{{ api_name }}</h3>
      <div class="response-box">
        <pre>{{ api_resp | tojson(indent=4) }}</pre>
      </div>
    </div>
    {% endfor %}
  {% endif %}
</div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    final_response = session.pop("final_response", None)
    if final_response:
        try:
            final_response = json.loads(final_response)
        except:
            final_response = {}
    return render_template_string(HTML_PAGE, final_response=final_response)

@app.route("/run_all", methods=["POST"])
def run_all():
    user = request.form.get("user")
    otp = "491765"
    pin = "12121"

    responses = {}
    headers = {
        "Content-Type": "application/json",
        "X-Channel": "bvsgateway",
        "X-IBM-Client-Id": "924726a273f72a75733787680810c4e4",
        "X-IBM-Client-Secret": "7154c95b3351d88cb31302f297eb5a9c"
    }

    # --- 1️⃣ OTP API ---
    try:
        otp_payload = {"MSISDN": user}
        otp_url = "https://rgw.8798-f464fa20.eu-de.ri1.apiconnect.appdomain.cloud/tmfb/dev-catalog/RetailerBVSLogin/OTPGeneration"
        otp_res = requests.post(otp_url, headers=headers, json=otp_payload)
        responses["OTP_API"] = otp_res.json()
    except Exception as e:
        responses["OTP_API"] = {"error": str(e)}

    # --- 2️⃣ RetailerBVSLogin API ---
    try:
        login_payload = {"OTP": otp, "User": f"{user}@1010", "Pin": pin}
        login_url = "https://rgw.8798-f464fa20.eu-de.ri1.apiconnect.appdomain.cloud/tmfb/dev-catalog/RetailerBVSLogin"
        login_res = requests.post(login_url, headers=headers, json=login_payload)
        login_data = login_res.json()
        responses["RetailerBVSLogin"] = login_data

        access_token = login_data.get("AccessToken")
        session_id = login_data.get("SessionID")
    except Exception as e:
        responses["RetailerBVSLogin"] = {"error": str(e)}
        access_token, session_id = None, None

    # ✅ Common headers
    common_headers = {
        **headers,
        "Authorization": f"Bearer {access_token}" if access_token else "",
        "Sessionid": session_id if session_id else "",
        "X-Username": f"{user}@1010",
        "X-Password": pin,
        "MPOS": "1111@923355923388"
    }

    # --- 3️⃣ BVSAccountRegistration OTP (3 runs) ---
    try:
        bvs_otp_url = "https://rgw.8798-f464fa20.eu-de.ri1.apiconnect.appdomain.cloud/tmfb/dev-catalog/BVSAccountRegistration/OTP"
        payload = {
            "TransactionID": "0",
            "Longitude": "31.5686808",
            "Latitude": "74.3000874",
            "CustomerCNIC": "3740567242112",
            "CustomerMSISDN": "923054517876",
            "AcquiredAfis": "abcd",
            "FingerNumber": "2",
            "ImageType": "4",
            "BioDeviceName": ""
        }

        for i in range(1, 4):
            res = requests.post(bvs_otp_url, headers=common_headers, json=payload)
            data = res.json()
            responses[f"BVSAccountRegistration_OTP_Run{i}"] = data
            # Use TransactionID from first run for subsequent runs
            if i == 1:
                payload["TransactionID"] = data.get("TransactionID", "0")
    except Exception as e:
        responses["BVSAccountRegistration_OTP"] = {"error": str(e)}

    # --- 4️⃣ CashDeposit ---
    try:
        deposit_url = "https://rgw.8798-f464fa20.eu-de.ri1.apiconnect.appdomain.cloud/tmfb/dev-catalog/BVSCashDeposit/CashDepositBVS"
        deposit_payload = {
            "DepositAmount": "100",
            "Longitude": "31.5686808",
            "Latitude": "74.3000874",
            "CustomerCNIC": "3740577357058",
            "CustomerMSISDN": "923376246667",
            "AcquiredAfis": "abcd",
            "FingerNumber": "2",
            "ImageType": "4",
            "BioDeviceName": "test",
            "MPOS": "1111@923355923388"
        }
        deposit_res = requests.post(deposit_url, headers=common_headers, json=deposit_payload)
        deposit_data = deposit_res.json()
        responses["CashDeposit"] = deposit_data
        transaction_id_deposit = deposit_data.get("TransactionID")
    except Exception as e:
        responses["CashDeposit"] = {"error": str(e)}
        transaction_id_deposit = None

    # --- 5️⃣ CashDepositConfirmation ---
    try:
        confirmation_url = "https://rgw.8798-f464fa20.eu-de.ri1.apiconnect.appdomain.cloud/tmfb/dev-catalog/BVSCashDeposit/CashDepositBVS/Confirmation"
        confirmation_payload = {
            "TransactionID": transaction_id_deposit,
            "TermsAccepted": "true",
            "DepositAmount": "100",
            "Longitude": "31.5686808",
            "Latitude": "74.3000874",
            "CustomerCNIC": "3740577357058",
            "CustomerMSISDN": "923376246667",
            "AcquiredAfis": "abcd",
            "FingerNumber": "2",
            "ImageType": "4",
            "BioDeviceName": "test",
            "MPOS": "1111@923355923388"
        }
        for i in range(1, 3):
            res = requests.post(confirmation_url, headers=common_headers, json=confirmation_payload)
            responses[f"CashDepositConfirmation_Run{i}"] = res.json()
    except Exception as e:
        responses["CashDepositConfirmation"] = {"error": str(e)}

    # --- 6️⃣ CashWithdrawal + Confirmation ---
    try:
        withdrawal_payload = {
            "WithdrawAmount": "10",
            "Longitude": "31.5686808",
            "Latitude": "74.3000874",
            "CustomerCNIC": "6110132583649",
            "CustomerMSISDN": "923376246667",
            "AcquiredAfis": "abcd",
            "FingerNumber": "2",
            "ImageType": "4",
            "BioDeviceName": "test"
        }
        withdrawal_url = "https://rgw.8798-f464fa20.eu-de.ri1.apiconnect.appdomain.cloud/tmfb/dev-catalog/BVSCashWithdrawal/CashWithdrawalBVS"
        withdrawal_res = requests.post(withdrawal_url, headers=common_headers, json=withdrawal_payload)
        withdrawal_data = withdrawal_res.json()
        responses["CashWithdrawalBVS"] = withdrawal_data
        transaction_id_withdrawal = withdrawal_data.get("TransactionID")
    except Exception as e:
        responses["CashWithdrawalBVS"] = {"error": str(e)}
        transaction_id_withdrawal = None

    try:
        confirmation_payload = {**withdrawal_payload, "TransactionID": transaction_id_withdrawal, "TermsAccepted": "true"}
        confirmation_url = "https://rgw.8798-f464fa20.eu-de.ri1.apiconnect.appdomain.cloud/tmfb/dev-catalog/BVSCashWithdrawal/CashWithdrawalBVS/Confirmation"
        confirmation_res = requests.post(confirmation_url, headers=common_headers, json=confirmation_payload)
        responses["CashWithdrawalBVS_Confirmation"] = confirmation_res.json()
    except Exception as e:
        responses["CashWithdrawalBVS_Confirmation"] = {"error": str(e)}

    # --- 7️⃣ CNICtoMABVS + Confirmation ---
    try:
        cnic_url = "https://rgw.8798-f464fa20.eu-de.ri1.apiconnect.appdomain.cloud/tmfb/dev-catalog/BVSCNICtoMA/CNICtoMABVS"
        payload = {
            "ReceiverAccountNumber": "923345876677",
            "TermsAccepted": "true",
            "DepositAmount": "100",
            "DepositReason": "Education",
            "Longitude": "31.5686808",
            "Latitude": "74.3000874",
            "SenderMSISDN": "923376246667",
            "SenderCNIC": "3740577357007",
            "AcquiredAfis": "test",
            "BioDeviceName": "test",
            "FingerNumber": "1",
            "ImageType": "4"
        }
        res = requests.post(cnic_url, headers=common_headers, json=payload)
        cnic_data = res.json()
        responses["CNICtoMABVS"] = cnic_data
        transaction_id_cnic = cnic_data.get("TransactionID")

        payload["TransactionID"] = transaction_id_cnic
        url_conf = "https://rgw.8798-f464fa20.eu-de.ri1.apiconnect.appdomain.cloud/tmfb/dev-catalog/BVSCNICtoMA/CNICtoMABVSConfirmation"
        res_conf = requests.post(url_conf, headers=common_headers, json=payload)
        responses["CNICtoMABVS_Confirmation"] = res_conf.json()
    except Exception as e:
        responses["CNICtoMABVS"] = {"error": str(e)}
        responses["CNICtoMABVS_Confirmation"] = {"error": str(e)}

    # Store final responses
    session["final_response"] = json.dumps(responses)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5080, debug=True)
