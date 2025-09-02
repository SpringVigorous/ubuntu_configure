
#include <iostream>
#include <locale>
#include <codecvt>
#include <iconv.h>
#include <memory_resource>
// #define USE_WSTRING_CONVERT
#include <cctype>
#include "cpp-base64/base64.h"
#include "cpp-base64/base64.cpp"

#include <boost/uuid/uuid.hpp>
#include <boost/uuid/uuid_generators.hpp>
#include <boost/uuid/uuid_io.hpp>

#include "joy_utility/tools/string_tools.h"
//#ifdef _DEBUG
//#define new DEBUG_NEW
//#endif


#ifdef USE_WSTRING_CONVERT
// 定义gbk编码的codecvt
class codecvt_gbk : public std::codecvt_byname<wchar_t, char, std::mbstate_t>
{
public:
    codecvt_gbk() : codecvt_byname("GBK") {}
};

// 定义中文编码的codecvt
class chs_codecvt : public std::codecvt_byname<wchar_t, char, std::mbstate_t>
{
public:
    chs_codecvt() : codecvt_byname("zh_CN") {}
};
#else
#include <boost/locale.hpp>
namespace boost_convert = boost::locale::conv;
// boost::locale::conv::utf_to_utf<> 是全能的
#endif // USE_WSTRING_CONVERT
_JOY_UTILITY_BEGIN_

template <class DestType, class SrcType>
std::basic_string<DestType> convert_to(const std::basic_string<SrcType>& src)
{
    using DestStringType = std::basic_string<DestType>;
    try
    {
#ifdef USE_WSTRING_CONVERT
        return DestStringType{};
#else
        return boost_convert::utf_to_utf<DestType>(src);
#endif
    }
    catch (...)
    {
        return DestStringType{};
    }
}

std::string string_tools::gbk_to_utf8(const std::string& gbk_str)
{
#ifdef USE_WSTRING_CONVERT
    return unicode_to_utf8(string_tools::gbk_to_unicode(gbk_str));
#else
    return boost_convert::to_utf<char>(gbk_str, "gbk");
    return boost_convert::between(gbk_str, "utf-8", "gbk");
    // 将gbk字符串转换为unicode字符串
#endif
}

std::string string_tools::utf8_to_gbk(const std::string& utf_str)
{
#ifdef USE_WSTRING_CONVERT
    return string_tools::unicode_to_gbk(utf8_to_unicode(utf_str));

#else
    return boost_convert::from_utf<char>(utf_str, "gbk");
    return boost_convert::between(utf_str, "gbk", "utf-8");

#endif

    // 将utf8字符串转换为gbk字符串
}

// 将unicode字符串转换为utf8字符串
std::string string_tools::unicode_to_utf8(const std::wstring& uicode_str)
{
#ifdef USE_WSTRING_CONVERT
    static std::wstring_convert<std::codecvt_utf8<wchar_t>> converter;
    return converter.to_bytes(uicode_str);
#else

    return boost_convert::from_utf<wchar_t>(uicode_str, "utf-8");
    return convert_to<char>(uicode_str);
#endif
}

// 将utf8字符串转换为unicode字符串
std::wstring string_tools::utf8_to_unicode(const std::string& utf_str)
{
#ifdef USE_WSTRING_CONVERT
    static std::wstring_convert<std::codecvt_utf8<wchar_t>> converter;
    return converter.from_bytes(utf_str);
#else

    return boost_convert::to_utf<wchar_t>(utf_str, "utf-8");
    return convert_to<wchar_t>(utf_str);
#endif
}
std::wstring string_tools::gbk_to_unicode(const std::string& gbk_str)
{
#ifdef USE_WSTRING_CONVERT
    static std::wstring_convert<chs_codecvt> converter;
    return converter.from_bytes(gbk_str);
#else
    return boost_convert::to_utf<wchar_t>(gbk_str, "gbk");
#endif
}

// 将unicode字符串转换为gbk字符串
std::string string_tools::unicode_to_gbk(const std::wstring& uicode_str)
{
#ifdef USE_WSTRING_CONVERT
    static std::wstring_convert<chs_codecvt> converter;
    return converter.to_bytes(uicode_str);
#else
    return boost_convert::from_utf<wchar_t>(uicode_str, "gbk");

#endif
}
std::wstring gbk_to_unicode_temp(const std::string& gbk_str)
{
    // 将gbk字符串转换为unicode字符串
    std::string strLocale = setlocale(LC_ALL, "");
    std::wstring ret;
    std::mbstate_t state{};
    const char* src = gbk_str.data();

    std::size_t len = std::mbsrtowcs(nullptr, &src, 0, &state);
    if (static_cast<std::size_t>(-1) != len)
    {
        const std::unique_ptr<wchar_t[]> buff(new wchar_t[len + 1]);
        len = std::mbsrtowcs(buff.get(), &src, len, &state);
        if (static_cast<std::size_t>(-1) != len)
        {
            ret.assign(buff.get(), len);
        }
    }
    setlocale(LC_ALL, strLocale.c_str());
    return ret;
}

