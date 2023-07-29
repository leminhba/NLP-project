import camelot
path_pdf = "D:\\362-1-1869-1-10-20220630.pdf"
result = camelot.read_pdf(path_pdf, pages='all')
result.export('foo.csv', f='csv', compress=True)