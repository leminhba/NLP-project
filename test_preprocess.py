from main_model.model.pipeline import *
from main_model.util.general_normalize import _clean_text
text = "Thanh long rất ngon có 500 tấn. Xoài có 1000 tấn. Dự án có điều kiện địa hình, địa chất, thủy văn thuận tiện để xây dựng dự án thủy điện"
print(_clean_text(text))
