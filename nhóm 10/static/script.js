function formatVND(n) {
  return n.toLocaleString("vi-VN") + " VNĐ";
}

let currentPlaceFeedback = null;
let currentRating = 5;

// Khởi tạo sao rating
const stars = document.querySelectorAll("#starContainer .fa-star");
stars.forEach(star => {
  star.addEventListener("click", () => {
    currentRating = parseInt(star.getAttribute("data-rating"));
    stars.forEach(s => {
      const r = parseInt(s.getAttribute("data-rating"));
      s.classList.toggle("active", r <= currentRating);
    });
  });
});

// Đóng modal
document.getElementById("closeModalBtn").addEventListener("click", () => {
  document.getElementById("feedbackModal").classList.add("hidden");
});

// Xử lý gửi phản hồi
document.getElementById("btnSubmitFeedback").addEventListener("click", async () => {
  if (!currentPlaceFeedback) return;

  const comment = document.getElementById("feedbackText").value;
  const payload = {
    place_id: currentPlaceFeedback.id,
    place_name: currentPlaceFeedback.name,
    city: currentPlaceFeedback.city,
    rating: currentRating,
    comment: comment
  };

  try {
    const res = await fetch("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    alert("Hệ thống: " + result.message);
    document.getElementById("feedbackModal").classList.add("hidden");
    document.getElementById("feedbackText").value = "";
  } catch (err) {
    alert("Không gửi được phản hồi: " + err);
  }
});

// Chạy thuật toán gợi ý
document.getElementById("btnGoiY").addEventListener("click", async function () {
  const btn = document.getElementById("btnGoiY");
  const emptyState = document.getElementById("emptyState");
  const resultsContainer = document.getElementById("resultsList");
  const statusBadge = document.getElementById("resultCount");
  const logNote = document.getElementById("explainNote");

  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang tính toán ma trận...';

  const payload = {
    city: document.getElementById("selCity").value,
    cat: document.getElementById("selCat").value,
    budget: parseFloat(document.getElementById("inpBudget").value) || 0,
    days: parseFloat(document.getElementById("inpDays").value) || 1,
    season: document.getElementById("selSeason").value
  };

  try {
    const response = await fetch("/api/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await response.json();
    emptyState.classList.add("hidden");
    resultsContainer.classList.remove("hidden");
    resultsContainer.innerHTML = "";

    if (!data.results || data.results.length === 0) {
      resultsContainer.innerHTML = '<div class="empty-state">Không có địa điểm phù hợp trong khu vực này.</div>';
      statusBadge.textContent = "0 Kết quả";
      return;
    }

    statusBadge.textContent = `Trả về ${data.results.length} POI tốt nhất`;

    data.results.forEach((r, idx) => {
      const p = r.place;
      const card = document.createElement("div");
      card.className = "result-item" + (idx === 0 ? " top-rank" : "");

      let tagsHtml = `
        <span class="chip ${p.city === data.user.city ? 'matched' : ''}"><i class="fa-solid fa-location-dot"></i> ${p.city}</span>
        <span class="chip ${p.cat1 === data.user.cat ? 'matched' : ''}"><i class="fa-solid fa-tag"></i> ${p.cat1}${p.cat2 !== 'Không có' ? ' / ' + p.cat2 : ''}</span>
        <span class="chip ${p.season === data.user.season ? 'matched' : ''}"><i class="fa-solid fa-sun"></i> ${p.season}</span>
      `;

      card.innerHTML = `
        <div class="place-info">
          <h3>#${idx + 1}. ${p.name}</h3>
          <div class="place-meta">
            <span><i class="fa-solid fa-ticket"></i> Chi phí: <strong>${formatVND(p.budget)}</strong></span>
            <span><i class="fa-solid fa-clock"></i> Lộ trình: <strong>${p.days} ngày</strong></span>
          </div>
          <div class="tags-list">${tagsHtml}</div>
          <div class="feedback-action">
            <button class="btn-feedback" data-index="${idx}">
              <i class="fa-regular fa-thumbs-up"></i> Đánh giá đề xuất
            </button>
          </div>
        </div>
        <div class="place-score">
          <div class="score-value">${Math.round(r.similarity)}%</div>
          <div class="score-label">Độ tương quan</div>
        </div>
      `;

      // Gắn sự kiện mở popup feedback cho từng địa điểm
      card.querySelector(".btn-feedback").addEventListener("click", () => {
        currentPlaceFeedback = p;
        document.getElementById("feedbackTargetPlace").textContent = `Địa điểm: #${idx + 1}. ${p.name} (${p.city})`;
        document.getElementById("feedbackModal").classList.remove("hidden");
      });

      resultsContainer.appendChild(card);
    });

    logNote.textContent = `Pipeline KNN hoàn tất: Đã trích xuất các POI của [${data.user.city}], chuẩn hóa thuộc tính và xác định 3 tọa độ có khoảng cách cực tiểu.`;

  } catch (error) {
    console.error("Lỗi:", error);
    logNote.textContent = "Lỗi đường truyền hệ thống hoặc không kết nối được tới Flask API.";
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-bolt"></i> Xử lý & Phân tích KNN';
  }
});