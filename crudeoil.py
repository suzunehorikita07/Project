# app.py
!pip install streamlit
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import warnings
warnings.filterwarnings("ignore")

# ------------------------
# Load Data
# ------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("crude_oil_with_predictions.xlsx")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# ------------------------
# Features & Target
# ------------------------
target_col = "Country_Spot_Price_USD"
features = [c for c in df.columns if c not in ["Date", target_col]]

# ------------------------
# Sidebar Controls
# ------------------------
st.sidebar.header("⚙ Model Controls")
country = st.sidebar.selectbox("Select Country", df["Country"].unique())
model_type = st.sidebar.radio("Select Model", ["Regression (fundamentals)", "Time-series"])
forecast_months = st.sidebar.slider("Forecast Horizon (Months)", min_value=6, max_value=36, value=24, step=6)

# ------------------------
# Train Models
# ------------------------
def train_regression(data):
    X = data[features]
    y = data[target_col]

    categorical = [col for col in features if df[col].dtype == "object"]
    transformer = ColumnTransformer(
        transformers=[("cat", OneHotEncoder(handle_unknown="ignore"), categorical)],
        remainder="passthrough"
    )
    model = Pipeline(steps=[
        ("transform", transformer),
        ("model", RandomForestRegressor(n_estimators=100, random_state=42))
    ])
    model.fit(X, y)
    return model

def make_lag_features(data, lags=3):
    df_lag = data.copy()
    for lag in range(1, lags+1):
        df_lag[f"lag_{lag}"] = df_lag[target_col].shift(lag)
    return df_lag

def train_timeseries(data):
    df_lag = make_lag_features(data)
    df_lag = df_lag.dropna()
    X = df_lag[[f"lag_{i}" for i in range(1, 4)]]
    y = df_lag[target_col]
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model, df_lag

def forecast_future(data, model, months=24):
    future = []
    last_row = data.iloc[-1].copy()
    lags = [last_row[target_col]] * 3

    for m in range(months):
        X_pred = np.array(lags[-3:]).reshape(1, -1)
        y_pred = model.predict(X_pred)[0]
        next_date = last_row["Date"] + pd.DateOffset(months=m+1)
        future.append({"Date": next_date, "Forecast": y_pred})
