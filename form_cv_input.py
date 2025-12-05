from fpdf import FPDF
import os

# ======== HÀM TẠO PDF HỖ TRỢ TIẾNG VIỆT ========
class PDF(FPDF):
    def header(self):
        self.set_font('NotoSans', '', 16)
        self.cell(0, 10, "CV Cá Nhân", ln=True, align="C")

def create_cv_pdf(name, skills, experience, score, suggestions, out_path):
    pdf = PDF()
    pdf.add_page()

    # 🔹 Thêm font Unicode NotoSans
    pdf.add_font('NotoSans', '', 'NotoSans-Regular.ttf', uni=True)
    pdf.set_font('NotoSans', '', 12)

    pdf.cell(0, 10, f"Họ tên: {name}", ln=True)
    pdf.cell(0, 10, f"Kỹ năng: {skills}", ln=True)
    pdf.cell(0, 10, f"Kinh nghiệm: {experience}", ln=True)
    pdf.ln(10)
    pdf.cell(0, 10, f"Điểm phù hợp CV: {score:.2f}%", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 10, f"Gợi ý cải thiện: {suggestions}")

    pdf.output(out_path, "F")

# ======== HÀM CHẤM ĐIỂM ========
def calculate_score(name, skills, experience):
    base_score = 50
    if len(skills) > 20:
        base_score += 20
    if "Python" in skills or "AI" in skills:
        base_score += 15
    if len(experience.split()) > 10:
        base_score += 15
    return min(base_score, 100)

# ======== HÀM GỢI Ý ========
def generate_suggestions(skills, experience):
    suggestions = []
    if "Python" not in skills:
        suggestions.append("Nên bổ sung kỹ năng Python vì được dùng nhiều trong AI và phân tích dữ liệu.")
    if len(experience.split()) < 10:
        suggestions.append("Mô tả chi tiết hơn kinh nghiệm làm việc để CV nổi bật hơn.")
    if "AI" not in skills and "Machine Learning" not in skills:
        suggestions.append("Thêm kỹ năng AI hoặc Machine Learning nếu bạn muốn ứng tuyển vào vị trí công nghệ.")
    if not suggestions:
        suggestions.append("CV của bạn đã rất tốt! Giữ phong độ này nhé.")
    return " ".join(suggestions)

# ======== CHƯƠNG TRÌNH CHÍNH ========
def main():
    print("=== NHẬP THÔNG TIN CV ===")
    name = input("Họ tên: ")
    skills = input("Kỹ năng: ")
    experience = input("Kinh nghiệm: ")

    score = calculate_score(name, skills, experience)
    suggestions = generate_suggestions(skills, experience)

    out_pdf = os.path.join(os.getcwd(), "cv_input.pdf")
    create_cv_pdf(name, skills, experience, score, suggestions, out_pdf)

    print(f"\n✅ Điểm phù hợp CV: {score:.2f}%")
    print("================================")
    print(f"💡 Gợi ý: {suggestions}")
    print(f"📄 File PDF lưu tại: {out_pdf}")

if __name__ == "__main__":
    main()
