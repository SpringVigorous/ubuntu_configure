from rectpack import newPacker,PackingBin

rectangles = [(176, 183),(120, 72),(133, 119),(109, 50),(184, 106),(193, 165),(185, 175),(183, 135),(89, 138),(140, 199),(34, 58),(130, 178),(90, 107),(116, 181),(198, 95),(66, 89),(138, 96),(129, 43),(167, 165),(140, 133),(76, 159),(116, 186),(35, 144),(86, 82),(144, 46)
]
bins = [(300, 450,2), (200, 150,6), (400, 300,5)]

packer = newPacker(bin_algo=PackingBin.Global, rotation=True)

# Add the rectangles to packing queue
for index,r in enumerate(rectangles):
	packer.add_rect(*r,rid=index)

# Add the bins where the rectangles will be placed
for index,b in enumerate(bins):
	packer.add_bin(*b,bid=index)

# Start packing
packer.pack()

def plt_txt(rect,index_str,color="blue"):
    centx=rect.x+rect.width/2
    centy=rect.y+rect.height/2
    # plt.text(centx, centx, index_str, fontsize=9, color=color, ha='center', va='bottom')
    plt.text(centx, centy, f"{index_str}\n{rect.width}x{rect.height}", fontsize=9, color=color, ha='center', va='center')

# 可视化输出
import matplotlib.pyplot as plt



for index,item in enumerate(packer):
    fig, ax = plt.subplots()
    bin_rect=item._surface

    
    plt_txt(bin_rect,str(item.bid),color="red")

    ax.add_patch(plt.Rectangle((bin_rect.x, bin_rect.y), bin_rect.width, bin_rect.height, edgecolor='green', fill=False))


    for rect in item:
        ax.add_patch(plt.Rectangle((rect.x, rect.y), rect.width, rect.height, edgecolor='red', fill=False))
        plt_txt(rect,str(rect.rid))
    plt.axis('equal')
    file_path=f"rect_{index}_{item.bid}.png"
    plt.savefig(file_path)
    print(f"保存图片到 {file_path}")
    plt.close()
    
    

