from parsel import Selector

html = '''
<div class="button">
    <div class="tel">
        <img src="example1.jpg" alt="Call Us">
        <img src="example2.jpg" alt="Contact Us">
    </div>
</div>
'''

selector = Selector(text=html)
# 使用 :attr() 来获取属性值
src = selector.css('.tel img::attr(src)').getall()
print(src)  # 输出: example.jpg
