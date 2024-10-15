import os
from glob import glob
import json

if False:
    # 指定目录路径
    dir_path = r'F:\教程\多肉\哔哩哔哩视频\title'

    # 查找所有以 ".ai-zh_title.txt" 结尾的文件
    files = glob(os.path.join(dir_path, '*.ai-zh_title.txt'))

    # 重命名每个找到的文件
    for file in files:
        # 构造新的文件名
        new_file_name = file.replace('.ai-zh', '')
        # 执行重命名
        os.rename(file, new_file_name)
        print(f'已将 {file} 重命名为 {new_file_name}')
    
    
if __name__=='__main__':
    
    
    
    
    # https://adschool.xiaohongshu.com/api/school/client/course/multi_get_lessones?source=xue&publishSystemId=1
    xhs={
    "code": 0,
    "success": True,
    "msg": "成功",
    "data": {
        "lastStudyLessonProgress": "2.12",
        "response": {
            "success": True,
            "message": "success"
        },
        "studyCount": 27101,
        "dataList": [
            {
                "lessonId": 4291,
                "title": "欢迎来到小红书",
                "contentType": 1,
                "lessonTimeValue": 173,
                "contentUrl": {
                    "fileId": None,
                    "subFileIds": None,
                    "fileName": None,
                    "fileType": "video",
                    "url": {
                        "master": "https://fe-video-qc.xhscdn.com/fe-platform/104101b03156iur53gk065v3ch2g1860004d3d3del2564",
                        "slave": None,
                        "slaves": None
                    },
                    "subUrls": None,
                    "source": "xueArticleImport"
                },
                "progress": "2.12"
            },
            {
                "progress": "0",
                "lessonId": 4290,
                "title": "如何在小红书上建立一个专业的品牌形象",
                "contentType": 1,
                "lessonTimeValue": 286,
                "contentUrl": {
                    "fileId": None,
                    "subFileIds": None,
                    "fileName": None,
                    "fileType": "video",
                    "url": {
                        "master": "https://fe-video-qc.xhscdn.com/fe-platform/104101b03156iuo19gk065v3ch2g1860004d3d3814sfme",
                        "slave": None,
                        "slaves": None
                    },
                    "subUrls": None,
                    "source": "xueArticleImport"
                }
            },
            {
                "lessonId": 4289,
                "title": "怎样在小红书写好笔记",
                "contentType": 1,
                "lessonTimeValue": 298,
                "contentUrl": {
                    "fileId": None,
                    "subFileIds": None,
                    "fileName": None,
                    "fileType": "video",
                    "url": {
                        "master": "https://fe-video-qc.xhscdn.com/fe-platform/104101b03156iuk040o065v3ch2g1860004d3d3eh3dhpi",
                        "slave": None,
                        "slaves": None
                    },
                    "subUrls": None,
                    "source": "xueArticleImport"
                },
                "progress": "0"
            },
            {
                "progress": "0",
                "lessonId": 4288,
                "title": "如何加热自己的笔记",
                "contentType": 1,
                "lessonTimeValue": 299,
                "contentUrl": {
                    "fileId": None,
                    "subFileIds": None,
                    "fileName": None,
                    "fileType": "video",
                    "url": {
                        "master": "https://fe-video-qc.xhscdn.com/fe-platform/104101b03156iucg30q065v3ch2g1860004d3d39i6a2ko",
                        "slave": None,
                        "slaves": None
                    },
                    "subUrls": None,
                    "source": "xueArticleImport"
                }
            },
            {
                "lessonId": 4287,
                "title": "产品种草组合投放策略",
                "contentType": 1,
                "lessonTimeValue": 296,
                "contentUrl": {
                    "fileId": None,
                    "subFileIds": None,
                    "fileName": None,
                    "fileType": "video",
                    "url": {
                        "master": "https://fe-video-qc.xhscdn.com/fe-platform/104101b03156iu8l8gk065v3ch2g1860004d3d3f4ojemi",
                        "slave": None,
                        "slaves": None
                    },
                    "subUrls": None,
                    "source": "xueArticleImport"
                },
                "progress": "0"
            },
            {
                "lessonTimeValue": 252,
                "contentUrl": {
                    "fileId": None,
                    "subFileIds": None,
                    "fileName": None,
                    "fileType": "video",
                    "url": {
                        "master": "https://fe-video-qc.xhscdn.com/fe-platform/104101b03156iu4n9gm065v3ch2g1860004d3d3blsarmi",
                        "slave": None,
                        "slaves": None
                    },
                    "subUrls": None,
                    "source": "xueArticleImport"
                },
                "progress": "0",
                "lessonId": 4286,
                "title": "如何在小红书投放第一个广告",
                "contentType": 1
            },
            {
                "lessonTimeValue": 271,
                "contentUrl": {
                    "fileId": None,
                    "subFileIds": None,
                    "fileName": None,
                    "fileType": "video",
                    "url": {
                        "master": "https://fe-video-qc.xhscdn.com/fe-platform/104101b03156ir33lgq065v3ch2g1860004d3d39koccds",
                        "slave": None,
                        "slaves": None
                    },
                    "subUrls": None,
                    "source": "xueArticleImport"
                },
                "progress": "0",
                "lessonId": 4285,
                "title": "如何与小红书博主合作",
                "contentType": 1
            },
            {
                "lessonId": 4284,
                "title": "如何做好数据洞察与度量",
                "contentType": 1,
                "lessonTimeValue": 275,
                "contentUrl": {
                    "fileId": None,
                    "subFileIds": None,
                    "fileName": None,
                    "fileType": "video",
                    "url": {
                        "master": "https://fe-video-qc.xhscdn.com/fe-platform/104101b03156iqnrmgk065v3ch2g1860004d3d3dso29vg",
                        "slave": None,
                        "slaves": None
                    },
                    "subUrls": None,
                    "source": "xueArticleImport"
                },
                "progress": "0"
            },
            {
                "contentType": 1,
                "lessonTimeValue": 275,
                "contentUrl": {
                    "fileId": None,
                    "subFileIds": None,
                    "fileName": None,
                    "fileType": "video",
                    "url": {
                        "master": "https://fe-video-qc.xhscdn.com/fe-platform/104101b03156iqeh90q065v3ch2g1860004d3d3e8lujgo",
                        "slave": None,
                        "slaves": None
                    },
                    "subUrls": None,
                    "source": "xueArticleImport"
                },
                "progress": "0",
                "lessonId": 4283,
                "title": "如何在小红书做好电商营销"
            },
            {
                "progress": "0",
                "lessonId": 4282,
                "title": "如何在小红书做好直播",
                "contentType": 1,
                "lessonTimeValue": 216,
                "contentUrl": {
                    "fileId": None,
                    "subFileIds": None,
                    "fileName": None,
                    "fileType": "video",
                    "url": {
                        "master": "https://fe-video-qc.xhscdn.com/fe-platform/104101b03156iqd790k065v3ch2g1860004d3d3ac2gf82",
                        "slave": None,
                        "slaves": None
                    },
                    "subUrls": None,
                    "source": "xueArticleImport"
                }
            },
            {
                "lessonId": 4281,
                "title": "小红书社区公约和商业内容公约",
                "contentType": 1,
                "lessonTimeValue": 444,
                "contentUrl": {
                    "fileId": None,
                    "subFileIds": None,
                    "fileName": None,
                    "fileType": "video",
                    "url": {
                        "master": "https://fe-video-qc.xhscdn.com/fe-platform/104101b03156iq0opgs065v3ch2g1860004d3d3dbbcjp0",
                        "slave": None,
                        "slaves": None
                    },
                    "subUrls": None,
                    "source": "xueArticleImport"
                },
                "progress": "0"
            },
            {
                "lessonId": 4280,
                "title": "小红书学习地图",
                "contentType": 1,
                "lessonTimeValue": 124,
                "contentUrl": {
                    "fileId": None,
                    "subFileIds": None,
                    "fileName": None,
                    "fileType": "video",
                    "url": {
                        "master": "https://fe-video-qc.xhscdn.com/fe-platform/104101b03156ipo8ggq065v3ch2g1860004d3d398ht2u8",
                        "slave": None,
                        "slaves": None
                    },
                    "subUrls": None,
                    "source": "xueArticleImport"
                },
                "progress": "0"
            }
        ],
        "lastStudyLessonId": 4291
    }
}
    json.dump(xhs, open('xhs.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)