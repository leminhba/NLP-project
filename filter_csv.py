import pandas as pd
import os
import re
import time
from multiprocessing import Pool, cpu_count
def load_keywords_from_excel(file_path):
    if file_path:
        filepath = os.path.abspath(file_path)
        df = pd.read_excel(file_path, usecols=[0])
        return set(df.iloc[:, 0].tolist())
    else: return set()


def compile_keywords(keywords):
    # Biên dịch các từ khóa thành biểu thức chính quy
    return [re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE) for kw in keywords]

def check_title_type(title, trong_trot, chan_nuoi, lam_nghiep, thuy_san, nong_thon_moi, kinh_te_nong_nghiep):
    # Danh sách để lưu trữ các loại tìm thấy
    types_found = set()  # Sử dụng set để tránh trùng lặp

    # Kiểm tra từng nhóm từ khóa độc lập với biểu thức chính quy
    if any(pattern.search(title) for pattern in trong_trot):
        types_found.add("trong_trot")
    if any(pattern.search(title) for pattern in chan_nuoi):
        types_found.add("chan_nuoi")
    if any(pattern.search(title) for pattern in lam_nghiep):
        types_found.add("lam_nghiep")
    if any(pattern.search(title) for pattern in thuy_san):
        types_found.add("thuy_san")
    if any(pattern.search(title) for pattern in nong_thon_moi):
        types_found.add("nong_thon_moi")
    if any(pattern.search(title) for pattern in kinh_te_nong_nghiep):
        types_found.add("kinh_te_nong_nghiep")

    # Trả về chuỗi phân tách bởi dấu phảy nếu có kết quả
    return ', '.join(types_found) if types_found else 'none'

def process_chunk(chunk):
    trong_trot = compile_keywords(load_keywords_from_excel("dictionary/trong_trot.xls"))
    chan_nuoi = compile_keywords(load_keywords_from_excel("dictionary/chan_nuoi.xls"))
    lam_nghiep = compile_keywords(load_keywords_from_excel("dictionary/lam_nghiep.xls"))
    thuy_san = compile_keywords(load_keywords_from_excel("dictionary/thuy_san.xls"))
    nong_thon_moi = compile_keywords(load_keywords_from_excel("dictionary/nong_thon_moi.xls"))
    kinh_te_nong_nghiep = compile_keywords(load_keywords_from_excel("dictionary/kinh_te_nong_nghiep.xls"))

    chunk['tags'] = chunk['title'].apply(
        lambda title: check_title_type(title, trong_trot, chan_nuoi, lam_nghiep, thuy_san, nong_thon_moi, kinh_te_nong_nghiep))
    return chunk

if __name__ == '__main__':
    # Đọc file CSV vào một DataFrame
    csv_file_path = 'kinh_te.csv'
    df = pd.read_csv(csv_file_path, encoding='utf-8')

    # Khởi tạo cột "tags" với giá trị mặc định là 'none'
    df['tags'] = 'none'

    # Lấy số lượng CPU cores
    num_cores = cpu_count()

    # Khởi tạo Pool để thực hiện xử lý song song trên nhiều nhân CPU
    pool = Pool(processes=16)

    # Đếm thời gian xử lý
    start_time = time.time()

    # Đếm số lượng dòng đã xử lý
    processed_rows_count = 0

    # Đọc và xử lý từng phần của file CSV
    chunk_size = 10000  # Đọc 1000 dòng mỗi lần
    chunks = pd.read_csv(csv_file_path, encoding='utf-8', chunksize=chunk_size)
    result_chunks = []
    for chunk in chunks:
        processed_chunk = process_chunk(chunk)
        result_chunks.append(processed_chunk)
        processed_rows_count += len(chunk)

        # Kiểm tra xem đã đủ 1000 dòng để in ra màn hình
        if processed_rows_count >= 1000:
            elapsed_time = time.time() - start_time
            print(f'Đã xử lý {processed_rows_count} dòng, thời gian xử lý cho 1000 dòng: {elapsed_time:.2f} giây')
            start_time = time.time()
            processed_rows_count = 0

    # Kết hợp các phần đã xử lý thành DataFrame
    df = pd.concat(result_chunks, ignore_index=True)

    # Đếm số dòng trong file CSV
    total_rows = len(df)

    # Lọc các dòng mà cột 'tags' không rỗng
    filtered_df = df[df['tags'] != 'none']

    # Ghi dữ liệu đã lọc vào file CSV
    filtered_df.to_csv('output.csv', index=False, encoding='utf-8')

    # Đếm thời gian xử lý hoàn thành
    elapsed_time = time.time() - start_time

    print(f'Số dòng trong file CSV: {total_rows}')
    print(f'Số dòng đã lọc và ghi vào file CSV: {len(filtered_df)}')
