import re
import pandas as pd

# Đoạn văn cần trích xuất
text = """Điều 1. Phê duyệt Chiến lược phát triển nông nghiệp và nông thôn bền vững giai đoạn 2021 - 2030, tầm nhìn đến năm 2050 (sau đây viết tắt là Chiến lược), với những nội dung chủ yếu sau:
I. QUAN ĐIỂM PHÁT TRIỂN
1. Nông nghiệp, nông dân, nông thôn có vị trí chiến lược trong sự nghiệp công nghiệp hoá, hiện đại hoá, xây dựng và bảo vệ tổ quốc; gìn giữ, phát huy bản sắc văn hóa dân tộc và bảo vệ môi trường sinh thái. Nông nghiệp là lợi thế, nền tảng bền vững của quốc gia. Nông thôn là địa bàn phát triển kinh tế quan trọng, là không gian chính gắn với tài nguyên thiên nhiên, nền tảng văn hóa, xã hội, đảm bảo an ninh, quốc phòng của đất nước. Nông dân là lực lượng lao động và nguồn tài nguyên con người quan trọng. Các vấn đề nông nghiệp, nông dân, nông thôn phải được giải quyết đồng bộ, gắn với quá trình đẩy mạnh công nghiệp hoá, hiện đại hoá đất nước.
2. Phát triển nông nghiệp hiệu quả, bền vững về kinh tế - xã hội - môi trường. Phát huy lợi thế, hiệu quả các nguồn lực (tài nguyên đất, nước, không khí, con người, truyền thống lịch sử, văn hóa) và khoa học công nghệ, đổi mới sáng tạo. Chuyển từ tư duy sản xuất nông nghiệp sang tư duy kinh tế nông nghiệp, sản xuất sản phẩm có giá trị cao, đa dạng theo chuỗi giá trị phù hợp với yêu cầu của thị trường, tích hợp các giá trị văn hóa, xã hội và môi trường vào sản phẩm. Sản xuất nông nghiệp có trách nhiệm, hiện đại, hiệu quả và bền vững; phát triển nông nghiệp sinh thái, hữu cơ, tuần hoàn, phát thải các-bon thấp, thân thiện với môi trường và thích ứng với biến đổi khí hậu.
3. Xây dựng nông thôn văn minh, có cơ sở hạ tầng và dịch vụ đồng bộ, hiện đại, đời sống cơ bản có chất lượng tiến gần đô thị; bảo tồn và phát huy truyền thống văn hóa tốt đẹp, an ninh trật tự được giữ vững; phát triển môi trường, cảnh quan xanh, sạch, đẹp. Phát triển kinh tế nông thôn đa dạng, chủ động tạo sinh kế nông thôn từ hoạt động phi nông nghiệp, tạo việc làm chính thức, thu hẹp khoảng cách thu nhập giữa nông thôn, thành thị và giảm di cư lao động ra các thành phố lớn. Xây dựng nông thôn mới trên cơ sở phát huy lợi thế, tiềm năng, phù hợp với từng vùng miền, gắn kết chặt chẽ với quá trình đô thị hóa, bảo đảm thực chất, đi vào chiều sâu, hiệu quả, bền vững; tập trung xây dựng nông thôn mới cấp thôn bản ở những nơi đặc biệt khó khăn, vùng đồng bào dân tộc thiểu số và miền núi."""

# Sử dụng regex để trích xuất nội dung vào các cột
dieu_pattern = r"Điều (\d+)\."
ma_muc_pattern = r"^(?:[IVX]+)\."
muc_1_pattern = r"\d+\."

dieu_match = re.search(dieu_pattern, text)
ma_muc_match = re.search(ma_muc_pattern, text)
muc_1_matches = re.finditer(muc_1_pattern, text)

dieu_content = dieu_match.group(0) if dieu_match else ""
ma_muc_content = ma_muc_match.group(0) if ma_muc_match else ""
muc_1_contents = [match.group(0).strip() for match in muc_1_matches]

# Tạo DataFrame pandas
data = {"Điều": [dieu_content] * len(muc_1_contents),
        "Mục La Mã": [ma_muc_content] * len(muc_1_contents),
        "Mục số thường": muc_1_contents}

df = pd.DataFrame(data)

# In bảng
print(df)
