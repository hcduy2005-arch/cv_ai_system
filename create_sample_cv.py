from fpdf import FPDF

text = """Name: Ho Cong Duy
Email: duy@example.com
Phone: 0123456789
Skills: Python, NLP, Machine Learning, Data Analysis
Experience:
- AI Intern at OpenAI
- Data Analyst at Tech Company
Education: University of Technology
"""

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

for line in text.split("\n"):
    pdf.cell(0, 10, txt=line, ln=True)

pdf.output("sample_cv.pdf")

print("✅ sample_cv.pdf created successfully!")
