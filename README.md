# 1) Cài thư viện
pip install -r requirements.txt

# 2) chạy server
uvicorn app.main:app --reload

# 3) seed admin (tùy chọn)
python -m app.seed

# 4) mở docs
#   http://localhost:8000/docs
#   Authorize -> nhập: Bearer <access_token>