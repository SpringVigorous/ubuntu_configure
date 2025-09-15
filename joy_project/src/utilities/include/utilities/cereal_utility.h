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
#include <fstream>
#include "utilities/utilities_macro.h"


_UTILITIES_BEGIN_


template <class Archive,class T>
void save_data(const T& data, std::ofstream& file) {

    Archive archive(file);
    // 序列化data对象
    archive(data);

}
template <class Archive, class T>
void load_data( T& data, std::ifstream& file) {
    Archive archive(file);
    // 序列化data对象
    archive(data);
}

template <class T>
void save_data_to_binary(const T& data, std::ofstream& file) {
    save_data<cereal::BinaryOutputArchive>(data, file);

}

template <class T>
void load_data_from_binary(T& data, std::ifstream& file) {
    load_data<cereal::BinaryInputArchive>(data, file);
}


template <class T>
void save_data_to_binary(const T& data, const std::string& filename) {
    // 创建输出文件流
    std::ofstream file(filename, std::ios::binary);
    save_data_to_binary(data, file);

}

template <class T>
void load_data_from_binary(T& data,const std::string& filename) {
    // 创建输入文件流
    std::ifstream file(filename, std::ios::binary);
    load_data_from_binary(data, file);
}

template <class T>
void save_data_to_xml(const T& data, std::ofstream& file) {
    save_data<cereal::XMLOutputArchive>(data, file);
}
template <class T>
void load_data_from_xml(T& data, std::ifstream& file) {
    load_data<cereal::XMLInputArchive>(data, file);
}
template <class T>
void save_data_to_xml(const T& data, const std::string& filename) {
    // 创建输出文件流
    std::ofstream file(filename);
    save_data_to_xml(data, file);
}
template <class T>
void load_data_from_xml(T& data, const std::string& filename) {
    // 创建输入文件流
    std::ifstream file(filename);
    load_data_from_xml(data, file);
}
template <class T>
void save_data_to_json(const T& data, std::ofstream& file) {
    save_data<cereal::JSONOutputArchive>(data, file);
}
template <class T>
void load_data_from_json(T& data, std::ifstream& file) {
    load_data<cereal::JSONInputArchive>(data, file);
}
template <class T>
void save_data_to_json(const T& data, const std::string& filename) {
    // 创建输出文件流
    std::ofstream file(filename);
    save_data_to_json(data, file);
}
template <class T>
void load_data_from_json(T& data, const std::string& filename) {
    // 创建输入文件流
    std::ifstream file(filename);
    load_data_from_json(data, file);
}




_UTILITIES_END_





#endif