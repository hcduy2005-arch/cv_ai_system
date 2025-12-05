# extract_text.py (Phiên bản FIX lỗi trích xuất đa dạng file với PyMuPDF & OCR Fallback)

import os
import re
import docx2txt
from pdfminer.high_level import extract_text as extract_text_from_pdf
from io import BytesIO

# Thư viện mới để xử lý PDF mạnh mẽ hơn
try:
    import fitz # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    # Nếu PyMuPDF chưa cài đặt, hệ thống vẫn dùng pdfminer
    PYMUPDF_AVAILABLE = False
    
# Thư viện OCR và tiền xử lý ảnh
try:
    import pytesseract
    from PIL import Image, ImageEnhance
    
    # *********** CẤU HÌNH ĐƯỜNG DẪN TESSERACT ***********
    # BẮT BUỘC phải thay thế đường dẫn sau bằng đường dẫn tesseract.exe CHÍNH XÁC trên máy bạn
    TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe' 
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    # ***************************************************
    
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


# --- HÀM TIỀN XỬ LÝ ẢNH ---
def preprocess_image(image_path):
    """
    Tiền xử lý file ảnh cho OCR: chuyển sang ảnh xám, tăng độ tương phản và độ sắc nét.
    """
    try:
        img = Image.open(image_path)
        
        # 1. Chuyển sang ảnh xám (Grayscale)
        img = img.convert('L')
        
        # 2. Tăng độ tương phản (Contrast)
        enhancer_contrast = ImageEnhance.Contrast(img)
        img = enhancer_contrast.enhance(1.8) 
        
        # 3. Tăng độ sắc nét (Sharpness)
        enhancer_sharpness = ImageEnhance.Sharpness(img)
        img = enhancer_sharpness.enhance(1.5) 
        
        # Lưu ảnh tạm thời đã xử lý
        temp_path = image_path.replace(os.path.splitext(image_path)[1], '_temp.png')
        img.save(temp_path)
        return temp_path
        
    except Exception as e:
        print(f"Lỗi khi tiền xử lý ảnh: {e}")
        return image_path


# --- HÀM OCR DỰ PHÒNG (Fallback) ---
def ocr_fallback(filepath):
    """
    Thực hiện OCR trên PDF/DOCX nếu trích xuất văn bản thất bại.
    Chỉ OCR trang đầu tiên để tiết kiệm thời gian.
    """
    if not PYMUPDF_AVAILABLE or not TESSERACT_AVAILABLE:
        return ""

    try:
        doc = fitz.open(filepath)
        page = doc.load_page(0)
        
        # Render trang đầu tiên thành ảnh có độ phân giải cao
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) 
        img_data = pix.tobytes("ppm")
        
        # Đọc ảnh từ bộ nhớ
        img = Image.open(BytesIO(img_data))
        
        # Thực hiện OCR trực tiếp trên ảnh
        text = pytesseract.image_to_string(img, lang='vie+eng')
        return text
        
    except Exception as e:
        print(f"Lỗi OCR Fallback: {e}")
        return ""


# --- HÀM TRÍCH XUẤT CHÍNH (Đã tối ưu hóa) ---
def extract_text_from_file(filepath):
    """
    Trích xuất văn bản thô từ file PDF, DOCX, TXT, và IMAGE với cơ chế dự phòng.
    """
    ext = os.path.splitext(filepath)[1].lower()
    text = ""
    temp_file_to_delete = None
    
    try:
        # 1. Xử lý PDF 
        if ext == '.pdf':
            if PYMUPDF_AVAILABLE:
                try:
                    # Ưu tiên PyMuPDF
                    doc = fitz.open(filepath)
                    for page in doc:
                        text += page.get_text()
                except Exception:
                    # Nếu PyMuPDF lỗi, thử Fallback bằng pdfminer
                    text = extract_text_from_pdf(filepath)
            else:
                # Dùng pdfminer nếu PyMuPDF không có
                text = extract_text_from_pdf(filepath)
                
            # CƠ CHẾ DỰ PHÒNG CHO PDF: Nếu văn bản trích xuất quá ngắn, thử OCR Fallback
            if len(text.strip()) < 100 and TESSERACT_AVAILABLE:
                fallback_text = ocr_fallback(filepath)
                # Chỉ chọn kết quả OCR nếu nó dài hơn đáng kể
                if len(fallback_text.strip()) > len(text.strip()) * 1.5:
                    text = fallback_text 
        
        # 2. Xử lý DOCX/DOC
        elif ext in ['.doc', '.docx']:
            text = docx2txt.process(filepath)
            
            # CƠ CHẾ DỰ PHÒNG CHO DOCX
            if len(text.strip()) < 100 and TESSERACT_AVAILABLE:
                 fallback_text = ocr_fallback(filepath)
                 if len(fallback_text.strip()) > len(text.strip()) * 1.5:
                    text = fallback_text

        # 3. Xử lý TXT
        elif ext == '.txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()

        # 4. Xử lý FILE ẢNH (OCR sau khi tiền xử lý)
        elif ext in ['.png', '.jpg', '.jpeg', '.webp'] and TESSERACT_AVAILABLE:
            processed_filepath = preprocess_image(filepath)
            if processed_filepath != filepath:
                temp_file_to_delete = processed_filepath

            # Sử dụng lang='vie+eng' để tăng cường độ chính xác cho tiếng Việt
            text = pytesseract.image_to_string(Image.open(processed_filepath), lang='vie+eng')
            
        else:
            text = f"[Định dạng {ext} không được hỗ trợ.]"
            
    except Exception as e:
        # Bắt lỗi hệ thống lớn và đặt cờ lỗi
        text = f"[EXTRACT_ERROR: Lỗi hệ thống khi trích xuất: {e}]"


    # Xóa file tạm thời sau khi xử lý OCR
    if temp_file_to_delete and os.path.exists(temp_file_to_delete):
        os.remove(temp_file_to_delete)

    # Chuẩn hóa văn bản đầu ra (loại bỏ khoảng trắng thừa)
    text = re.sub(r'[\r\n\t\f\v]+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Kiểm tra lần cuối: Nếu text rỗng sau chuẩn hóa và không phải lỗi hệ thống
    if not text and not "[EXTRACT_ERROR" in text:
        text = "[EXTRACT_ERROR: Văn bản trích xuất rỗng.]"
        
    return text