#include <ft2build.h>
#include FT_FREETYPE_H
#include <iostream>

int main()
{
    // 初始化Freetype库
    FT_Library library;
    if (FT_Init_FreeType(&library))
    {
        std::cerr << "Error: could not init FreeType library" << std::endl;
        return -1;
    }

    // 加载字体文件
    FT_Face face;
    const char * font_file = "path/to/your/font.ttf";
    if (FT_New_Face(library, font_file, 0, &face))
    {
        std::cerr << "Error: failed to load font" << std::endl;
        FT_Done_FreeType(library);
        return -1;
    }

    // 设置字体大小
    FT_Set_Pixel_Sizes(face, 0, 32); // 设置为32像素高

    // 计算字符串的尺寸
    const char * text = "Hello, World!";
    int pen_x = 0;
    int pen_y = 0;
    int max_width = 0;
    int max_height = 0;

    for (int i = 0; text[i]; i++)
    {
        // 加载字符
        if (FT_Load_Char(face, text[i], FT_LOAD_RENDER))
        {
            std::cerr << "Error: failed to load glyph" << std::endl;
            continue;
        }

        // 计算宽度
        max_width += face->glyph->bitmap.width + face->glyph->advance.x >> 6;
        // 更新高度
        if (face->glyph->bitmap.rows > max_height)
        {
            max_height = face->glyph->bitmap.rows;
        }
    }

    // 清理
    FT_Done_Face(face);
    FT_Done_FreeType(library);

    // 输出结果
    std::cout << "The size of the text is: " << max_width << " x " << max_height << std::endl;

    return 0;
}