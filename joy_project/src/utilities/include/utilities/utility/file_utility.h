#pragma once
#ifndef __UTILITIES_FILE_UTILITY_H__
#define __UTILITIES_FILE_UTILITY_H__
#include <fstream>
#include "utilities/utilities_macro.h"





_UTILITIES_BEGIN_




// 写入UTF-8 BOM（0xEF 0xBB 0xBF）
UTILITIES_API void write_utf8_bom(std::ofstream& file);
//是否是BOM开头
UTILITIES_API bool load_utf8_bom(std::ifstream& file);





_UTILITIES_END_
#endif
