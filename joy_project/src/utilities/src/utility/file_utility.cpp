
#include "utilities/utility/file_utility.h"

//#ifdef _DEBUG
//#define new DEBUG_NEW
//#endif
_UTILITIES_BEGIN_


// 写入UTF-8 BOM（0xEF 0xBB 0xBF）
void write_utf8_bom(std::ofstream& file) {
    if (!file.is_open()) return;
    const unsigned char bom[3] = { 0xEF, 0xBB, 0xBF };
    file.write(reinterpret_cast<const char*>(bom), 3);
}
//是否是BOM开头
bool load_utf8_bom(std::ifstream& file) {
    if (!file.is_open()) return false;

    // 1. 检查并跳过UTF-8-SIG的BOM
    unsigned char bom[3] = { 0 };
    file.read(reinterpret_cast<char*>(bom), sizeof(bom));
    if (!(bom[0] == 0xEF && bom[1] == 0xBB && bom[2] == 0xBF)) {
        // 若不是UTF-8-SIG，将文件指针移回开头
        file.seekg(0);
        return false;
    }
    return true;
}








_UTILITIES_END_