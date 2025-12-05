# score_cv.py (Phiên bản FIX Lỗi Gợi Ý Lặp Lại và Tinh Chỉnh Chấm Điểm)

import re

# --- TỪ KHÓA CHẤM ĐIỂM ---

# Danh sách Action Verb mạnh mẽ (Max 15đ) - Đã mở rộng cả tiếng Anh và Việt
ACTION_VERBS = [
    "developed", "managed", "led", "created", "implemented", "achieved", 
    "designed", "analyzed", "optimized", "initiated", "directed", "improved",
    "collaborated", "defined", "executed", "pioneered", "resolved", "spearheaded",
    "xây dựng", "quản lý", "lãnh đạo", "thiết kế", "phân tích", "tối ưu", "thực hiện", 
    "triển khai", "đạt được", "khởi xướng", "cải tiến", "hợp tác"
]

# Danh sách Kỹ năng & Từ khóa chính (Max 25đ) - Đã mở rộng
SKILL_KEYWORDS = [
    "python", "java", "javascript", "c++", "c#", "php", "go", "swift", "kotlin", "ruby",
    "html", "css", "react", "angular", "vue", "typescript", "frontend", "ui/ux", 
    "backend", "node.js", "express", "django", "flask", "spring", "sql", "mysql", 
    "postgresql", "mongodb", "database", "docker", "kubernetes", "aws", "azure", "gcp", 
    "cloud", "terraform", "ansible", "devops", "git", "ci/cd", "machine learning", 
    "deep learning", "ai", "data science", "nlp", "tableau", "power bi", "r", "spark",
    "communication", "leadership", "agile", "scrum", "problem solving", "critical thinking", 
    "kỹ năng giao tiếp", "lãnh đạo nhóm", "tư duy phản biện", "giải quyết vấn đề", 
    "làm việc nhóm", "cơ sở dữ liệu", "điện toán đám mây", "excel", "word", "powerpoint",
    "jira", "confluence", "trello", "asana", "salesforce", "marketing", "finance", 
    "tài chính", "kế toán", "bán hàng", "sales", "hr", "nhân sự", "tuyển dụng"
]

# --- HÀM TRÍCH XUẤT THÔNG TIN CÁ NHÂN ---
def extract_personal_info(text):
    info = {}
    
    # 1. Email
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', text)
    info['email'] = email_match.group(0) if email_match else 'Không tìm thấy'

    # 2. Phone 
    phone_match = re.search(
        r'(\+?84|0|\(0\))[\s\.\-]?\d{1,4}[\s\.\-]?\d{2,4}[\s\.\-]?\d{2,4}[\s\.\-]?\d{2,4}', 
        text
    )
    if phone_match:
        full_match = phone_match.group(0)
        digits_and_plus = re.sub(r'[^\d+]', '', full_match) 
        digits_count = len(re.sub(r'[^\d]', '', digits_and_plus))
        info['phone'] = digits_and_plus if 9 <= digits_count <= 11 else 'Không tìm thấy'
    else:
        info['phone'] = 'Không tìm thấy'
    
    # 3. Tên (Giữ đơn giản)
    info['name'] = 'Chưa xác định'
    return info

