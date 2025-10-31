# 🧩 Run All APIs - Flask Project

This project is a **Flask-based automation tool** that runs a series of APIs sequentially (OTP, Login, Cash Deposit, Withdrawal, and CNIC transfers).  
It displays **each API response beautifully formatted** in the browser when you click the **"Run All APIs"** button.

---

## 🚀 Features

✅ Single-click to run **all APIs sequentially**  
✅ Fetches OTP, Login, and uses **AccessToken + SessionID dynamically**  
✅ Reuses generated tokens automatically for dependent APIs  
✅ Executes **Cash Deposit Confirmation** twice with the same input  
✅ Automatically passes **TransactionID** between API calls  
✅ Beautiful, modern, responsive UI with box-styled API responses  
✅ Flask backend with built-in API chaining logic  

---

## 🧠 API Flow

1. **OTP API** → Generates OTP for user  
2. **RetailerBVSLogin** → Logs in and returns `AccessToken` + `SessionID`  
3. **CashDeposit** → Performs a deposit transaction  
4. **CashDepositConfirmation** → Runs **twice** using the same transaction ID  
5. **CashWithdrawalBVS** → Executes withdrawal and stores transaction ID  
6. **CashWithdrawalBVS_Confirmation** → Confirms the withdrawal  
7. **CNICtoMABVS** → Performs CNIC to MA transfer  
8. **CNICtoMABVS_Confirmation** → Confirms the CNIC to MA transaction  

---

## 🧩 Project Structure

📦 flask-run-all-apis
├── app.py # Main Flask application
├── README.md # Project documentation
└── requirements.txt # Python dependencies (optional)

yaml


---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/flask-run-all-apis.git
cd flask-run-all-apis

3️⃣ Install Dependencies

pip install flask requests

4️⃣ Run the Flask App

python app.py
🌐 Access the Application
Once running, open your browser and go to:
👉 http://localhost:5080

You’ll see a button labeled "Run All APIs" — click it to start the process.
Each API’s response will appear in a neatly formatted container.

🧾 Example Output
Each API response is displayed as:

lua

+-----------------------------+
|         OTP_API             |
|-----------------------------|
| { "Response": "OTP Sent" }  |
+-----------------------------+

+-----------------------------+
|    RetailerBVSLogin         |
|-----------------------------|
| { "AccessToken": "...",     |
|   "SessionID": "..." }      |
+-----------------------------+
⚠️ Notes
Each run will generate a new AccessToken and SessionID automatically.

Tokens are reused for all APIs that require authentication.

Cash Deposit Confirmation runs two times automatically.

Ensure your API URLs and credentials (like Client ID/Secret) are correct.

🧑‍💻 Tech Stack
Backend: Flask (Python)

HTTP Requests: Requests Library

Frontend: Vanilla JS + HTML + CSS

API Display: JSON pretty print inside HTML containers