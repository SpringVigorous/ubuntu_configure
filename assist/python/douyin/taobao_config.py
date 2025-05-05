import  os

root_dir=r"F:\worm_practice\taobao"
desc_dir=os.path.join(root_dir,"详图")
main_dir=os.path.join(root_dir,"主图")

org_pic_dir=os.path.join(root_dir,"org_pic")
ocr_pic_dir=os.path.join(root_dir,"ocr_pic")
db_dir=os.path.join(root_dir,"数据")
shop_dir=os.path.join(root_dir,"店铺")

os.makedirs(desc_dir,exist_ok=True)
os.makedirs(main_dir,exist_ok=True)
os.makedirs(org_pic_dir,exist_ok=True)
os.makedirs(ocr_pic_dir,exist_ok=True)
os.makedirs(shop_dir,exist_ok=True)
os.makedirs(db_dir,exist_ok=True)


xlsx_file=os.path.join(db_dir,"taobao.xlsx")


shop_name="店铺"
product_name="商品"
pic_name="图片"
ocr_name="文字识别"


shop_id="shopId"
item_id="itemId"
item_url_id="itemUrl"
num_id="num"
name_id="name"
pic_url_id="pic_url"
shop_name_id="shop_name"
user_id="user_id"
seller_id="seller_id"
home_url_id="home_url"
goods_name_id="goods_name"
ocr_text_id="text"
org_pic_path_id="org_pic_path"
ocr_pic_path_id="ocr_pic_path"


sleep_time=5
goods_type=1
shop_type=2
detail_type=3