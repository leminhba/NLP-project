import json
import csv

# Đường dẫn đến file JSONL đầu vào và file CSV đầu ra
input_file = 'D:/Laptrinh/Python/Dataset/vi_5.jsonl'
output_file = 'vi_5.csv'

# Khởi tạo biến đếm
record_count = 0

# Mở file JSONL đầu vào và file CSV đầu ra
with open(input_file, 'r', encoding='utf-8') as json_file, \
     open(output_file, 'w', newline='', encoding='utf-8') as csv_file:
    # Khởi tạo đối tượng CSV writer
    csv_writer = csv.writer(csv_file)
    # Ghi header cho file CSV (nếu có)
    csv_writer.writerow(
        ['id', 'scores', 'langs', 'text', 'url', 'collection'])  # Thay 'field1', 'field2', ... bằng các trường dữ liệu thích hợp
    # Đọc và ghi 1000 dòng đầu tiên
    for i in range(100):
        line = json_file.readline().strip()
        if not line:  # Kiểm tra nếu đã đọc hết file
            break
        data = json.loads(line)
        # Ghi dữ liệu vào file CSV
        csv_writer.writerow([data['id'], data['scores'], data['langs'], data['text'], data['url'], data['collection']])