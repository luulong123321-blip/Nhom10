import os
from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
from feedback_store import save_feedback, init_feedback_store
from train import ChinaTravelKNNRecommender

app = Flask(__name__)
init_feedback_store()

MODEL_PATH = "model_best.joblib"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("Chưa tìm thấy model_best.joblib. Hãy chạy python train.py trước!")

model = joblib.load(MODEL_PATH)

@app.route("/")
def index():
    df = model.df
    cities = sorted(list(set(df['city'])))
    cats = sorted(list(set(df['cat1'].tolist() + df['cat2'].tolist()) - {"Không có"}))
    seasons = ["Mùa xuân", "Mùa hè", "Mùa thu", "Mùa đông"]
    return render_template("index.html", cities=cities, categories=cats, seasons=seasons)

@app.route("/api/recommend", methods=["POST"])
def recommend_api():
    data = request.get_json() or {}
    user_query = {
        "city": data.get("city"),
        "cat": data.get("cat"),
        "budget": float(data.get("budget", 0)),
        "days": float(data.get("days", 1)),
        "season": data.get("season")
    }
    # Giới hạn lấy Top 3 địa điểm phù hợp nhất
    results = model.recommend(user_query, top_k=3)
    return jsonify({"results": results, "user": user_query})

@app.route("/api/feedback", methods=["POST"])
def feedback_api():
    fb_data = request.get_json() or {}
    save_feedback(fb_data)
    return jsonify({"status": "success", "message": "Cảm ơn bạn đã phản hồi!"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)