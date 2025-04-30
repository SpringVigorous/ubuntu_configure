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


xlsx_file=os.path.join(db_dir,"taobao.xlsx")


shop_name="店铺"
pic_name="图片"
orc_name="文字识别"

item_id="itemId"
num_id="num"
name_id="name"

