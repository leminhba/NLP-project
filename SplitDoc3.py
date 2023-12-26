import re


# Biểu thức chính quy cho các mục bắt đầu bằng chữ số và số La Mã
numeric_splitter = re.compile(r"^\d+\.", re.MULTILINE)
roman_splitter = re.compile(r"^[IVXLC]+\.", re.MULTILINE)
#doc_splitter = re.compile(r"^(?:Điều\ )\d+\.?", re.MULTILINE) #tach theo Dieu
#doc_splitter = re.compile(r"^(?:\d+)\.\d+\.", re.MULTILINE) #tach theo Khoan


# Biểu thức chính quy để tách theo số La Mã và số thứ tự
#doc_splitter = re.compile(r"(?:^[IVXLC]+\.\d+\.)", re.MULTILINE)
#doc_splitter = re.compile(r"(?:^[IVXLC]+\.\d+\.|\b(đánh giá|tồn tại|hạn chế|khó khăn|vướng mắc)\b)", re.MULTILINE | re.IGNORECASE)

# Danh sách các từ khóa
#keywords = ["đánh giá", "tồn tại", "hạn chế", "khó khăn", "vướng mắc"]
# Tạo chuỗi từ danh sách các từ khóa, phân tách bằng '|'
#keywords_pattern = r"(" + "|".join(keywords) + ")"

# Biểu thức chính quy để tìm kiếm số La Mã hoặc số thứ tự theo sau ngay lập tức bởi một trong các từ khóa
#doc_splitter = re.compile(r"(^[IVXLC]+\.\d+\.|\b)\s*" + keywords_pattern, re.MULTILINE | re.IGNORECASE)