std::string unicode_to_gbk_temp(const std::wstring& uicode_str)
{
    // 将unicode字符串转换为gbk字符串
    std::string strLocale = setlocale(LC_ALL, "");
    std::string ret;
    std::mbstate_t state{};
    const wchar_t* src = uicode_str.c_str();
    std::size_t len = std::wcsrtombs(nullptr, &src, 0, &state);
    if (static_cast<std::size_t>(-1) != len)
    {
        const std::unique_ptr<char[]> buff(new char[len + 1]);
        len = std::wcsrtombs(buff.get(), &src, len, &state);
        if (static_cast<std::size_t>(-1) != len)
        {
            ret.assign(buff.get(), len);
        }
    }
    setlocale(LC_ALL, strLocale.c_str());
    return ret;
}

// 定义缓冲区大小
#define BUFFER_SIZE 1024
int wstr_to_str(const wchar_t* in_wstr, char** out_str, const char* from_code, const char* to_code)
{
    // 初始化输出缓冲区
    size_t out_len = BUFFER_SIZE;
    *out_str = (char*)malloc(out_len);
    if (*out_str == NULL)
    {
        perror("Memory allocation failed");
        return -1;
    }
    memset(*out_str, 0, out_len);

    // 创建iconv描述符
    iconv_t cd = iconv_open(to_code, from_code);
    if (cd == (iconv_t)-1)
    {
        perror("iconv_open failed");
        free(*out_str);
        return -1;
    }

    // 输入数据结构
    char* in_buf = (char*)in_wstr;
    size_t in_left = wcslen(in_wstr) * sizeof(wchar_t); // 计算宽字符串长度（字节数）

    // 转换过程
    while (in_left > 0)
    {
        char* out_ptr = *out_str + strlen(*out_str);
        size_t out_left = out_len - strlen(*out_str);

        if (iconv(cd, (char**)&in_buf, &in_left, &out_ptr, &out_left) == (size_t)-1)
        {
            if (errno == E2BIG)
            { // 输出缓冲区太小
                out_len += BUFFER_SIZE;
                *out_str = (char*)realloc(*out_str, out_len);
                if (*out_str == NULL)
                {
                    perror("Memory reallocation failed");
                    iconv_close(cd);
                    return -1;
                }
                continue;
            }
            else
            {
                perror("iconv conversion failed");
                iconv_close(cd);
                free(*out_str);
                return -1;
            }
        }

        // 更新输出缓冲区的结束位置
        *out_str = (char*)realloc(*out_str, strlen(*out_str) + 1); // 确保分配正确的大小，并添加终止符
        if (*out_str == NULL)
        {
            perror("Memory reallocation failed");
            iconv_close(cd);
            return -1;
        }
    }

    // 关闭iconv描述符
    iconv_close(cd);

    return 0;
}

int str_to_wstr(const char* in_str, wchar_t** out_wstr, const char* from_code, const char* to_code)
{
    // 初始化输出缓冲区
    size_t out_len = BUFFER_SIZE * sizeof(wchar_t);
    *out_wstr = (wchar_t*)malloc(out_len);
    if (*out_wstr == NULL)
    {
        perror("Memory allocation failed");
        return -1;
    }
    memset(*out_wstr, 0, out_len);

    // 创建iconv描述符
    iconv_t cd = iconv_open(to_code, from_code);
    if (cd == (iconv_t)-1)
    {
        perror("iconv_open failed");
        free(*out_wstr);
        return -1;
    }

    // 输入数据结构
    char* in_buf = (char*)in_str;
    size_t in_left = strlen(in_str); // 计算窄字符串长度（字节数）

    // 转换过程
    while (in_left > 0)
    {
        wchar_t* out_ptr = *out_wstr + wcslen(*out_wstr);
        size_t out_left = (out_len - (wcslen(*out_wstr) * sizeof(wchar_t))) / sizeof(wchar_t); // 计算剩余宽字符空间数

        if (iconv(cd, (char**)&in_buf, &in_left, (char**)&out_ptr, &out_left) == (size_t)-1)
        {
            if (errno == E2BIG)
            { // 输出缓冲区太小
                out_len += BUFFER_SIZE * sizeof(wchar_t);
                *out_wstr = (wchar_t*)realloc(*out_wstr, out_len);
                if (*out_wstr == NULL)
                {
                    perror("Memory reallocation failed");
                    iconv_close(cd);
                    return -1;
                }
                continue;
            }
            else
            {
                perror("iconv conversion failed");
                iconv_close(cd);
                free(*out_wstr);
                return -1;
            }
        }

        // 更新输出缓冲区的结束位置
        *out_wstr = (wchar_t*)realloc(*out_wstr, ((wchar_t*)out_ptr - *out_wstr) * sizeof(wchar_t) + sizeof(wchar_t)); // 确保分配正确的大小，并添加终止符
        if (*out_wstr == NULL)
        {
            perror("Memory reallocation failed");
            iconv_close(cd);
            return -1;
        }
    }

    // 添加终止符
    *(*out_wstr + wcslen(*out_wstr)) = L'\0';

    // 关闭iconv描述符
    iconv_close(cd);

    return 0;
}

