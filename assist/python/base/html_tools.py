from collections.abc import Iterable

class HtmlHelper:


    @staticmethod
    def tab_head_item(head_content):
        return """<th style="text-align:center; border:1px solid black; padding:8px;">{content}</th>
        """.format(content=head_content)

    @staticmethod
    def tab_tr(content):
        return """<tr>
            {content}
            </tr>
            """.format(content=content.strip())

    @staticmethod
    def tab_head(head_content:Iterable):
        content="".join([HtmlHelper.tab_head_item(item) for item in head_content])
        return HtmlHelper.tab_tr(content)

        
    @staticmethod
    def tab_body_item_txt(txt_content,vertical_align='center',color='black'):
        if isinstance(txt_content,str):
            txt_content=txt_content.replace("\n", "<br>")
        return """<td style="vertical-align:{align_type}; border:1px solid black; padding:8px;width:auto;color: {color};">{content}</td>
        """.format(align_type=vertical_align,content=txt_content,color=color)
        
    @staticmethod
    def tab_body_item_img(src_image,vertical_align='center',color='black'):
        src_cid_content,name,*args=src_image
        return """<td style="vertical-align:{align_type}; border:1px solid black; padding:8px;width:auto;color: {color};"><img src="cid:{src_id}"style="display:block;">{src_name}</td>
        """.format(align_type=vertical_align,src_id=src_cid_content,color=color,src_name=name)

    @staticmethod
    def tab_body_item(content,item_type=0,vertical_align='center',color='black'):
        is_txt=item_type==0
        func=HtmlHelper.tab_body_item_txt if  is_txt else HtmlHelper.tab_body_item_img
        if not vertical_align:
            vertical_align='top' if is_txt else 'center'
        return func(content,vertical_align,color=color)
            
    @staticmethod
    def tab_body_row(row_content:Iterable):
        content="".join([HtmlHelper.tab_body_item(*item) for item in row_content])
        return HtmlHelper.tab_tr(content)

        
    @staticmethod
    def tab_body(row_contents:Iterable[Iterable]):
        return "".join([HtmlHelper.tab_body_row(item)  for item in row_contents])

    #content,item_type=0,vertical_align='center'
    @staticmethod
    def tab(tabhead:Iterable,tabbody:Iterable[Iterable]):
        head=HtmlHelper.tab_head(tabhead)
        body=HtmlHelper.tab_body(tabbody)
    
        return """<table style="border-collapse: collapse; width: auto;">
            {head}
            {body}
        </table>""".format(head=head.strip(),body=body.strip())
        
    @staticmethod
    def html_content(content):
        return """<html>
        <body>
        {content}
        </body>
        </html>""".format(content=content.strip())
        
    #content,item_type=0,vertical_align='center'
    @staticmethod
    def html_tab(tabhead:Iterable,tabbody:Iterable[Iterable]):
        return HtmlHelper.html_content(HtmlHelper.tab(tabhead,tabbody))
    
    
if __name__ == '__main__':
    heads=["编号","描述","图片"]
    bodys=[
        [(1,0,"top"),("描述",0,"top"),("09b5e9ac",1,"center")],
        [(1,0,"top"),("描述",0,"top"),("09b5e9ac",1,"center")],
        [(1,0,"top"),("描述",0,"top"),("09b5e9ac",1,"center")],
        [(1,0,"top"),("描述",0,"top"),("09b5e9ac",1,"center")],
        [(1,0,"top"),("描述",0,"top"),("09b5e9ac",1,"center")],

    ]
    
    print(HtmlHelper.html_tab(heads,bodys))