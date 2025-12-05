from flask import Flask, render_template, request, redirect, url_for
import os
import json
from werkzeug.utils import secure_filename
from datetime import datetime

# Import các module custom
from score_cv import score_cv 
from extract_text import extract_text_from_file 
from score_cv import generate_suggestions # Import hàm gợi ý để dùng khi có lỗi trích xuất

app = Flask(__name__)

# Cấu hình thư mục và loại file cho phép
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# File lưu trữ lịch sử
HISTORY_FILE = 'history.json'

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    """Kiểm tra phần mở rộng của file có hợp lệ không."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_history():
    """Tải toàn bộ lịch sử đánh giá từ history.json."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return [] 
    return []

def save_history(history):
    """Lưu lịch sử đánh giá vào history.json."""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    """Trang chủ hiển thị form upload và lịch sử đánh giá."""
    history = load_history()
    # Sắp xếp theo điểm tổng giảm dần cho bảng xếp hạng
    cv_list_sorted = sorted(history, key=lambda x: x.get('total_score', 0), reverse=True)
    
    # Lấy kết quả gần nhất cho mục "Kết quả gần nhất"
    latest_result = cv_list_sorted[0] if cv_list_sorted else None
    
    return render_template('index.html', latest_result=latest_result, cv_list=cv_list_sorted)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Xử lý việc tải lên file CV, tính điểm và lưu vào lịch sử."""
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    
    if file.filename == '' or not allowed_file(file.filename):
        return redirect(url_for('index'))
        
    filename = secure_filename(file.filename)
    # Tạo tên file duy nhất để tránh xung đột
    unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(filepath)
    
    # --- CƠ CHẾ BẮT LỖI MỀM KHI TRÍCH XUẤT (QUAN TRỌNG) ---
    try:
        text = extract_text_from_file(filepath)
    except Exception as e:
        app.logger.error(f"Lỗi trích xuất văn bản: {e}")
        # Gắn cờ lỗi rõ ràng vào văn bản thô để score_cv nhận diện
        text = f"[EXTRACT_ERROR: Lỗi trích xuất không xác định {e}]" 
    # --------------------------------------------------------

    # Gọi hàm tính điểm hoàn chỉnh (sẽ tự động xử lý cờ lỗi [EXTRACT_ERROR] trong text)
    result = score_cv(text, unique_filename)
    
    result['original_filename'] = filename # Lưu tên gốc
    result['filepath'] = filepath # Lưu đường dẫn file 

    # Cập nhật và lưu lịch sử
    history = load_history()
    history.append(result)
    save_history(history)

    # Chuyển hướng đến trang chi tiết của CV vừa upload
    return redirect(url_for('view_cv_detail', filename=unique_filename))

@app.route('/detail/<filename>')
def view_cv_detail(filename):
    """Hiển thị trang chi tiết kết quả đánh giá CV dựa trên tên file."""
    history = load_history()
    result = next((cv for cv in history if cv['filename'] == filename), None)
    
    if result is None:
        return render_template('index.html', latest_result=None, cv_list=load_history()) 
        
    return render_template('view_cv_detail.html', result=result)

@app.route('/delete/<filename>', methods=['POST'])
def delete_cv(filename):
    """Xóa CV khỏi lịch sử và file khỏi thư mục uploads."""
    history = load_history()
    
    # 1. Tìm và xóa kết quả khỏi lịch sử
    initial_len = len(history)
    cv_to_delete = next((cv for cv in history if cv['filename'] == filename), None)
    history = [cv for cv in history if cv['filename'] != filename]
    
    if len(history) < initial_len:
        save_history(history)
        # 2. Xóa file vật lý
        if cv_to_delete and 'filepath' in cv_to_delete:
            filepath = cv_to_delete['filepath']
            if os.path.exists(filepath):
                os.remove(filepath)
            
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Lưu ý: Cần đảm bảo tất cả các file khác (score_cv.py, extract_text.py, templates/*.html) 
    # đã được cập nhật phiên bản mới nhất trước khi chạy app.py
    app.run(debug=True)