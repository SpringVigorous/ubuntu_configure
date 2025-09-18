#include <gtest/gtest.h>
#include <vector>
#include "joy_utility/interface/serialize_interface.h"
#include "joy_utility/interface/data_node_base.h"
#include "joy_utility/kenels/hobject.h"


#include "joy_utility/tools/import_export_tools.h"
#include "joy_utility/tools/string_tools.h"



#include "environment.hxx"
#include <concepts>
#include <string>
#include <filesystem>
#include <iostream>



// 调整概念：同时兼容const char*和const char数组（字符串常量）
template<typename T>
concept StringLike =
(std::is_same_v<std::remove_cvref_t<T>, const char*> ||  // 匹配const char*
    std::is_same_v<std::remove_cvref_t<T>, std::string> ||  // 匹配std::string
    std::is_same_v<std::remove_cvref_t<T>, std::filesystem::path> ||  // 匹配path
    (std::is_array_v<std::remove_cvref_t<T>> &&  // 匹配const char[N]数组（字符串常量）
    std::is_same_v< std::remove_cvref_t<std::remove_all_extents_t<std::remove_cvref_t<T>>>, char>));

// 辅助工具：将数组/指针统一转换为const char*
template<typename T>
const char* to_const_char_ptr(const T& input) {
    if constexpr (std::is_array_v<std::remove_cvref_t<T>>) {
        return input;  // 数组衰减为指针
    }
    else {
        return input;  // 本身就是const char*
    }
}

// 转换为std::string的模板函数
template<StringLike T>
std::string to_string(const T& input) {
    if constexpr (std::is_same_v<std::remove_cvref_t<T>, const char*> ||
        (std::is_array_v<std::remove_cvref_t<T>> &&  // 匹配const char[N]数组（字符串常量）
            std::is_same_v< std::remove_cvref_t<std::remove_all_extents_t<std::remove_cvref_t<T>>>, char>)) {
        // 处理const char*或const char[N]（字符串常量）
        return std::string(input);
        //return std::string(to_const_char_ptr(input));
    }
    else if constexpr (std::is_same_v<std::remove_cvref_t<T>, std::string>) {
        // 处理std::string
        return input;
    }
    else if constexpr (std::is_same_v<std::remove_cvref_t<T>, std::filesystem::path>) {
        // 处理filesystem::path
        return input.string();
    }
}


TEST(joy_utility,test_string ) {

    const char* c_str = "Hello, const char*";
    std::string std_str = "Hello, std::string";
    std::filesystem::path fs_path = "/usr/local";
    auto literal = "husky";  // 类型是const char[6]（字符串常量）

    // 测试转换
    std::cout << to_string(c_str) << std::endl;    // 正常
    std::cout << to_string(std_str) << std::endl;  // 正常
    std::cout << to_string(fs_path) << std::endl;  // 正常
    std::cout << to_string(literal) << std::endl;  // 字符串常量（const char[6]）也能正常转换
    std::cout << to_string("direct literal") << std::endl;  // 直接传递字符串字面量

}