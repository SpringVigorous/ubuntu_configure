#pragma once
#ifndef __UTILITIES_CEREAL_UTILITY_H__
#define __UTILITIES_CEREAL_UTILITY_H__
#include <cereal/cereal.hpp> // 引入cereal核心头文件（关键）
#include <cereal/types/memory.hpp>
#include <cereal/types/polymorphic.hpp>
#include <cereal/types/string.hpp>

//多种方式
#include <cereal/archives/json.hpp>
#include <cereal/archives/binary.hpp>
#include <cereal/archives/xml.hpp>
#include <memory>
#include <istream>
#include <ostream>

#include <fstream>
#include "utilities/utilities_macro.h"
#include <filesystem>
#include <concepts>

_UTILITIES_BEGIN_
using filesystem_path = std::filesystem::path;

template <class Archive,class T>
void save_data(const T& data, std::ostream& file) {

    Archive archive(file);
    // 序列化data对象
    archive(data);

}
template <class Archive, class T>
void load_data( T& data, std::istream& file) {
    Archive archive(file);
    // 序列化data对象
    archive(data);
}

template <class T>
void save_data_to_binary(const T& data, std::ostream& file) {
    save_data<cereal::BinaryOutputArchive>(data, file);

}

template <class T>
void load_data_from_binary(T& data, std::istream& file) {
    load_data<cereal::BinaryInputArchive>(data, file);
}


template <class T>
void load_data_from_xml(T& data, std::istream& file) {
    load_data<cereal::XMLInputArchive>(data, file);
}

template <class T>
void save_data_to_xml(const T& data, std::ostream& file) {
    save_data<cereal::XMLOutputArchive>(data, file);
}

template <class T>
void save_data_to_json(const T& data, std::ostream& file) {
    save_data<cereal::JSONOutputArchive>(data, file);
}
template <class T>
void load_data_from_json(T& data, std::istream& file) {
    load_data<cereal::JSONInputArchive>(data, file);
}

// 定义概念，限制类型必须是 const char*, std::string 或 std::filesystem::path,也包含 const char[N]
template<typename T>
concept StringLike =
(std::is_same_v<std::remove_cvref_t<T>, const char*> ||  // 匹配const char*
    std::is_same_v<std::remove_cvref_t<T>, std::string> ||  // 匹配std::string
    std::is_same_v<std::remove_cvref_t<T>, std::filesystem::path> ||  // 匹配path
    (std::is_array_v<std::remove_cvref_t<T>> &&  // 匹配const char[N]数组（字符串常量）
        std::is_same_v< std::remove_cvref_t<std::remove_all_extents_t<std::remove_cvref_t<T>>>, char>));


// 模板函数 as_string，使用概念约束
template <StringLike T>
std::string as_string(const T& value) {
    if constexpr (std::is_same_v<std::remove_cvref_t<T>, const char*> ||
        (std::is_array_v<std::remove_cvref_t<T>> &&  // 匹配const char[N]数组（字符串常量）
            std::is_same_v< std::remove_cvref_t<std::remove_all_extents_t<std::remove_cvref_t<T>>>, char>)) {
        // 处理const char*或const char[N]（字符串常量）
        return std::string(value);
    }
    else if constexpr (std::same_as<T, std::string>) {
        return value;              // std::string 直接返回
    }
    else if constexpr (std::same_as<T, std::filesystem::path>) {
        return value.string();     // std::filesystem::path 返回其字符串形式
    }
    else
    {
        return "";
    }
}
//template <std::size_t N>
//std::string as_string(const char(&str)[N]) {
//    return std::string(str); // 构造自固定大小的字符数组
//}


template <class T, StringLike U>
void load_data_from_binary(T& data,  const U& file_path) {
    // 创建输入文件流
    std::ifstream file(as_string(file_path), std::ios::binary);
    load_data_from_binary(data, file);
}
template <class T, StringLike U>
void save_data_to_binary(const T& data,  const U& file_path) {
    // 创建输出文件流
    std::ofstream file(as_string(file_path), std::ios::binary);
    save_data_to_binary(data, file);

}

template <class T, StringLike U>
void save_data_to_xml(const T& data, const U& file_path) {
    // 创建输出文件流
    std::ofstream file(as_string(file_path));
    save_data_to_xml(data, file);
}
template <class T, StringLike U>
void load_data_from_xml(T& data,  const U& file_path) {
    // 创建输入文件流
    std::ifstream file(as_string(file_path));
    load_data_from_xml(data, file);
}
template <class T, StringLike U>
void save_data_to_json(const T& data,  const U& file_path) {
    // 创建输出文件流
    std::ofstream file(as_string(file_path));
    save_data_to_json(data, file);
}
template <class T, StringLike U>
void load_data_from_json(T& data,  const U& file_path) {
    // 创建输入文件流
    std::ifstream file(as_string(file_path));
    load_data_from_json(data, file);
}



_UTILITIES_END_





#endif