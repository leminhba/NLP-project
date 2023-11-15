from pdf2docx import Converter
import os

# # # dir_path for input reading and output files & a for loop # # #

path_input = 'pdf/'
path_output = 'docx/'

for file in os.listdir(path_input):
    cv = Converter(path_input+file)
    cv.convert(path_output+file+'.docx', start=0, end=None)
    cv.close()
    print(file)