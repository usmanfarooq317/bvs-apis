from flask import Flask, render_template_string, request, redirect, url_for, session
import requests, json

app = Flask(__name__)
app.secret_key = "supersecret"
app.config["SESSION_TYPE"] = "filesystem"

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Run All APIs</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f3f3f3; padding: 20px; }
        h1 { color: #333; }
        textarea { width: 100%; height: 500px; font-family: monospace; font-size: 14px; }
        button { background: #007bff; color: white; border: none; padding: 10px 20px;
                 border-radius: 6px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        input { padding: 8px; font-size: 16px; width: 300px; }
        label { font-weight: bold; }
    </style>
</head>
<body>
    <h1>Run All APIs</h1>
    <form method="POST" action="/run_all">
        <label>Mobile Number:</label>
        <input type="text" name="user" value="923431664399" readonly /><br><br>
        <button type="submit">Run All APIs</button>
    </form>

    {% if final_response %}
    <h2>API Responses</h2>
    <textarea readonly>{{ final_response }}</textarea>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    final_response = session.pop("final_response", None)
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
        otp_res = requests.post(otp_url, headers=headers, data=json.dumps(otp_payload))
        responses["OTP_API"] = otp_res.json()
    except Exception as e:
        responses["OTP_API"] = {"error": str(e)}

    # --- 2️⃣ RetailerBVSLogin API ---
    try:
        login_payload = {"OTP": otp, "User": f"{user}@1010", "Pin": pin}
        login_url = "https://rgw.8798-f464fa20.eu-de.ri1.apiconnect.appdomain.cloud/tmfb/dev-catalog/RetailerBVSLogin"
        login_res = requests.post(login_url, headers=headers, data=json.dumps(login_payload))
        login_data = login_res.json()
        responses["RetailerBVSLogin"] = login_data

        access_token = login_data.get("AccessToken")
        session_id = login_data.get("SessionID")
    except Exception as e:
        responses["RetailerBVSLogin"] = {"error": str(e)}
        access_token, session_id = None, None

    # ✅ Common headers (with AccessToken & SessionID)
    common_headers = {
        **headers,
        "Authorization": f"Bearer {access_token}",
        "Sessionid": session_id,
        "X-Username": f"{user}@1010",
        "X-Password": pin,
        "MPOS": "1111@923355923388"
    }

    # --- 3️⃣ CashDeposit ---
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

        # ✅ Use valid common headers (includes token/sessionid)
        deposit_res = requests.post(deposit_url, headers=common_headers, json=deposit_payload)
        deposit_data = deposit_res.json()
        responses["CashDeposit"] = deposit_data
        transaction_id = deposit_data.get("TransactionID")
    except Exception as e:
        responses["CashDeposit"] = {"error": str(e)}
        transaction_id = None

    # --- 4️⃣ CashDepositConfirmation (Run 2 Times) ---
    try:
        confirmation_url = "https://rgw.8798-f464fa20.eu-de.ri1.apiconnect.appdomain.cloud/tmfb/dev-catalog/BVSCashDeposit/CashDepositBVS/Confirmation"
        confirmation_payload = {
            "TransactionID": transaction_id,
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

        # ✅ Use same authorized headers
        confirm_res_1 = requests.post(confirmation_url, headers=common_headers, json=confirmation_payload)
        confirm_res_2 = requests.post(confirmation_url, headers=common_headers, json=confirmation_payload)

        responses["CashDepositConfirmation_Run1"] = confirm_res_1.json()
        responses["CashDepositConfirmation_Run2"] = confirm_res_2.json()
    except Exception as e:
        responses["CashDepositConfirmation"] = {"error": str(e)}

    # --- 5️⃣ CashWithdrawalBVS API ---
    try:
        payload = {
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
        url = "https://rgw.8798-f464fa20.eu-de.ri1.apiconnect.appdomain.cloud/tmfb/dev-catalog/BVSCashWithdrawal/CashWithdrawalBVS"
        res = requests.post(url, headers=common_headers, data=json.dumps(payload))
        responses["CashWithdrawalBVS"] = res.json()
    except Exception as e:
        responses["CashWithdrawalBVS"] = {"error": str(e)}

    # --- 6️⃣ CashWithdrawalBVS Confirmation ---
    try:
        payload = {
            "TransactionID": "134914",
            "TermsAccepted": "true",
            "WithdrawAmount": "100",
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
        url = "https://rgw.8798-f464fa20.eu-de.ri1.apiconnect.appdomain.cloud/tmfb/dev-catalog/BVSCashWithdrawal/CashWithdrawalBVS/Confirmation"
        res = requests.post(url, headers=common_headers, data=json.dumps(payload))
        responses["CashWithdrawalBVS_Confirmation"] = res.json()
    except Exception as e:
        responses["CashWithdrawalBVS_Confirmation"] = {"error": str(e)}

    # --- 7️⃣ CNICtoMABVS API ---
    try:
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
        url = "https://rgw.8798-f464fa20.eu-de.ri1.apiconnect.appdomain.cloud/tmfb/dev-catalog/BVSCNICtoMA/CNICtoMABVS"
        res = requests.post(url, headers=common_headers, data=json.dumps(payload))
        responses["CNICtoMABVS"] = res.json()
    except Exception as e:
        responses["CNICtoMABVS"] = {"error": str(e)}

    # --- 8️⃣ CNICtoMABVS Confirmation ---
    try:
        payload = {
            "ReceiverAccountNumber": "923345876677",
            "TransactionID": "147441",
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
            "MPOS": "1233@923457685757",
            "ImageType": "4"
        }
        url = "https://rgw.8798-f464fa20.eu-de.ri1.apiconnect.appdomain.cloud/tmfb/dev-catalog/BVSCNICtoMA/CNICtoMABVSConfirmation"
        res = requests.post(url, headers=common_headers, data=json.dumps(payload))
        responses["CNICtoMABVS_Confirmation"] = res.json()
    except Exception as e:
        responses["CNICtoMABVS_Confirmation"] = {"error": str(e)}

    session["final_response"] = json.dumps(responses, indent=4)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5080, debug=True)
