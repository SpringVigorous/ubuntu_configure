import requests
import csv


note_id=""
data_json={
	"cursor_score": "",
	"num": 30,
	"refresh_type": 1,
	"note_index": 0,
	"unread_begin_note_id": "",
	"unread_end_note_id": "",
	"unread_note_count": 0,
	"category": "homefeed_recommend",
	"search_key": "",
	"need_num": 15,
	"image_formats": ["jpg", "webp", "avif"],
	"need_filter_image": False
}
 
class Writer:
	def __init__(self, result_file):
		self.result_file = result_file
 
	def write(self, data_row):
		# 保存到csv文件
		with open(self.result_file, 'a+', encoding='utf_8_sig', newline='') as f:
			writer = csv.writer(f)
			writer.writerow(data_row) 
	"""这里采用csv库保存数据，方便每爬取一条笔记数据，快速保存到csv文件中。
	完整代码中，还含有：判断循环结束条件、转换时间戳、js逆向解密等关键实现逻辑，详见文末。
	"""
def search_note(note_id,a,s):
	# 请求地址
	url = 'https://edith.xiaohongshu.com/api/sns/web/v1/homefeed'

	# 定义一个请求头，用于伪造浏览器：
	cookies = 'a1=19029c91c9erh6glnzwujndoez49q5pope7wjw49x00000858779;webId=04a7b350ba3ec00cc1ec563c2eca3319;gid=yj8JjSD22jU0yj8JjSjySdE4jdFxKk1IuE7VWjCIfldu4E88jA2UlV888Y2YWWj82i82D0fq;customer-sso-sid=68c517381709387753437817a2f255a13cd6a803;x-user-id-ark.xiaohongshu.com=5d593e3500000000010013c2;customerClientId=606764650847459;abRequestId=04a7b350ba3ec00cc1ec563c2eca3319;xsecappid=xhs-pc-web;webBuild=4.31.6;web_session=040069b26ead56dc3c1f8535f8344b9e09a377;unread={%22ub%22:%2266c9d9e8000000001d03b3b5%22%2C%22ue%22:%2266c31d33000000001f0157c2%22%2C%22uc%22:21};acw_tc=669686031de5a37e4a1164072f5ea00898fb2a14633ad24a3f5c7440f0078005;websectiga=cf46039d1971c7b9a650d87269f31ac8fe3bf71d61ebf9d9a0a87efb414b816c;sec_poison_id=ee254610-89ad-493e-a217-c1cea0b3fbe1'


	# 请求头
	headers = {
		'Accept': 'application/json, text/plain, */*',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
		'Content-Type': 'application/json;charset=UTF-8',
		'Cookie': cookies,
		'Origin': 'https://www.xiaohongshu.com',
		'Referer': 'https://www.xiaohongshu.com/',
		'Sec-Ch-Ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
		'Sec-Ch-Ua-Mobile': '?0',
		'Sec-Ch-Ua-Platform': '"macOS"',
		'Sec-Fetch-Dest': 'empty',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Site': 'same-site',
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
	}
	# 请求参数
	post_data = {
		"source_note_id": note_id,
		"image_formats": ["jpg", "webp", "avif"],
		"extra": {"need_body_topic": "1"}
	}
	# 下面就是发送请求和接收数据：
	# 发送请求
	r = requests.post(url, headers=headers, data=data_json)
	# 接收数据
	json_data = r.json()
	# 逐个解析字段数据，以"笔记标题"为例：
	# 笔记标题
	try:
		title = json_data['data']['items'][0]['note_card']['title']
	except:
		title = ''
	
	
	desc=''
	create_time=''
	update_time=''
	ip_location=''
	like_count=''
	collected_count=''
	comment_count=''
	share_count=''
	nickname=''
	user_id=''
	user_url=''

	"""熟悉xhs的朋友都知道，有些笔记是没有标题的，所以这里加上try保护，防止程序报错导致中断运行。
	其他字段同理，不再赘述。
	最后，是把数据保存到csv文件："""
	# 返回数据
	data_row = note_id, title, desc, create_time, update_time, ip_location, like_count, collected_count, comment_count, share_count, nickname, user_id, user_url
 
	Writer('result.csv').write(data_row)


	# 代码运行结果如下：