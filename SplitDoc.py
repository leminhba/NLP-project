import re
#doc_splitter = re.compile(r"^(?:Điều\ )\d+\.?", re.MULTILINE) #tach theo Dieu
#doc_splitter = re.compile(r"^(?:Điều\ )?\d+\.", re.MULTILINE) #tach theo Khoan
#Chi lay ten Dieu
doc_splitter = re.compile(r"^(?:Điều\ )\d+\.?", re.MULTILINE)

text = """
Chương I

NHỮNG QUY ĐỊNH CHUNG

Điều 14. Phạm vi điều chỉnh

Nghị định này quy định chi tiết một số điều, khoản của Luật Phòng, chống rửa tiền về nguyên tắc, tiêu chí, phương pháp đánh giá rủi ro quốc gia về rửa tiền; nhận biết khách hàng; tiêu chí xác định chủ sở hữu hưởng lợi; giao dịch có giá trị lớn bất thường hoặc phức tạp; cơ quan nhà nước có thẩm quyền tiếp nhận thông tin, hồ sơ, tài liệu, báo cáo; thu thập, xử lý và phân tích thông tin phòng, chống rửa tiền; trao đổi, cung cấp, chuyển giao thông tin phòng, chống rửa tiền với cơ quan có thẩm quyền trong nước; căn cứ để nghi ngờ hoặc phát hiện các bên liên quan đến giao dịch thuộc Danh sách đen và cơ quan nhà nước có thẩm quyền tiếp nhận báo cáo trì hoãn giao dịch.

Điều 2. Đối tượng áp dụng

1. Tổ chức tài chính.

2. Tổ chức, cá nhân kinh doanh ngành, nghề phi tài chính có liên quan.

3. Tổ chức, cá nhân Việt Nam, tổ chức nước ngoài, người nước ngoài, tổ chức quốc tế có giao dịch với tổ chức tài chính, tổ chức, cá nhân kinh doanh ngành, nghề phi tài chính có liên quan.

4. Tổ chức, cá nhân khác và các cơ quan có liên quan đến phòng, chống rửa tiền.

Chương II

ĐÁNH GIÁ RỦI RO QUỐC GIA VỀ RỬA TIỀN

Điều 32. Nguyên tắc đánh giá rủi ro quốc gia về rửa tiền

1. Đánh giá rủi ro quốc gia về rửa tiền do cơ quan nhà nước có thẩm quyền thực hiện theo các tiêu chí, phương pháp được pháp luật quy định, phù hợp với chuẩn mực quốc tế và điều kiện thực tiễn của Việt Nam.

2. Đánh giá rủi ro quốc gia về rửa tiền phải xác định được mức độ rủi ro về rửa tiền của quốc gia.

3. Đánh giá rủi ro quốc gia về rửa tiền là cơ sở để xây dựng kế hoạch thực hiện sau đánh giá và cập nhật chính sách, chiến lược về phòng, chống rửa tiền tương ứng trong từng thời kỳ.

4. Thông tin, tài liệu, dữ liệu phục vụ việc đánh giá rủi ro quốc gia về rửa tiền được thu thập từ cơ sở dữ liệu của các cơ quan có thẩm quyền, đối tượng báo cáo, tài liệu nghiên cứu trong và ngoài nước trên nguyên tắc công khai, minh bạch, bảo đảm tuân thủ các quy định về bảo vệ bí mật nhà nước.
"""
starts = [match.span()[0] for match in doc_splitter.finditer(text)] + [len(text)]
sections = [text[starts[idx]:starts[idx+1]] for idx in range(len(starts)-1)]
for section in sections:
    section = section.splitlines()[0]  #chi lay so dieu
    print([section])