text = """
I. ĐÁNH GIÁ TÌNH HÌNH KINH TẾ - XÃ HỘI 6 THÁNG ĐẦU NĂM 2021 VÀ NHIỆM VỤ 6 THÁNG CUỐI NĂM 2021
1. PHÁT TRIỂN SẢN XUẤT KINH DOANH VÀ CÁC NHIỆM VỤ TRỌNG TÂM  
1.1. Kết quả sản xuất
a) Trồng trọt
Trong tháng 3, tập trung gieo trồng, chăm sóc và thu hoạch lúa và các loại cây hoa màu vụ Đông Xuân. Tính chung 3 tháng đầu năm, sản xuất trồng trọt vẫn ổn định, sản lượng nhiều loại cây lâu năm chủ lực tăng. Giá trị sản xuất trồng trọt tăng khoảng 1,21% so với cùng kỳ năm 2022, chiếm 59,5% tỷ trọng GTSX của lĩnh vực nông nghiệp chung. Cụ thể:
1.2. Tiêu thụ nông sản, phát triển thị trường
a) Xuất, nhập khẩu
Theo báo cáo của Trung tâm Chuyển đổi số và Thống kê Nông nghiệp, tổng kim ngạch xuất, nhập khẩu hàng NLTS 03 tháng đầu năm ước đạt 20,63 tỷ USD, giảm 11,2% so với CKNT; trong đó, xuất khẩu ước đạt 11,19 tỷ USD, giảm 14,4% so với CKNT; nhập khẩu ước đạt 9,44 tỷ USD, giảm 7,2%; xuất siêu 1,76 tỷ USD, giảm 39,6% so với CKNT.
2. ĐÁNH GIÁ CHUNG
2.1. Những mặt được, ưu điểm
Mặc dù, tiếp tục gặp nhiều khó khăn, thách thức, nhưng toàn Ngành đã chủ động, tích cực, sáng tạo trong công tác tham mưu Chính phủ, Thủ tướng Chính phủ, phối hợp với chặt chẽ với các Bộ, ngành, địa phương; huy động các nguồn lực xã hội để quyết liệt thực hiện đồng bộ các nhiệm vụ, giải pháp tháo gỡ khó khăn và đặt tăng trưởng toàn Ngành Quý I/2023 đạt khá cao 2,5% với: 
(1) Duy trì tăng trưởng trên tất cả các tiểu ngành, lĩnh vực, góp phần ổn định kinh tế vĩ mô; 
(2) Bảo đảm an ninh lương thực, thực phẩm; an toàn thực phẩm góp phần bảo đảm các cân đối lớn của nền kinh tế; 
(3) Số hợp tác xã nông nghiệp; số xã, huyện đạt chuẩn nông thôn mới tăng, sản phẩm đạt chuẩn OCOP chất lượng cao tiếp tục tăng;
(4) Bộ đã chỉ đạo xây dựng và thực hiện nghiêm túc, kịp thời các Nghị quyết của Trung ương Đảng, Bộ Chính trị, Chính phủ nhằm tạo điều kiện phát triển nông nghiệp, nông thôn, xây dựng lực lượng nông dân tri thức, chuyên nghiệp. Qua đó, tạo nền tảng để thực hiện chuyển đổi nông nghiệp bền vững, trong đó chuyển đổi tư duy từ sản xuất nông nghiệp sang kinh tế nông nghiệp.
2.2. Những tồn tại, hạn chế
- Tốc độ tăng trưởng toàn ngành chưa đạt so với kịch bản tăng trưởng đề ra; tổng kim ngạch xuất khẩu NLTS giảm, thặng dư thương mại giảm so với CKNT. Nguyên nhân do kinh tế toàn cầu năm 2023 dự báo tăng trưởng chậm lại; ảnh hưởng từ xung đột quân sự Nga - Ukraine; tình trạng lạm phát cao tại một số nước trên thế giới đã làm giảm nhu cầu tiêu dùng, nhu cầu nhập khẩu. Thêm vào đó, do sau khi dịch bệnh Covid-19 được kiểm soát, nhiều nước tái xuất khẩu nông sản và tăng cung trên thị trường; trong khi ở trong nước, nhiều doanh nghiệp chưa ký được đơn hàng xuất khẩu mới năm 2023 (Bộ đã dự báo được tình hình từ những tháng cuối năm 2022).
- Tại thị trường trong nước: Giá cả một số mặt hàng giảm nhẹ như: lúa, cà phê, chè, hạt tiêu, trái cây, lợn hơi, gà.. do sang tháng 3, nhu cầu tiêu dùng lương thực thực phẩm thấp hơn so với tháng trước (trong dịp Tết nguyên đán).
2.3. Tồn tại, hạn chế 
Với tinh thần nhìn thẳng, thấy rõ tồn tại, hạn chế để khắc phục, quyết liệt trong hoạt động thực tiễn; khát vọng thành công hơn, chúng ta thấy rằng còn những hạn chế, tồn tại cần tập trung khắc phục trong thời gian tới, đó là:
(1) Việc cụ thể hóa và tổ chức thực hiện các chính sách hỗ trợ sản xuất kinh doanh, liên kết sản xuất với tiêu thụ nông sản thực phẩm an toàn ở một số địa phương còn chậm, sản lượng và quy mô còn hạn chế.
7. ĐÁNH GIÁ CHUNG
7.1. Thuận lợi
Được sự quan tâm chỉ đạo sâu sát của Chính phủ, Bộ Nông nghiệp và PTNT, Tỉnh ủy, UBND tỉnh; sự phối hợp có hiệu quả giữa các Sở, Ngành, đơn vị có liên quan và UBND các huyện, thị xã, thành phố trong chỉ đạo, điều hành, tổ chức thực hiện nhiệm vụ phát triển nông nghiệp, nông thôn trên địa bàn tỉnh. Vai trò lãnh đạo, chỉ đạo, điều hành và tổ chức thực hiện nhiệm vụ của Sở Nông nghiệp và PTNT; sự nhiệt tình của đội ngũ cán bộ, công chức, viên chức trong việc hướng dẫn nông, ngư dân tổ chức sản xuất, phòng trừ các đối tượng gây hại trên cây trồng, vật nuôi, thủy sản và tinh thần tích cực lao động, ứng dụng các tiến bộ khoa học, công nghệ trong quá trình sản xuất của nông, ngư dân. Mặc dù sản xuất nông nghiệp bị ảnh hưởng bởi biến đổi khí hậu và dịch bệnh Covid-19 nhưng ngành nông nghiệp đã chủ động phòng chống nên bảo vệ được diện tích sản xuất nông nghiệp, nuôi trồng thủy sản và an sinh xã hội được đảm bảo.
7.2. Khó khăn, hạn chế
- Do ảnh hưởng của tình hình dịch bệnh Covid 19, giá vật tư đầu vào tăng nhưng giá tôm nguyên liệu và lúa hàng hóa không tăng mà đôi lúc còn giảm nên làm ảnh hưởng lớn đến lợi nhuận của người sản xuất. Đa số người nuôi tôm còn khó khăn về vốn, số hộ đảm bảo thủ tục vay không nhiều, thiếu tài sản thế chấp hoặc đang thế chấp ngân hàng. 
- Đối với xây dựng nhãn hiệu: Kinh phí chứng nhận cao, các bước và thủ tục để xây dựng chưa quy định cụ thể nên rất khó hướng dẫn tổ chức, cá nhân thực hiện; bên cạnh đó thời gian thực hiện chứng nhận kéo dài từ 18 - 24 tháng.

"""
matches = ["đánh giá", "tồn tại", "hạn chế", "khó khăn", "vướng mắc"]

def find_sections(splitter):
    starts = [match.span()[0] for match in splitter.finditer(text)] + [len(text)]
    sections = [text[starts[idx]:starts[idx+1]] for idx in range(len(starts)-1)]
    return sections

# Thử tìm theo chữ số trước
sections = find_sections(numeric_splitter)

# Nếu không tìm thấy mục nào, thử tìm theo số La Mã
if not sections:
    sections = find_sections(roman_splitter)


for section in sections:
    section_head = section.splitlines()[0].lower()
    if any(match in section_head for match in matches):  # chỉ lấy mục thỏa mãn điều kiện
        print(section_head)