# --- HÀM TẠO GỢI Ý CHUYÊN SÂU (ĐÃ FIX LỖI LẶP LẠI VÀ TĂNG ĐỘ CHÍNH XÁC) ---
def generate_suggestions(result):
    """
    Tạo ra các gợi ý chi tiết dựa trên kết quả tính điểm và lỗi (nếu có).
    Đảm bảo gợi ý thay đổi linh hoạt theo từng CV.
    """
    suggestions = {
        "skills": [], "experience": [], "structure_style": [], "final_review": []
    }
    
    # Lấy các biến từ kết quả
    text = result['raw_text'].lower()
    word_count = result.get('word_count', 0)
    total_score = result.get('total_score', 0)
    current_skills_count = len(result.get('skills_found', []))
    exp_years = result.get('experience_years', 0)
    action_verb_score = result.get('verb_score', 0)
    
    # === KIỂM TRA LỖI TRÍCH XUẤT/VĂN BẢN RỖNG ===
    # Kiểm tra nếu text quá ngắn hoặc chứa cờ lỗi trích xuất
    if word_count < 50 or "[EXTRACT_ERROR" in result.get('raw_text', ''):
        suggestions['final_review'].append("🚨 **LỖI TRÍCH XUẤT/CV QUÁ NGẮN:** Hệ thống không trích xuất được đủ văn bản thô để chấm điểm chính xác.")
        suggestions['final_review'].append("💡 **Giải pháp:** Vui lòng chuyển đổi CV sang định dạng **PDF thuần văn bản** hoặc đảm bảo **OCR** đã được cấu hình đúng nếu đó là file ảnh.")
        return suggestions
    # ==================================

    # 1. Gợi ý KỸ NĂNG & TỪ KHÓA
    if current_skills_count < 5:
        suggestions['skills'].append(f"❌ **Thiếu Kỹ năng Cốt lõi:** CV chỉ tìm thấy {current_skills_count} kỹ năng quan trọng. Hãy bổ sung thêm các kỹ năng chuyên môn và công cụ (tools) liên quan trực tiếp đến JD.")
    elif current_skills_count < 10:
        suggestions['skills'].append(f"🔍 **Cần đa dạng hóa:** Có {current_skills_count} kỹ năng được tìm thấy. Hãy phân loại chúng thành Kỹ năng cứng, Kỹ năng mềm, và Công cụ.")
    else:
         suggestions['skills'].append("✅ **Kỹ năng đa dạng:** Số lượng kỹ năng đủ mạnh để vượt qua hệ thống lọc ATS cơ bản.")


    target_keywords = ["python", "java", "sql", "marketing", "finance"]
    keyword_count = sum(text.count(kw) for kw in target_keywords)
    keyword_density = (keyword_count / word_count) * 100 if word_count > 0 else 0
    if keyword_density < 0.5 and word_count > 100:
        suggestions['skills'].append(f"⚠️ **Mật độ Từ khóa Thấp ({keyword_density:.2f}%):** Cần nhắc lại các kỹ năng chính một cách tự nhiên trong mô tả công việc.")
    
    # 2. Gợi ý KINH NGHIỆM & TÍNH HÀNH ĐỘNG
    if exp_years == 0:
        suggestions['experience'].append("📈 **Cần kinh nghiệm/dự án:** Kinh nghiệm làm việc chưa được tìm thấy. Hãy thêm các dự án cá nhân, đồ án, hoặc các hoạt động tình nguyện.")
    elif exp_years < 3:
        suggestions['experience'].append(f"🚀 **Chi tiết hóa thành tựu:** Với {exp_years} năm kinh nghiệm, hãy mở rộng phần mô tả công việc bằng các **số liệu định lượng** (ví dụ: 'Giảm 15% lỗi', 'Quản lý dự án với ngân sách 50 triệu').")
        
    if action_verb_score < 7:
        suggestions['experience'].append(f"🗣️ **Cần Action Verb (Điểm hành động thấp):** Hãy bắt đầu các gạch đầu dòng mô tả kinh nghiệm bằng các **Action Verb** mạnh mẽ (Ví dụ: *Developed, Managed, Led* thay vì *Was responsible for*).")
    else:
        suggestions['experience'].append("✅ **Tính hành động mạnh mẽ:** Mô tả kinh nghiệm đã sử dụng tốt các động từ hành động.")
    
    
    # 3. Gợi ý CẤU TRÚC, ĐỊNH DẠNG & MỤC TIÊU
    is_summary_found = re.search(r'objective|mục tiêu|summary|tóm tắt', text[:1500])
    is_core_sections_found = re.search(r'experience|kinh nghiệm', text) and re.search(r'education|học vấn', text)
    has_contact_info = (result['info'].get('email') != 'Không tìm thấy' and result['info'].get('phone') != 'Không tìm thấy')

    if not is_summary_found:
        suggestions['structure_style'].append("🎯 **Thiếu Mục tiêu/Tóm tắt:** Hãy thêm một đoạn **tóm tắt ngắn (Summary/Objective)** ở đầu CV để thu hút sự chú ý của nhà tuyển dụng.")
        
    if not is_core_sections_found:
        suggestions['structure_style'].append("⚠️ **Thiếu Mục Chính:** CV cần có các mục rõ ràng như **Kinh nghiệm** và **Học vấn**.")
        
    if word_count > 700:
         suggestions['structure_style'].append(f"📄 **Cấu trúc quá dài ({word_count} từ):** CV nên được giữ trong 1-2 trang.")
         
    if not has_contact_info:
        suggestions['structure_style'].append("❌ **Thiếu Thông tin Liên hệ:** Email hoặc Số điện thoại chưa được tìm thấy. Đảm bảo chúng được đặt ở vị trí dễ nhìn.")

    # 4. Nhận xét Chung
    if total_score < 55:
        suggestions['final_review'].append(f"🚨 **Cần Đại tu (Tổng điểm {total_score}/100):** Điểm thấp cho thấy CV chưa đáp ứng được các tiêu chí cơ bản. Tập trung vào việc thêm các **Action Verb** và **Kỹ năng**.")
    elif total_score < 75:
        suggestions['final_review'].append(f"👌 **Tốt, cần tối ưu (Tổng điểm {total_score}/100):** CV đã ở mức trung bình khá. Hãy áp dụng các gợi ý chi tiết ở trên, đặc biệt là phần **Định lượng Thành tựu**.")
    else:
        suggestions['final_review'].append(f"👍 **Sẵn sàng (Tổng điểm {total_score}/100):** CV đã đáp ứng tốt các tiêu chí và có tính cạnh tranh cao. Hãy kiểm tra các chi tiết nhỏ để đạt điểm tuyệt đối.")

    return suggestions

