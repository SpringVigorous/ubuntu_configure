#pragma once
#ifndef __JOY_UTILITY_STRING_TOOLS_H__
#define __JOY_UTILITY_STRING_TOOLS_H__

#include <string>
#include <format>
#include <type_traits>
#include <concepts>
#include <array>
#include <algorithm>
#include "joy_utility/joy_utility_macro.h"

_JOY_UTILITY_BEGIN_

template <typename T>
std::string format_with_precision(T value) {
    if constexpr (std::floating_point<T>) {  // 编译时检查是否为浮点数
        return std::format("{:.6f}", value);  // 保留6位小数
    }
    else {
        return std::format("{}", value);      // 非浮点数默认格式化
    }
};


class JOY_UTILITY_API string_tools
{
private:
    string_tools() = delete;
    ~string_tools() = delete;

public:
    //! 将gbk格式的字符串转换为utf8格式
    static std::string gbk_to_utf8(const std::string& gbk_str);

    //! 将utf8格式的字符串转换为gbk格式
    static std::string utf8_to_gbk(const std::string& utf_str);

    //! 将unicode格式的字符串转换为utf8格式
    static  std::string unicode_to_utf8(const std::wstring& uicode_str);

    //! 将utf8格式的字符串转换为unicode格式
    static std::wstring utf8_to_unicode(const std::string& utf_str);

    //! 将gbk格式的字符串转换为unicode格式
    static std::wstring gbk_to_unicode(const std::string& gbk_str);

    //! 将unicode格式的字符串转换为gbk格式
    static std::string unicode_to_gbk(const std::wstring& uicode_str);

    static std::u16string utf8_to_utf16(const std::string& utf32_str);

    static std::string utf16_to_utf8(const std::u16string& utf16_str);

    static std::u32string utf8_to_utf32(const std::string& utf8_str);

    static  std::string utf32_to_utf8(const std::u32string& utf32_str);

    static  std::u32string utf16_to_utf32(const std::u16string& utf16_str);

    static  std::u16string utf32_to_utf16(const std::u32string& utf32_str);

    static  std::u16string utf8_to_utf16(const std::u8string& utf32_str);
    static  std::u32string utf8_to_utf32(const std::u8string& utf8_str);
    static  std::u8string utf8_to_utf8(const std::string& utf8_str);
    static  std::string utf8_to_utf8(const std::u8string& utf8_str);

    static std::string to_base64(const std::string& str);
    static std::string from_base64(const std::string& str);

    static std::string generate_guid();


    template<class T>
    static std::string num_to_string(T value)
    {
        return format_with_precision(value);
    }

    static bool is_equal_ignore_case(const std::string& value1, const std::string& value2);



    template<const char*... Strs>
    consteval auto concat_const() {
        constexpr size_t total_len = (0 + ... + (std::char_traits<char>::length(Strs)));
        std::array<char, total_len + 1> res{};
        size_t pos = 0;

        // 折叠表达式展开：逐个复制字符串
        ([&] {
            for (size_t i = 0; Strs[i]; ++i)
                res[pos++] = Strs[i];
            }(), ...);

        res[pos] = '\0';
        return res;
    }

};








_JOY_UTILITY_END_
#endif
