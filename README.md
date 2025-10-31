# 🧩 Run All APIs - Flask Project

This project is a **Flask-based automation tool** that runs a series of APIs sequentially (OTP, Login, BVSAccountRegistration OTP, Cash Deposit, Withdrawal, and CNIC transfers).  
It displays **each API response beautifully formatted** in the browser when you click the **"Run All APIs"** button.

---

## 🚀 Features

✅ Single-click to run **all APIs sequentially**  
✅ Fetches OTP, Login, and uses **AccessToken + SessionID dynamically**  
✅ Reuses generated tokens automatically for dependent APIs  
✅ Executes **Cash Deposit Confirmation** twice with the same input  
✅ Automatically passes **TransactionID** between API calls  
✅ Runs **BVSAccountRegistration OTP** three times with correct transaction ID chaining  
✅ Beautiful, modern, responsive UI with box-styled API responses  
✅ Flask backend with built-in API chaining logic  

---

## 🧠 API Flow

1. **OTP API** → Generates OTP for user  
2. **RetailerBVSLogin** → Logs in and returns `AccessToken` + `SessionID`  
3. **BVSAccountRegistration OTP** → Runs three times sequentially using transaction ID from first run  
4. **CashDeposit** → Performs a deposit transaction  
5. **CashDepositConfirmation** → Runs **twice** using the same transaction ID  
6. **CashWithdrawalBVS** → Executes withdrawal and stores transaction ID  
7. **CashWithdrawalBVS_Confirmation** → Confirms the withdrawal  
8. **CNICtoMABVS** → Performs CNIC to MA transfer  
9. **CNICtoMABVS_Confirmation** → Confirms the CNIC to MA transaction  

---

## 🧩 Project Structure

📦 flask-run-all-apis  
├── app.py # Main Flask application  
├── README.md # Project documentation  
├── requirements.txt # Python dependencies  
├── Dockerfile # Docker image definition  
└── docker-compose.yml # Docker Compose setup  

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/usmanfarooq317/bvs-apis.git
cd bvs-apis
2️⃣ Install Dependencies
bash
 code
pip install flask requests
3️⃣ Run the Flask App
bash

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

+-----------------------------+
| BVSAccountRegistration OTP  |
|-----------------------------|
| { "TransactionID": "148879",|
|   "ResponseCode": "100" }   |
+-----------------------------+
⚠️ Notes
Each run generates a new AccessToken and SessionID automatically.

Tokens are reused for all APIs that require authentication.

Cash Deposit Confirmation runs two times automatically.

BVSAccountRegistration OTP runs three times sequentially using the transaction ID from the first run.

Ensure your API URLs and credentials (Client ID/Secret, username/password) are correct.

🧑‍💻 Tech Stack
Backend: Flask (Python)

HTTP Requests: Requests Library

Frontend: Vanilla JS + HTML + CSS

API Display: JSON pretty print inside HTML containers

🐳 Docker Setup
1️⃣ Build Docker Image
bash

docker build -t bvs-api-dashboard .
2️⃣ Run Container
bash

docker run -p 5080:5080 bvs-api-dashboard
3️⃣ Using Docker Compose
bash

docker-compose up --build