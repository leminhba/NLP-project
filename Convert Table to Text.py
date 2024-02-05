import pandas as pd
import random

def interpret_comparison(value):
    """Hàm này chuyển đổi giá trị so sánh thành một chuỗi diễn giải."""
    if "-" in value:
        return f"giảm {value.replace('-', '').strip()}"
    else:
        return f"tăng {value.strip()}"
    return value.strip()


def create_report_from_excel(file_path):
    # Đọc file Excel
    data = pd.read_excel(file_path)
    period = data.loc[0, 'Kỳ thu thập']
    # Lấy và chuyển đổi dữ liệu từ dataframe
    area_sowed = data.loc[0, 'Kết quả']
    decrease_sowed = interpret_comparison(data.loc[0, 'So sánh cùng kỳ năm trước'])
    area_harvested = data.loc[1, 'Kết quả']
    decrease_harvested = interpret_comparison(data.loc[1, 'So sánh cùng kỳ năm trước'])
    avg_yield = data.loc[2, 'Kết quả']
    increase_yield = interpret_comparison(data.loc[2, 'So sánh cùng kỳ năm trước'])
    production = data.loc[3, 'Kết quả']
    increase_production = interpret_comparison(data.loc[3, 'So sánh cùng kỳ năm trước'])

    # Tạo báo cáo với các diễn giải đã chuyển đổi
    # Định nghĩa một tập hợp các template báo cáo
    templates = [
        "Lúa: Đến {period}, diện tích gieo trồng là {area_sowed} nghìn ha, {decrease_sowed}; diện tích thu hoạch là {area_harvested} nghìn ha, {decrease_harvested}. Năng suất và sản lượng lần lượt là {avg_yield} tạ/ha, {increase_yield} và {production} triệu tấn, {increase_production}.",
        "Trong {period} đầu năm, với {area_sowed} nghìn ha gieo trồng, {decrease_sowed} so với năm trước, và {area_harvested} nghìn ha thu hoạch, {decrease_harvested}, năng suất đạt {avg_yield} tạ/ha, {increase_yield}. Sản lượng {production} triệu tấn, {increase_production}.",
        # Thêm nhiều template khác với các phong cách diễn đạt khác nhau
    ]

    # Chọn ngẫu nhiên một template
    template = random.choice(templates)

    report = template.format(
        period=period,
        area_sowed=data.loc[0, 'Kết quả'],
        decrease_sowed=interpret_comparison(data.loc[0, 'So sánh cùng kỳ năm trước']),
        area_harvested=data.loc[1, 'Kết quả'],
        decrease_harvested=interpret_comparison(data.loc[1, 'So sánh cùng kỳ năm trước']),
        avg_yield=data.loc[2, 'Kết quả'],
        increase_yield=interpret_comparison(data.loc[2, 'So sánh cùng kỳ năm trước']),
        production=data.loc[3, 'Kết quả'],
        increase_production=interpret_comparison(data.loc[3, 'So sánh cùng kỳ năm trước'])
    )

    return report


# Sử dụng hàm với đường dẫn file
file_path = 'bao_cao_sx.xls'
report = create_report_from_excel(file_path)
print(report)