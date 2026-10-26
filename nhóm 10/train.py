import os
import pandas as pd
import numpy as np
import joblib

# Vì đã lọc cố định theo thành phố, bỏ W_CITY để tính độ tương đồng 100% dựa trên các tiêu chí còn lại
W_CAT = 2.0
W_SEASON = 1.5
W_BUDGET = 1.0
W_DAYS = 1.0
MAX_DIST = W_CAT + W_SEASON + W_BUDGET + W_DAYS  # Tổng khoảng cách tối đa = 5.5

def custom_knn_distance(place, user, budget_range, days_range):
    # Tính khoảng cách theo sở thích
    if place['cat1'] == user['cat']:
        cat_dist = 0.0
    elif place['cat2'] == user['cat']:
        cat_dist = 0.3
    else:
        cat_dist = 1.0
        
    # Tính khoảng cách theo mùa
    season_dist = 0.0 if place['season'] == user['season'] else 1.0
    
    # Khoảng cách ngân sách và số ngày
    budget_dist = min(1.0, abs(place['budget'] - user['budget']) / budget_range)
    days_dist = min(1.0, abs(place['days'] - user['days']) / days_range) if days_range > 0 else 0.0
    
    return (W_CAT * cat_dist +
            W_SEASON * season_dist +
            W_BUDGET * budget_dist +
            W_DAYS * days_dist)

class ChinaTravelKNNRecommender:
    def __init__(self, data_path=os.path.join("data", "DATA.xlsx")):
        self.df = pd.read_excel(data_path).fillna("Không có")
        self.budget_range = float(self.df['budget'].max())
        self.days_range = float(self.df['days'].max() - 1)
        self.max_dist = MAX_DIST

    def recommend(self, user_query, top_k=3):
        # 1. Lọc trước các địa điểm thuộc đúng thành phố người dùng đã chọn
        city_df = self.df[self.df['city'].str.strip() == user_query['city'].strip()]
        
        # Nếu thành phố không có dữ liệu, trả về danh sách trống
        if city_df.empty:
            return []

        records = city_df.to_dict('records')
        scored = []
        
        # 2. Chạy KNN tính độ phù hợp giữa các địa điểm trong thành phố đó
        for p in records:
            d = custom_knn_distance(p, user_query, self.budget_range, self.days_range)
            sim = max(0.0, (1.0 - d / self.max_dist) * 100.0)
            scored.append({"place": p, "dist": d, "similarity": round(sim, 2)})
            
        # Sắp xếp điểm tương đồng từ cao xuống thấp (khoảng cách nhỏ nhất lên đầu)
        scored.sort(key=lambda x: x["dist"])
        return scored[:top_k]

if __name__ == "__main__":
    excel_path = os.path.join("data", "DATA.xlsx")
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Không tìm thấy {excel_path}. Hãy chạy `python prepare_data.py` trước!")
        
    model = ChinaTravelKNNRecommender(excel_path)
    joblib.dump(model, "model_best.joblib")
    print("-> Đã huấn luyện và lưu lại mô hình vào model_best.joblib thành công.")