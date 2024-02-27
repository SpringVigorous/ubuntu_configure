from itertools import count
from sys import meta_path
from matplotlib.pyplot import axis
import pandas as pd
import json
from os import path, system


def read_json(filefullpath: str, showHandle: bool = False):
    with open(filefullpath, "rb") as f:
        data = json.loads(f.read())
    fileItem = pd.json_normalize(data, max_level=10, errors="ignore")
    fileItem["fileID"] = [f"file-{x}" for x in range(len(fileItem.index))]

    vecDraw = []
    vecBlock = []
    vecHandle = []
    drawNum = 0
    blockNum = 0
    handleNum = 0
    for _, draw_row in fileItem.iterrows():
        draw = pd.json_normalize(
            draw_row["Drawings"], max_level=10, errors="ignore")
        draw["fileID"] = draw_row["fileID"]
        draw["drawID"] = [
            f"draw-{x}" for x in range(drawNum, drawNum+len(draw.index))]
        drawNum += len(draw.index)

        for _, block_row in draw.iterrows():
            block = pd.json_normalize(
                block_row["SubBlock"], max_level=10, errors="ignore")
            block["fileID"] = block_row["fileID"]
            block["drawID"] = block_row["drawID"]
            block["blockID"] = [
                f"block-{x}" for x in range(blockNum, blockNum+len(block.index))]
            blockNum += len(block.index)

            if showHandle:
                for _, handle_row in block.iterrows():
                    if "Handles" not in handle_row.index:
                        continue
                    if handle_row.hasnans:
                        continue

                    handles = handle_row["Handles"]

                    for val in handles:
                        handle = {
                            "Handle": [json.dumps(val)],
                            "fileID": [handle_row["fileID"]],
                            "drawID": [handle_row["drawID"]],
                            "blockID":  [handle_row["blockID"]],
                            "handleID": [f"handle-{handleNum}"],
                        }
                        handleNum += 1
                        handleframe = pd.DataFrame(handle)
                        vecHandle.append(handleframe)

            #去除
            block.drop(["Handles"], inplace=True, axis=1, errors="ignore")
            vecBlock.append(block)

        #去除
        draw.drop(["SubBlock"], inplace=True, axis=1, errors="ignore")
        vecDraw.append(draw)
    #去除
    fileItem.drop(["Drawings"], inplace=True, axis=1, errors="ignore")

    drawItem = pd.concat(vecDraw)
    blockItem = pd.concat(vecBlock)
    handleItem = pd.concat(vecHandle) if len(vecHandle) > 0 else None
    # 输出到excel文档
    (filePath, __) = path.splitext(filefullpath)
    outPath = f"{filePath}-tab.xlsx"
    with pd.ExcelWriter(outPath) as writer:
        fileItem.to_excel(writer, sheet_name="file")
        drawItem.to_excel(writer, sheet_name="Drawings")
        blockItem.to_excel(writer, sheet_name="SubBlocks")
        if not handleItem is None:
            handleItem.to_excel(writer, sheet_name="Handles")

    print(f"输出文件{outPath}")
    system(outPath)


read_json(r"E:\BIM\baijiayun\dispatch\drawing_recogniton_dispatch\cache_data\result_data_cache\20221217\1142\Drawing.json",False)
