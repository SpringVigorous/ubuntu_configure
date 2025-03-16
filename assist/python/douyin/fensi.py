# <div>
# 	<div class="i5U4dMnB">
# 		<div class="umh5JQVJ">
# 			<a href="//www.douyin.com/user/MS4wLjABAAAA4UN7dtUt0fpYNdUyEEpqNo8i3_hofGSMellb5Mi-yf4-Gd20ROdP7S5ZYCqxkq-v" class="uz1VJwFY" target="_blank" rel="noopener noreferrer">
# 				<span data-e2e="live-avatar" class="semi-avatar semi-avatar-circle semi-avatar-medium semi-avatar-grey syIEauc_ AaEZ65VP avatar-component-avatar-container" role="listitem" style="background-color:transparent">
# 					<img src="//p11.douyinpic.com/aweme/100x100/aweme-avatar/tos-cn-i-0813_oYA0ZPMAIiyAwIAzlTXkAksgBAdPzHNQzpEyi" alt="O低谷有雾o头像" class="fiWP27dC">
# 					</span>
# 				</a>
# 			</div>
# 			<div class="PETaiSYi">
# 				<div class="X8ljGzft">
# 					<div class="kUKK9Qal">
# 						<a href="//www.douyin.com/user/MS4wLjABAAAA4UN7dtUt0fpYNdUyEEpqNo8i3_hofGSMellb5Mi-yf4-Gd20ROdP7S5ZYCqxkq-v?enter_from=personal_homepage&amp;enter_method=fans_list&amp;from_tab_name=main&amp;is_search=0&amp;list_name=fans&amp;nt=0&amp;tab_name=fans_lish" class="uz1VJwFY" target="_blank" rel="noopener noreferrer">
# 							<span>
# 								<span class="arnSiSbK">
# 									<span>
# 										<span>
# 											<span>
# 												<span>O低谷有雾o</span>
# 											</span>
# 										</span>
# 									</span>
# 								</span>
# 							</span>
# 						</a>
# 					</div>
# 				</div>
# 			</div>
# 			<div class="HrvFYsXO">
# 				<button class="semi-button semi-button-primary xjIRvxqr" type="button" aria-disabled="false">
# 					<span class="semi-button-content" x-semi-prop="children">
# 						<div class="zPZJ3j40">回关</div>
# 					</span>
# 				</button>
# 				<button class="semi-button semi-button-secondary q8mycLOZ" type="button" aria-disabled="false">
# 					<span class="semi-button-content" x-semi-prop="children">
# 						<div class="tk5cqv6a">
# 							<div class="zPZJ3j40">移除</div>
# 						</div>
# 						<div class="DUBYbTPi">
# 							<div class="zPZJ3j40">
# 								<span class="ahBOP4gD">确认移除</span>
# 								<div class="S7nskTQm"></div>
# 								<span class="hWX1Xf7k">取消</span>
# 							</div>
# 						</div>
# 					</span>
# 				</button>
# 			</div>
# 		</div>
#   </div>
#   </div>


from pathlib import Path
import os
import sys
root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )


from base import logger_helper,UpdateTimeType,exception_decorator,convert_seconds_to_datetime



import json
import time
import pandas as pd


from lxml import html
# 示例 XML 数据
xml_data = '''
<root>
    <person>
        <name>John</name>
        <age>30</age>
    </person>
    <person>
        <name>Jane</name>
        <age>25</age>
    </person>
</root>
'''
xml_data=None
with open(r"F:\worm_practice\douyin\account\粉丝.xml", 'r', encoding='utf-8') as f:
    xml_data = f.read()

# 解析 XML 数据
tree = html.fromstring(xml_data)
infos = tree.xpath('//div[@class="i5U4dMnB"]')

# image_url=/html/body/div[21]/div/div/div[2]/div/div/div[3]/div[1]/div[1]/div[1]/a/span/img


