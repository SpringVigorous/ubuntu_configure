import requests
import parsel
import pdfkit
import os
import re

html_str ='''
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Document</title>
</head>
<body>article</body>
</html>

'''
headers={
    'user-agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36'
    
}
def change_title(title:str):
    return re.sub(r'[\\/:*?"<>|]', '', title)

url='https://so.csdn.net/so/search?spm=1000.2115.3001.4498&q=windows%20c%2B%2B%20%20%E5%A4%9A%E8%BF%9B%E7%A8%8B&t=&u='


for page in range(1,2):
    # url=f'blog.csdn.net/pythonxuexi123/article/list/{page}'
    response=requests.get(url=url,headers=headers)
    response.encoding='utf-8'
    content=response.text
    print(content)
    
    selector=parsel.Selector(content)
    href=selector.css('.article-list div.article-item-box a::attr(href)').getall()   

    for link in href:
        # print(link)
        # 对文章的url地址发送请求
        response_1 =requests.get(url=link, headers=headers)
        selector_1=parsel.Selector(response_1.text)
        title =selector_1.css('#articlecontentId::text').get()
        content =selector_1.css('#content_views').get()
        new_title = change_title(title)
        #保存数据 字符串格式化方法
        html = html_str.format(article=content)
        html_path ='HTML\\'+ new_title + '.html'
        pdf_path ='PDF\\'+ new_title +'.pdf'
        with open(html_path, mode='w', encoding='utf-8') as f:
            f.write(html)
            print('正在保存:',title)
        #把html文件转换成 PDF文件
        config = pdfkit.configuration(wkhtmltopdf=r'D:\Tool\wkhtmltopdf\lwkhtmltopdf.exe')
        pdfkit.from_file(html_path, pdf_path, configuration=config)
        os.remove(html_path)