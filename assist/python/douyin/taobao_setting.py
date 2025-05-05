#tab框，包含 用户评价、参数信息、图文详情

# loaded_path='xpath://div[@class="Oo3vRXl7BS--tabTitleItem--_3629685"]'
goods_loaded_path='xpath://div[contains(@class, "tabTitleItem")]'
desc_img_path='xpath://div[contains(@class, "singleImage")]'



#主图 +title +video(包含哪些产品（url、id、销量、sku图）)
listent_main_api='mtop.taobao.pcdetail.data.get'

#js参数：详图信息
#'https://h5api.m.taobao.com/h5/mtop.taobao.detail.getdesc/7.0/'
listen_desc_api='mtop.taobao.detail.getdesc'
#视频
#https://h5api.m.taobao.com/h5/mtop.taobao.cloudvideo.video.query/3.0/



shop_loaded_path='xpath://div[contains(@class,"cardContainer")]'
listent_shop_api=['mtop.taobao.shop.simple.fetch','mtop.taobao.shop.simple.item.fetch']


download_pic_headers={
    'authority': 'img.alicdn.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 SE 2.X MetaSr 1.0',
}
download_verify=False