import re

# Chuỗi mẫu
chuoi_bao_cao = """
Phần I
I. Tổng quan
1. Trồng trọt
Trong tháng, các địa phương phía Bắc tiến hành thu hoạch cây vụ Đông, chuẩn bị đất gieo trồng hoa màu vụ Đông Xuân và gieo trồng lúa Đông Xuân trà sớm; 
2. Chăn nuôi
Chăn nuôi gia súc, gia cầm cơ bản kiểm soát tốt dịch bệnh cả trước và trong Tết
II. Kết quả
III. Kế hoạch
"""

# Tình huống 1: Chỉ lấy theo mục số La Mã
muc_so_la_ma = re.findall(r'^I\. [A-Z][^.]*$', chuoi_bao_cao, re.MULTILINE)
print("Tình huống 1:", muc_so_la_ma)

# Tình huống 2: Chỉ lấy theo mục số
muc_so_thuong = re.findall(r'^[0-9]+\.\s*[A-Za-z\s]+', chuoi_bao_cao, re.MULTILINE)
print("Tình huống 2:", muc_so_thuong)

# Tình huống 3: Theo 2 mục: số La Mã và số thường
muc_so_la_ma_va_thuong = re.findall(r'^I\. [A-Z][^.]*$|[0-9]+\.\s*[A-Za-z\s]+', chuoi_bao_cao, re.MULTILINE)
print("Tình huống 3:", muc_so_la_ma_va_thuong)

# Tình huống 4: Theo 2 mục: Phần và số La Mã
phan_va_so_la_ma = re.findall(r'^Phần [IV]+|I\. [A-Z][^.]*$', chuoi_bao_cao, re.MULTILINE)
print("Tình huống 4:", phan_va_so_la_ma)

# Tình huống 5: Theo cả 3 mục: Phần, số La Mã và số thường
phan_so_la_ma_va_thuong = re.findall(r'^Phần [IVXLCDM]+|I\. [A-Z][^.]*$|[0-9]+\.\s*[A-Za-z\s]+', chuoi_bao_cao, re.MULTILINE)
print("Tình huống 5:", phan_so_la_ma_va_thuong)

# Tạo một danh sách các tuple chứa tên tiêu đề và nội dung tương ứng
sections = re.findall(r'(Phần [IVXLCDM]+|[IVXLCDM]+\.\s*[A-Za-z\s]+)(.*?)(?=(Phần [IVXLCDM]+|[IVXLCDM]+\.\s*[A-Za-z\s]+|$))', chuoi_bao_cao, re.DOTALL)

# In ra tên tiêu đề và nội dung tương ứng
for section in sections:
    section_head = section[0].strip()
    section_content = section[1].strip()
    print("Tiêu đề:", section_head)
    print("Nội dung:", section_content)
    print()