# --- HÀM TÍNH ĐIỂM CHÍNH (ĐÃ TINH CHỈNH CÔNG THỨC) ---
def score_cv(text, filename="Unknown"):
    
    # === XỬ LÝ LỖI KHỞI TẠO VÀ VĂN BẢN RỖNG ===
    if not text.strip() or "[EXTRACT_ERROR" in text:
        # Nếu trích xuất thất bại hoặc text rỗng, trả về 0 điểm và cờ lỗi
        result = {
            "filename": filename, "total_score": 0, "word_count": 0, "experience_years": 0, 
            "action_verb_count": 0, "word_score": 0, "skill_score": 0, "exp_score": 0, 
            "verb_score": 0, "structure_score": 0, "skills_found": [], 
            "info": extract_personal_info(text), "raw_text": text, "error": 'Trích xuất thất bại'
        }
        result['suggestions'] = generate_suggestions(result)
        return result
    # ===============================================

    # 1. CHUẨN HÓA VĂN BẢN
    text_lower = text.lower()
    cleaned_text = re.sub(r'[\r\n\t\f\v]+', ' ', text_lower) 
    cleaned_text = re.sub(r'[^a-z0-9\sáàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ\/\-\.\#]+', ' ', cleaned_text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    words = cleaned_text.split()
    word_count = len(words)
    
    # 1. Độ dài (Max 20đ) - Tối ưu hóa điểm giữa 300-500 từ
    if word_count < 300:
        word_score = word_count * 0.05
    elif word_count < 500:
        word_score = 15 + (word_count - 300) * 0.025
    else:
        word_score = 20 - (word_count - 500) * 0.01 
    word_score = max(0, min(word_score, 20))
    
    # 2. Kỹ năng chính (Max 25đ) - Tăng trọng số điểm cho mỗi skill
    skills_found = []
    skill_match_count = 0
    for skill in SKILL_KEYWORDS:
        # Sử dụng re.search với r'\b' để đảm bảo khớp từ nguyên vẹn
        if re.search(r'\b' + re.escape(skill) + r'\b', cleaned_text):
            skills_found.append(skill)
            skill_match_count += 1
            
    skill_score = min(skill_match_count * 2.5, 25) # Mỗi skill cho 2.5 điểm
    
    # 3. Kinh nghiệm làm việc (Max 30đ)
    years_match = re.findall(r'(\d+)\s*(years|year|yrs|nam|năm)', text_lower)
    exp_years = max([int(y[0]) for y in years_match], default=0)
    exp_score = min(exp_years * 7, 30) # Mỗi năm kinh nghiệm cho 7 điểm (Max 4.3 năm)
    
    # 4. Tính Hành động (Max 15đ) - Sử dụng tần suất Action Verb
    action_verb_count = 0
    for verb in ACTION_VERBS:
        action_verb_count += cleaned_text.count(verb)
        
    verb_score = min(action_verb_count * 1, 15) # Mỗi Action Verb cho 1 điểm
    
    # 5. Cấu trúc & Định dạng (Max 10đ) - Bổ sung check Contact Info
    structure_score = 0
    
    # Check Mục tiêu/Tóm tắt (+4đ)
    if re.search(r'objective|mục tiêu|summary|tóm tắt', cleaned_text[:1500]):
        structure_score += 4
        
    # Check Kinh nghiệm & Học vấn (+3đ)
    if re.search(r'experience|kinh nghiệm', cleaned_text) and re.search(r'education|học vấn', cleaned_text):
        structure_score += 3
        
    # Check Thông tin liên hệ (+3đ)
    extracted_info = extract_personal_info(text)
    if extracted_info.get('email') != 'Không tìm thấy' and extracted_info.get('phone') != 'Không tìm thấy':
        structure_score += 3
        
    structure_score = min(structure_score, 10)

    # 6. Tính Tổng Điểm
    total_score = round(word_score + skill_score + exp_score + verb_score + structure_score)

    result = {
        "filename": filename,
        "word_count": word_count, "word_score": round(word_score, 2),
        "skills_found": list(set(skills_found)), 
        "skill_score": skill_score,
        "experience_years": exp_years, "exp_score": exp_score,
        "action_verb_count": action_verb_count, "verb_score": verb_score,
        "structure_score": structure_score,
        "total_score": total_score,
        "info": extracted_info,
        "raw_text": text,
        "error": None
    }
    
    result['suggestions'] = generate_suggestions(result) 
    return result