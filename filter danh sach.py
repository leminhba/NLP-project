import pandas as pd

# Đọc dữ liệu
df = pd.read_excel("cau_kho_khan.xls", usecols=[4])
sentences = [s.lower() for s in df.iloc[:, 0].tolist()]  # Chuyển sang chữ thường ngay từ đầu
df2 = pd.read_excel("tu_kho_khan.xls", usecols=[0])
keywords = set(df2.iloc[:, 0].tolist())  # Sử dụng set nhưng không chuyển đổi chữ thường
#keywords = set([k.lower() for k in df2.iloc[:, 0].tolist()])  # Sử dụng set và chuyển sang chữ thường

# Tạo danh sách các câu không chứa từ khóa
non_matching_sentences = [s for s in sentences if not any(k in s for k in keywords)]

# Lưu kết quả
output_file = 'non_matching_sentences.txt'
with open(output_file, 'w', encoding='utf-8') as file:
    file.writelines(f"Câu số {i + 1}: {s}\n" for i, s in enumerate(non_matching_sentences))

print(f"Kết quả đã được lưu vào tệp {output_file}")