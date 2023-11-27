import re

from pyparsing import infixNotation, opAssoc, Literal, CaselessKeyword

#tạo một danh sách gồm 10 câu
list_of_sentences = [
    "Machine learning is a field of computer science.",
    "Mathematics is the foundation of many algorithms in machine learning.",
    "Big data plays a crucial role in machine learning.",
    "Computers can learn from data to perform complex tasks.",
    "Both mathematics and computers are important in the development of machine learning.",
    "Data is the key to understanding machine learning deeply.",
    "Computer science researches methods of machine learning.",
    "Mathematics is the language of machine learning.",
    "Machine learning and computer science both study data processing.",
    "Data combined with mathematics is an important factor in machine learning."
]
keyword = "(computer science OR computers)"


list_of_keywords = ["machine learning AND (computer science OR computers)", "mathematics", "data AND machine learning"]
# Tìm trong list_of_sentences các câu thỏa mãn điều kiện: machine learning AND (computer science OR computers)
# và in ra màn hình
for sentence in list_of_sentences:
    if re.search(r'\bmachine learning\b', sentence) and (re.search(r'\bcomputer science\b', sentence) or re.search(r'\bcomputers\b', sentence)):
        print(sentence)




