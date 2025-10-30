from flask import Flask, render_template_string, request, jsonify
import requests, json

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Run All APIs</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #f2f4f8; margin: 0; padding: 30px; }
        h1 { color: #222; text-align: center; margin-bottom: 30px; }
        button {
            background: #0078d4;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            display: block;
            margin: 0 auto 30px;
        }
        button:hover { background: #005ea6; }
        .response-container {
            background: white;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            border-radius: 10px;
            margin-bottom: 20px;
            padding: 20px;
        }
        .response-container h2 {
            font-size: 18px;
            margin-bottom: 10px;
            color: #0078d4;
        }
        pre {
            background: #f7f9fc;
            border-radius: 8px;
            padding: 15px;
            overflow-x: auto;
            border: 1px solid #e2e8f0;
        }
        .loading {
            text-align: center;
            font-size: 18px;
            color: #0078d4;
        }
    </style>
    <script>
        async function runAllAPIs() {
            document.getElementById('responses').innerHTML = '<p class="loading">Running all APIs... Please wait ⏳</p>';
            const formData = new FormData();
            formData.append('user', '923431664399');

            const response = await fetch('/run_all', { method: 'POST', body: formData });
            const data = await response.json();

            const container = document.getElementById('responses');
            container.innerHTML = '';
            for (const [key, value] of Object.entries(data)) {
                const div = document.createElement('div');
                div.className = 'response-container';
                div.innerHTML = `<h2>${key}</h2><pre>${JSON.stringify(value, null, 4)}</pre>`;
                container.appendChild(div);
            }
        }
    </script>
</head>
<body>
    <h1>Run All APIs</h1>
    <button onclick="runAllAPIs()">Run All APIs</button>
    <div id="responses"></div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_PAGE)

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

    # --- 2️⃣ RetailerBVSLogin ---
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

    # Common headers
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

        deposit_res = requests.post(deposit_url, headers=common_headers, json=deposit_payload)
        deposit_data = deposit_res.json()
        responses["CashDeposit"] = deposit_data
        transaction_id_deposit = deposit_data.get("TransactionID")
    except Exception as e:
        responses["CashDeposit"] = {"error": str(e)}
        transaction_id_deposit = None

    # --- 4️⃣ CashDepositConfirmation (Run Twice) ---
    try:
        confirmation_url = "https://rgw.8798-f464fa20.eu-de.ri1.apiconnect.appdomain.cloud/tmfb/dev-catalog/BVSCashDeposit/CashDepositBVS/Confirmation"
        confirm_payload = {
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

        res1 = requests.post(confirmation_url, headers=common_headers, json=confirm_payload)
        res2 = requests.post(confirmation_url, headers=common_headers, json=confirm_payload)
        responses["CashDepositConfirmation_Run1"] = res1.json()
        responses["CashDepositConfirmation_Run2"] = res2.json()
    except Exception as e:
        responses["CashDepositConfirmation"] = {"error": str(e)}

    # --- 5️⃣ CashWithdrawalBVS + Confirmation ---
    try:
        withdrawal_url = "https://rgw.8798-f464fa20.eu-de.ri1.apiconnect.appdomain.cloud/tmfb/dev-catalog/BVSCashWithdrawal/CashWithdrawalBVS"
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

        withdrawal_res = requests.post(withdrawal_url, headers=common_headers, json=withdrawal_payload)
        withdrawal_data = withdrawal_res.json()
        responses["CashWithdrawalBVS"] = withdrawal_data
        txn_withdrawal = withdrawal_data.get("TransactionID") or withdrawal_data.get("transactionId") or withdrawal_data.get("TxnId")

        confirm_payload = {
            "TransactionID": txn_withdrawal,
            "TermsAccepted": "true",
            "WithdrawAmount": "10",
            "Longitude": "31.5686808",
            "Latitude": "74.3000874",
            "CustomerCNIC": "6110132583649",
            "CustomerMSISDN": "923376246667",
            "AcquiredAfis": "abcd",
            "FingerNumber": "2",
            "ImageType": "4",
            "BioDeviceName": "test",
            "MPOS": "1111@923355923388"
        }

        confirm_url = "https://rgw.8798-f464fa20.eu-de.ri1.apiconnect.appdomain.cloud/tmfb/dev-catalog/BVSCashWithdrawal/CashWithdrawalBVS/Confirmation"
        confirm_res = requests.post(confirm_url, headers=common_headers, json=confirm_payload)
        responses["CashWithdrawalBVS_Confirmation"] = confirm_res.json()
    except Exception as e:
        responses["CashWithdrawalBVS_Confirmation"] = {"error": str(e)}

    # --- 6️⃣ CNICtoMABVS + Confirmation ---
    try:
        cnic_payload = {
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
        cnic_url = "https://rgw.8798-f464fa20.eu-de.ri1.apiconnect.appdomain.cloud/tmfb/dev-catalog/BVSCNICtoMA/CNICtoMABVS"
        cnic_res = requests.post(cnic_url, headers=common_headers, json=cnic_payload)
        cnic_data = cnic_res.json()
        responses["CNICtoMABVS"] = cnic_data

        txn_cnic = cnic_data.get("TransactionID") or cnic_data.get("transactionId") or cnic_data.get("TxnId")

        confirm_payload = {
            **cnic_payload,
            "TransactionID": txn_cnic,
            "MPOS": "1233@923457685757"
        }
        confirm_url = "https://rgw.8798-f464fa20.eu-de.ri1.apiconnect.appdomain.cloud/tmfb/dev-catalog/BVSCNICtoMA/CNICtoMABVSConfirmation"
        confirm_res = requests.post(confirm_url, headers=common_headers, json=confirm_payload)
        responses["CNICtoMABVS_Confirmation"] = confirm_res.json()
    except Exception as e:
        responses["CNICtoMABVS_Confirmation"] = {"error": str(e)}

    return jsonify(responses)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5080, debug=True)
