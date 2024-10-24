
from collections import namedtuple


JsonData=namedtuple("JsonData",["theme","json_data"]) # str,dict


RawData=namedtuple("RawDataQueue",["file_path","json_data"]) #str,dict
NotesData=namedtuple("NotesData",["theme","pd"])  #  str, pd

ThemesData=namedtuple("ThemesData",["file_path","datas"]) # str,list[NotesData]
CommentData=namedtuple("CommentData",["writer","theme","html","note_id","note_title"]) # str,dict