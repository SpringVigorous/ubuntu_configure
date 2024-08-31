import pdfplumber


def test_pdf():
    with pdfplumber.open(r'F:\教程\python\爬虫\马哥python说\【马哥python说】python资料包20220318\Python入门指南.pdf') as pdf:
        page = pdf.pages[45]
        text = page.extract_text()
        print(text)
    
    
    pass

if __name__ == '__main__':
    test_pdf()