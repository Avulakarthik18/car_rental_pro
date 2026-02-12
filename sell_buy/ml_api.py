# ============================================
# 🚀 CAR PRICE PREDICTION + SUGGESTION API
# ============================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)

CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True
)

@app.after_request
def after_request(response):

    response.headers.add(
        "Access-Control-Allow-Origin", "*"
    )
    response.headers.add(
        "Access-Control-Allow-Headers",
        "Content-Type,Authorization"
    )
    response.headers.add(
        "Access-Control-Allow-Methods",
        "GET,POST,OPTIONS"
    )

    return response


# ============================================
# 📦 LOAD MODEL + ENCODERS
# ============================================

model = joblib.load("ui_price_model.pkl")
encoders = joblib.load("ui_encoders.pkl")

# Use SAME dataset used in training
df = pd.read_csv("final_car_dataset.csv")


# ============================================
# 🔮 PRICE PREDICTION
# ============================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        data = request.json

        if not data:
            return jsonify({
                "success": False,
                "error": "No data received"
            })

        print("Incoming:", data)

        # Encode safely
        def encode_safe(column, value):

            le = encoders[column]

            if value in le.classes_:
                return le.transform([value])[0]
            else:
                return 0

        company = encode_safe("company", data["company"])
        model_name = encode_safe("model", data["model"])
        fuel = encode_safe("fuel", data["fuel"])
        transmission = encode_safe("transmission", data["transmission"])
        owner = encode_safe("ownerType", data["ownerType"])

        features = np.array([[

            company,
            model_name,
            int(data["year"]),
            int(data["km"]),
            fuel,
            transmission,
            owner

        ]])

        price = model.predict(features)[0]

        return jsonify({
            "success": True,
            "price": int(price)
        })

    except Exception as e:

        print("Prediction Error:", e)

        return jsonify({
            "success": False,
            "error": str(e)
        })


# ============================================
# 🔎 COMPANY SUGGESTIONS
# ============================================

@app.route("/companies", methods=["GET"])
def companies():

    try:

        company_list = sorted(
            df["company"]
            .dropna()
            .unique()
            .tolist()
        )

        return jsonify(company_list)

    except:
        return jsonify([])


# ============================================
# 🔎 MODEL SUGGESTIONS
# ============================================

@app.route("/models/<company>", methods=["GET"])
def models(company):

    try:

        model_list = sorted(

            df[
                df["company"].str.lower() ==
                company.lower()
            ]["model"]
            .dropna()
            .unique()
            .tolist()

        )

        return jsonify(model_list)

    except:
        return jsonify([])


# ============================================
# ▶ RUN SERVER
# ============================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5002,
        debug=True
    )
