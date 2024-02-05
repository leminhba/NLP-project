import main.util as util
import os


def extract_and_write_txt(docx_path):
    """
    Extracts text from a DOCX file and writes it to a TXT file in the same directory.
    The TXT file will only be created if it does not already exist.

    Parameters:
    - docx_path: str. The full path to the DOCX file.

     Returns:
    - str. The content of the TXT file.
    """

    # Tách đường dẫn và tên file
    dir_path, file_name = os.path.split(docx_path)
    base_name = os.path.splitext(file_name)[0]
    txt_file_name = f"{base_name}.txt"
    txt_file_path = os.path.join(dir_path, txt_file_name)

    # Kiểm tra nếu file TXT tồn tại
    if os.path.exists(txt_file_path):
        print(f"File {txt_file_name} already exists. Reading content...")
        with open(txt_file_path, 'r', encoding='utf-8') as file:
            return file.read(), None
    else:
        # Trích xuất nội dung từ file DOCX
        content, message = util.extract_text_from_file(docx_path)
        if content:
            # Ghi nội dung vào file TXT
            with open(txt_file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Content written to {txt_file_path}")
            return content, message
        else:
            print(f"Failed to extract content: {message}")
            return None, message


# Đường dẫn tới file .docx
path_file_temp = 'D:/Laptrinh/GSDG/GSDGNganh/MIC/Upload/Temp/2024/202402031040-202401311201-BC GIAO BAN BO T1.2024-29.01.2024_Final.docx'

# Gọi hàm và in ra nội dung trả về
content, message = extract_and_write_txt(path_file_temp)
if content:
    print("Content retrieved:")
    print(content)
    print(message)