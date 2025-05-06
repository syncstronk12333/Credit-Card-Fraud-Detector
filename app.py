import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from geopy.distance import geodesic

#checks if the card is used in relatively distant places in short period of time meaning impossible travel speed.

def detect_large_travel_distance(df, threshold_km=500):
    grouped = df.groupby("Card_Number")
    fraud_flags = {}
    
    for _, transactions in grouped:
        transactions = transactions.sort_values("Timestamp")
        for i in range(len(transactions) - 1):
            coord1 = (transactions.iloc[i]["Latitude"], transactions.iloc[i]["Longitude"])
            coord2 = (transactions.iloc[i + 1]["Latitude"], transactions.iloc[i + 1]["Longitude"])
            distance = geodesic(coord1, coord2).km
            time_diff = (transactions.iloc[i + 1]["Timestamp"] - transactions.iloc[i]["Timestamp"]).total_seconds() / 3600
            if time_diff > 0 and distance / time_diff > threshold_km:
                fraud_flags[transactions.iloc[i + 1]["Transaction_ID"]] = "Unrealistic travel distance"
    
    return fraud_flags

#checks if there are three rapid transaction within a span of 300 seconds or 5 minutes

def detect_rapid_transactions(df):
    grouped = df.groupby("Card_Number")
    fraud_flags = {}
    for _, transactions in grouped:
        transactions = transactions.sort_values("Timestamp").reset_index()
        for i in range(len(transactions) - 2):
            time_diff = (transactions.loc[i + 2, "Timestamp"] - transactions.loc[i, "Timestamp"]).total_seconds()
            if time_diff < 300:
                fraud_flags[transactions.loc[i + 2, "Transaction_ID"]] = "Rapid consecutive transactions"
    
    return fraud_flags

#card used in a new country all of a sudden could mean it might be compromised so it is flagged false.

def detect_new_country_usage(df):
    fraud_flags = {}
    grouped = df.sort_values("Timestamp").groupby("Card_Number")
    
    for card_number, transactions in grouped:
        seen_countries = set()
        for _, row in transactions.iterrows():
            country = row["Country"]
            tx_id = row["Transaction_ID"]
            if country not in seen_countries:
                seen_countries.add(country)
            else:
                continue
            if len(seen_countries) > 1:
                fraud_flags[tx_id] = "Transaction in new/unusual country"
    
    return fraud_flags

#Any transaction between 12AM and 5AM are flagged suspicious as they are very odd hours for trasnactions to take place

def detect_odd_hours(df):
    fraud_flags = {}
    for _, row in df[df["Timestamp"].dt.hour.between(0, 5)].iterrows():
        fraud_flags[row["Transaction_ID"]] = "Unusual transaction time"
    return fraud_flags

#transactions above 10,000 INR are flagged suspicous

def detect_high_value(df, threshold=10000):
    fraud_flags = {}
    for _, row in df[df["Amount"] > threshold].iterrows():
        fraud_flags[row["Transaction_ID"]] = "High-value transaction"
    return fraud_flags

#devices which are not "iPhone 13" (user's device) are flagged false

def detect_suspicious_devices(df):
    fraud_flags = {}
    for _, row in df[df["Device_ID"] != "iPhone 13"].iterrows():
        fraud_flags[row["Transaction_ID"]] = "Used suspicious device ID"
    return fraud_flags

#any amount value that is outside lower and upper bounds are deemed supsicious

def detect_iqr_outliers(df):
    Q1, Q3 = np.percentile(df["Amount"], [25, 75])
    IQR = Q3 - Q1
    lower_bound, upper_bound = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
    fraud_flags = {}
    for _, row in df[(df["Amount"] < lower_bound) | (df["Amount"] > upper_bound)].iterrows():
        fraud_flags[row["Transaction_ID"]] = "Not in IQR's range"
    return fraud_flags

#flags transactions which took more than 2 attempts at authentication.

def detect_failed_authentications(df):
    fraud_flags = {}
    for _, row in df[df["Failed_Auth"] > 2].iterrows():
        fraud_flags[row["Transaction_ID"]] = "Multiple failed authentications"
    return fraud_flags


st.title("Credit Card Fraud Detection System")

uploaded_file = st.file_uploader("Please upload your transaction CSV file in .csv format", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, parse_dates=["Timestamp"])

    st.success("File uploaded successfully!!")

    # Run fraud detection
    fraudulent_transactions = {}
    fraudulent_transactions.update(detect_large_travel_distance(df))
    fraudulent_transactions.update(detect_rapid_transactions(df))
    fraudulent_transactions.update(detect_odd_hours(df))
    fraudulent_transactions.update(detect_high_value(df))
    fraudulent_transactions.update(detect_iqr_outliers(df))
    fraudulent_transactions.update(detect_failed_authentications(df))
    fraudulent_transactions.update(detect_new_country_usage(df))
    fraudulent_transactions.update(detect_suspicious_devices(df))


    df["Fraud_Flag"] = df["Transaction_ID"].apply(lambda x: x in fraudulent_transactions)
    df["Fraud_Reason"] = df["Transaction_ID"].map(fraudulent_transactions)

    st.subheader("Detected Fraudulent Transactions are as below:")
    fraud_df = df[df["Fraud_Flag"] == True][["Transaction_ID", "Card_Number", "Amount", "Timestamp", "Fraud_Reason"]]

    st.write(f"Total Fraudulent Transactions Detected: **{len(fraud_df)}**")
    st.dataframe(fraud_df)

    # download the new report

    st.download_button(
        label="Download Fraud Report as CSV file",
        data=fraud_df.to_csv(index=False),
        file_name="fraudReport.csv",
        mime="text/csv"
    )