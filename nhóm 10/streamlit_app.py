import streamlit as st
import joblib
import pandas as pd

# Cấu hình tiêu đề trang web
st.set_page_config(page_title="Hệ thống Gợi ý", page_icon="🎯", layout="centered")

st.title("🎯 Hệ thống Gợi ý Thông minh")
st.write("Nhập thông tin bên dưới để nhận kết quả phù hợp nhất:")

# Nạp mô hình hoặc dữ liệu
@st.cache_resource
def load_model():
    return joblib.load("model_best.joblib")

model = load_model()

# Tạo các ô nhập liệu / dropdown trực quan
city = st.selectbox("Chọn thành phố mong muốn:", ["Bắc Kinh", "Thượng Hải", "Thành Đô"])
days = st.slider("Số ngày dự kiến:", min_value=1, max_value=30, value=3)
budget = st.number_input("Ngân sách dự kiến (VND):", min_value=1000000, step=500000)

# Xử lý sự kiện bấm nút
if st.button("Xem Gợi ý"):
    st.success("Đang xử lý kết quả cho bạn...")
    # Gọi hàm dự đoán từ mô hình của bạn
    # results = model.recommend(...)
    st.write(f"Kết quả phân tích cho hành trình **{days} ngày** tại **{city}**:")
    st.info("Địa điểm phù hợp nhất: Gợi ý 1, Gợi ý 2...")