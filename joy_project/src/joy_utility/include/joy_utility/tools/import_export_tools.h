#pragma once
#ifndef __JOY_UTILITY_IMPORT_EXPORT_TOOLS_H__
#define __JOY_UTILITY_IMPORT_EXPORT_TOOLS_H__
#include <string>
#include <memory>
#include <string>
#include "joy_utility/joy_utility_macro.h"
#include "joy_utility/interface/serialize_interface.h"
#include <json/json.h>
#include "joy_utility/interface/json_archive.h"
#include "tinyxml2.h"
#include "joy_utility/interface/xml_archive.h"
#include <utility>
#include <fstream>
#include <ios>
#include <iostream>
#include <stdexcept>
_JOY_UTILITY_BEGIN_

JOY_UTILITY_API void test_export_xml(tinyxml2::XMLElement* root);


template<class T, class Archive>
bool read_members(T& data, Archive& ar)
{
    data.serialize_members(ar);
    return true;
}
template<class T, class Archive>
bool write_members(const T& data, Archive& ar)
{
    const_cast<T&>(data).serialize_members(ar);
    return true;
}
template<class T>
bool import_from_json_file(const std::string& file_path, T& data)
{
    if constexpr (has_serialize_members_func_v<T>)
    {
        std::ifstream file(file_path, std::ios::in);
        if (!file.is_open())
            return false;
        Json::Value json_obj;
        JSONCPP_STRING errs;
        Json::CharReaderBuilder readerBuilder;
        bool success = Json::parseFromStream(readerBuilder, file, &json_obj, &errs);
        file.close();
        if (!success)
            return false; // json内容必须为utf-8编码
        json_archive ar(&json_obj, false);
        read_members(data, ar);
        return true;
    }
    else
    {
        return false;
    }
}
template<class T>
bool export_to_json_file(const T& data, const std::string& file_path)
{
    if constexpr (has_serialize_members_func_v<T>)
    {
        Json::Value json;
        json_archive serialize_ar(&json, true);
        write_members(data, serialize_ar);
        //std::string std_res = json.toStyledString();
        // 2. 生成UTF-8 JSON字符串
        Json::StreamWriterBuilder builder;
        builder["emitUTF8"] = true;
        std::string res = Json::writeString(builder, json);
        std::ofstream new_file(file_path, std::ios::out);
        if (!new_file.is_open() && !new_file.good()) return false;
        new_file.write(res.c_str(), res.length());
        new_file.close();
        return true;
    }
    else
    {
        return false;
    }
}
template<class T>
bool import_from_xml_file(const std::string& file_path, T& data)
{
    if constexpr (has_serialize_members_func_v<T>)
    {
        tinyxml2::XMLDocument doc;
        if (tinyxml2::XML_SUCCESS != doc.LoadFile(file_path.c_str())) return false;

        //doc.SaveFile("F:/test/joy_project/test/data/joy_utility/test_serialize_1.xml");

        tinyxml2::XMLElement* xml = doc.FirstChildElement("xml_root"); // 写入的时候最外层会强制加上此节点，否则无法序列化
        if (!xml) return false;


        xml_archive ar(xml, false);

        read_members(data, ar);
        
        //doc.SaveFile("F:/test/joy_project/test/data/joy_utility/test_serialize_2.xml");
        return true;
    }
    else
    {
        return false;
    }
}


template<class T>
bool export_to_xml_file(const T& data, const std::string& file_path)
{
    if constexpr (has_serialize_members_func_v<T>)
    {

        tinyxml2::XMLDocument doc;
        tinyxml2::XMLDeclaration* declare=doc.NewDeclaration();
        doc.LinkEndChild(declare);

        tinyxml2::XMLElement* root_node = doc.NewElement("xml_root"); // 写入的时候最外层会强制加上此节点，否则无法序列化
        if (!root_node) return false;
        doc.LinkEndChild(root_node);


        xml_archive ar(root_node, true);
        write_members(data, ar);

        //test_export_xml(root_node);

        tinyxml2::XMLError err = doc.SaveFile(file_path.c_str());
        if (tinyxml2::XML_SUCCESS != err)
            return false;

        return true;
    }
    else
    {
        return false;
    }
}
template<class T>
bool import_from_bin_file(const std::string& file_path, T& data)
{
    if constexpr (has_serialize_members_func_v<T>)
    {
        std::ifstream file(file_path, std::ios::in);
        if (!file.is_open())
            return false;
        Json::Value json_obj;
        JSONCPP_STRING errs;
        Json::CharReaderBuilder readerBuilder;
        bool success = Json::parseFromStream(readerBuilder, file, &json_obj, &errs);
        file.close();
        if (!success)
            return false; 
        json_archive ar(&json_obj, false);
        data.serialize_members(ar);
        return true;
    }
    else
    {
        return false;
    }
}
template<class T>
bool export_to_bin_file(const T& data, const std::string& file_path)
{
    if constexpr (has_serialize_members_func_v<T>)
    {
        Json::Value json;
        json_archive serialize_ar(&json, true);
        const_cast<T&>(data).serialize_members(serialize_ar);
        // 2. 生成UTF-8 JSON字符串
        Json::StreamWriterBuilder builder;
        builder["emitUTF8"] = true;
        std::string res = Json::writeString(builder, json);
        //std::string res = json.toStyledString();
        std::ofstream new_file(file_path, std::ios::out);
        if (!new_file.is_open() && !new_file.good()) return false;
        new_file.write(res.c_str(), res.length());
        new_file.close();
        return true;
    }
    else
    {
        return false;
    }
}

_JOY_UTILITY_END_
#endif