#  💳 Credit Card Fraud Detection System
This Streamlit-based project detects potentially fraudulent credit card transactions based on user-uploaded transaction data. It uses rule-based anomaly detection techniques inspired by real-world financial heuristics.

## 🚀 Features
- Detects **unrealistic travel distance** between consecutive transactions.
- Flags **rapid multiple transactions** in a short span.
- Alerts on **transactions during odd hours** (12 AM – 5 AM).
- Highlights **high-value transactions** exceeding a threshold.
- Identifies **IQR outliers** in transaction amounts.
- Detects use of **unknown/suspicious device IDs**.
- Flags **transactions from unusual countries** for a given card.
- Marks **multiple failed authentication attempts**.

🧪 Detection Logic Summary
| Rule                  | Description                                                        |
|-----------------------|--------------------------------------------------------------------|
| Large Travel Distance | Flags if travel speed between locations implies unrealistic movement. |
| Rapid Transactions    | Flags 3 transactions within 5 minutes.                             |
| Odd Hours             | Flags transactions between 12 AM and 5 AM.                         |
| High-Value            | Flags transactions over ₹10,000.                                   |
| IQR Outliers          | Detects amount values outside interquartile range.                 |
| Suspicious Devices    | Flags non-expected device usage (e.g., not iPhone 13).             |
| New Country           | Flags first transaction from a new country after initial use.      |
| Failed Authentication | Flags transactions with more than 2 failed login attempts.         |

## 📂 How to Use
Clone this repository:

```sql
git clone https://github.com/yourusername/credit-card-fraud-detection.git
cd credit-card-fraud-detection
```

Install required libraries:

```sql
pip install -r requirements.txt
```

Run the app:

```sql
streamlit run app.py
```

Upload your .csv file containing transaction data and review detected fraud.

## 📝 Input File Format
Your CSV should include the following columns:

- Transaction_ID (unique identifier)
- Card_Number
- Amount
- Timestamp (in datetime format)
- Latitude, Longitude
- Country
- Device_ID
- Failed_Auth

## 📦 Output

Upload the dataset and view a table of all suspicious transactions with reasons for flagging.

Download the fraud report as a CSV file.

## 📸 Sample Screenshot

![image](https://github.com/user-attachments/assets/77c17f90-b344-4eed-b5f9-59feb054d046)