std::string str_to_str(const std::string& gbk_input, const char* from_code, const char* to_code)
{
    // 初始化iconv描述符
    iconv_t cd = iconv_open(to_code, from_code);
    if (cd == (iconv_t)-1)
    {
        throw std::runtime_error("初始化iconv失败");
    }

    // 为转换结果分配缓冲区
    size_t in_len = gbk_input.size();
    const char* in = gbk_input.c_str();
    size_t out_len = in_len * 4; // UTF-8可能需要更大的空间，这里假设每个GBK字符最多转换成4个字节的UTF-8
    std::string utf8_output(out_len, '\0');

    char* out = &utf8_output[0];
    size_t result_len;

    // 进行编码转换
    if (iconv(cd, (char**)&in, &in_len, &out, &out_len) == (size_t)-1)
    {
        iconv_close(cd);
        // throw std::runtime_error("GBK转UTF-8过程中发生错误");
    }

    // 调整输出字符串长度
    utf8_output.resize(utf8_output.size() - out_len);

    // 关闭iconv描述符
    iconv_close(cd);

    return utf8_output;
}

std::wstring str_to_wstr(std::string org_str, const char* from_code, const char* to_code)
{
    wchar_t* out_utf16 = NULL;
    if (0 == str_to_wstr(org_str.c_str(), &out_utf16, from_code, to_code))
    {
        return std::wstring(out_utf16, out_utf16 + wcslen(out_utf16));
        free(out_utf16);
    }
    return L"";
}

std::string wstr_to_str(std::wstring org_str, const char* from_code, const char* to_code)
{

    char* out_utf16 = NULL;
    if (0 == wstr_to_str(org_str.c_str(), &out_utf16, from_code, to_code))
    {
        return std::string(out_utf16, out_utf16 + strlen(out_utf16));
        free(out_utf16);
    }

    return "";
}

std::u16string string_tools::utf8_to_utf16(const std::string& utf8_str)
{
    return convert_to<char16_t>(utf8_str);
}
std::string string_tools::utf16_to_utf8(const std::u16string& utf16_str)
{
    return convert_to<char>(utf16_str);
}
std::u32string string_tools::utf8_to_utf32(const std::string& utf8_str)
{
    return convert_to<char32_t>(utf8_str);
}
std::string string_tools::utf32_to_utf8(const std::u32string& utf32_str)
{
    return convert_to<char>(utf32_str);
}
std::u32string string_tools::utf16_to_utf32(const std::u16string& utf16_str)
{
    return convert_to<char32_t>(utf16_str);
}
std::u16string string_tools::utf32_to_utf16(const std::u32string& utf32_str)
{
    return convert_to<char16_t>(utf32_str);
}
std::u16string string_tools::utf8_to_utf16(const std::u8string& utf32_str)
{
    return convert_to<char16_t>(utf32_str);
}
std::u32string string_tools::utf8_to_utf32(const std::u8string& utf8_str)
{
    return convert_to<char32_t>(utf8_str);
}
std::u8string string_tools::utf8_to_utf8(const std::string& utf8_str)
{
    return std::u8string(utf8_str.begin(), utf8_str.end());
}
std::string string_tools::utf8_to_utf8(const std::u8string& utf8_str)
{
    return std::string(utf8_str.begin(), utf8_str.end());
}
std::string string_tools::to_base64(const std::string& str)
{

    return base64_encode(str);
}
std::string string_tools::from_base64(const std::string& str)
{
    return base64_decode(str);

}
std::string string_tools::generate_guid()
{
    boost::uuids::uuid uuid = boost::uuids::random_generator()();

    return boost::uuids::to_string(uuid);

}
bool string_tools::is_equal_ignore_case(const std::string& a, const std::string& b) {
    // 长度不同直接返回false（优化效率）
    if (a.size() != b.size()) {
        return false;
    }
    // 逐个字符转换为小写后比较
    for (size_t i = 0; i < a.size(); ++i) {
        // 转换为unsigned char避免符号问题（处理特殊字符）
        if (tolower(static_cast<unsigned char>(a[i])) !=
            tolower(static_cast<unsigned char>(b[i]))) {
            return false;
        }
    }
    return true;
}




_JOY_UTILITY_END_