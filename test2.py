import re

# Danh sách 10 câu
list_of_sentences = [
    "Học máy là một lĩnh vực quan trọng trong khoa học máy tính.",
    "Khoa học dữ liệu là một phần của học máy.",
    "Các phương pháp học máy đang phát triển nhanh chóng.",
    "Khoa học máy tính là một ngành học rộng lớn.",
    "Trong khoa học máy, việc thu thập dữ liệu là quan trọng.",
    "Nghiên cứu khoa học máy đòi hỏi kiến thức chuyên sâu về toán học.",
    "Khoa học dữ liệu và học máy đang thay đổi cách chúng ta xử lý thông tin.",
    "Học máy có ứng dụng rộng rãi trong nhiều lĩnh vực khác nhau.",
    "Khoa học máy tính cung cấp các phương pháp giải quyết vấn đề phức tạp.",
    "Nghiên cứu về học máy đang thu hút sự chú ý lớn từ cộng đồng khoa học."
]

# Danh sách từ khóa để phân loại
list_of_keywords = ["học máy AND (khoa học OR máy tính)", "toán học", "dữ liệu AND học máy"]

# Tạo một từ điển để theo dõi câu đã được phân loại và đếm số câu
classified_sentences = {keyword: {'sentences': [], 'count': 0} for keyword in list_of_keywords}
classified_sentences["khác"] = {'sentences': [], 'count': 0}

# Phân loại câu vào từng nhóm và đếm số câu
for sentence in list_of_sentences:
    classified = False  # Đánh dấu câu đã được phân loại hay chưa

    for keyword in list_of_keywords:
        # Kiểm tra AND và OR
        if "AND" in keyword or "OR" in keyword:
            and_or_keywords = re.split(r'\b(AND|OR)\b', keyword)
            and_keywords = [kw.strip() for kw in and_or_keywords if kw.strip() != "AND"]
            # Loại bỏ dấu "(" ở đầu các từ và dấu ")" ở cuối các từ trong từ điển
            and_keywords = [kw.strip("(").strip(")") for kw in and_keywords]
            or_keywords = [kw.strip() for kw in and_or_keywords if kw.strip() != "OR"]

            # nếu tìm thấy AND và một trong số các từ trong and_keywords đều có trong câu thì phân loại câu vào nhóm đó

            if "AND" in keyword and all(re.search(fr'\b{kw}\b', sentence) for kw in and_keywords):
                classified_sentences[keyword]['sentences'].append(sentence)
                classified_sentences[keyword]['count'] += 1
                classified = True
                break
            elif "OR" in keyword and any(re.search(fr'\b{kw}\b', sentence) for kw in or_keywords):
                classified_sentences[keyword]['sentences'].append(sentence)
                classified_sentences[keyword]['count'] += 1
                classified = True
                break
        # Kiểm tra từ đơn
        else:
            if re.search(fr'\b{keyword}\b', sentence):
                classified_sentences[keyword]['sentences'].append(sentence)
                classified_sentences[keyword]['count'] += 1
                classified = True
                break

    if not classified:
        classified_sentences["khác"]['sentences'].append(sentence)
        classified_sentences["khác"]['count'] += 1

# Sắp xếp nhóm theo số câu giảm dần
sorted_classified_sentences = sorted(classified_sentences.items(), key=lambda x: x[1]['count'], reverse=True)

# In kết quả
for keyword, group_info in sorted_classified_sentences:
    print(f"Nhóm '{keyword}': ({group_info['count']} câu)")
    for sentence in group_info['sentences']:
        print("-", sentence)
    print()





