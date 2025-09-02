
#include "json/json.h"
#include "joy_utility/interface/json_archive.h"

#include "joy_utility/tools/string_tools.h"
#include <vector>
//#ifdef _DEBUG
//#define new DEBUG_NEW
//#endif
_JOY_UTILITY_BEGIN_


json_archive::json_archive(Json::Value* json, bool is_storing/* = false*/)
    : m_json(json), m_is_storing(is_storing), m_json_array_reading_index(0)
{
    clear_parent_nodes_cache();
}

json_archive::~json_archive()
{

}

bool json_archive::is_storing()
{
    return m_is_storing;
}

void json_archive::read_impl(const std::string& name, const serialize_flag& data)
{
    if (serialize_flag::sub_obj_bg == data)
    {
        if (m_json->isArray())
        {
            Json::Value* tmp_json = m_json;
            m_json = &((*m_json)[m_json_array_reading_index++]);
            m_parent_nodes.push(std::make_pair(tmp_json, m_json_array_reading_index));
        }
        else
        {
            // 没有相应的成员会崩溃
            if (!m_json->isMember(name)) return;

            m_parent_nodes.push(std::make_pair(m_json, 0));
            m_json_array_reading_index = 0;
            m_json = &((*m_json)[name]);
        }
    }
    else if (serialize_flag::sub_obj_ed == data)
    {
        if (!m_parent_nodes.empty())
        {
            std::pair<Json::Value*, int> top_item = m_parent_nodes.top();
            m_json = top_item.first;
            m_json_array_reading_index = top_item.second;
            m_parent_nodes.pop();
        }
    }
    else if (serialize_flag::array_bg == data)
    {
        if (m_json->isArray())
        {
            Json::Value* tmp_json = m_json;
            m_json = &((*m_json)[m_json_array_reading_index++]);
            m_parent_nodes.push(std::make_pair(tmp_json, m_json_array_reading_index));
        }
        else
        {
            // 没有相应的成员会崩溃
            if (!m_json->isMember(name)) return;

            m_parent_nodes.push(std::make_pair(m_json, 0));
            m_json_array_reading_index = 0;
            m_json = &((*m_json)[name]);
        }
    }
    else if (serialize_flag::array_ed == data)
    {
        if (!m_parent_nodes.empty())
        {
            std::pair<Json::Value*, int> top_item = m_parent_nodes.top();
            m_json = top_item.first;
            m_json_array_reading_index = top_item.second;
            m_parent_nodes.pop();
        }
    }
    else
    {
        // nothing;
    }
}

void json_archive::read_impl(const std::string& name, bool& data)
{
    if (m_json->isArray())
        data = (*m_json)[m_json_array_reading_index++].asBool();
    else if (m_json->isMember(name))
        data = (*m_json)[name].asBool();
}

void json_archive::read_impl(const std::string& name, char& data)
{
    if (m_json->isArray())
        data = (char)(*m_json)[m_json_array_reading_index++].asInt();
    else if (m_json->isMember(name))
        data = (char)(*m_json)[name].asInt();
}

void json_archive::read_impl(const std::string& name, unsigned char& data)
{
    if (m_json->isArray())
        data = (unsigned char)(*m_json)[m_json_array_reading_index++].asUInt();
    else if (m_json->isMember(name))
        data = (unsigned char)(*m_json)[name].asUInt();
}

void json_archive::read_impl(const std::string& name, wchar_t& data)
{
    if (m_json->isArray())
        data = (wchar_t)(*m_json)[m_json_array_reading_index++].asInt();
    else if (m_json->isMember(name))
        data = (wchar_t)(*m_json)[name].asUInt();
}

void json_archive::read_impl(const std::string& name, short& data)
{
    if (m_json->isArray())
        data = (*m_json)[m_json_array_reading_index++].asInt();
    else if (m_json->isMember(name))
        data = (*m_json)[name].asInt();
}

void json_archive::read_impl(const std::string& name, unsigned short& data)
{
    if (m_json->isArray())
        data = (*m_json)[m_json_array_reading_index++].asInt();
    else if (m_json->isMember(name))
        data = (*m_json)[name].asUInt();
}

void json_archive::read_impl(const std::string& name, int& data)
{
    if (m_json->isArray())
        data = (*m_json)[m_json_array_reading_index++].asInt();
    else if (m_json->isMember(name))
        data = (*m_json)[name].asInt();
}

void json_archive::read_impl(const std::string& name, unsigned int& data)
{
    if (m_json->isArray())
        data = (*m_json)[m_json_array_reading_index++].asInt();
    else if (m_json->isMember(name))
        data = (*m_json)[name].asUInt();
}

void json_archive::read_impl(const std::string& name, long& data)
{
    if (m_json->isArray())
        data = (long)(*m_json)[m_json_array_reading_index++].asInt64();
    else if (m_json->isMember(name))
        data = (long)(*m_json)[name].asInt64();
}

void json_archive::read_impl(const std::string& name, unsigned long& data)
{
    if (m_json->isArray())
        data = (unsigned long)(*m_json)[m_json_array_reading_index++].asUInt64();
    else if (m_json->isMember(name))
        data = (unsigned long)(*m_json)[name].asUInt64();
}

void json_archive::read_impl(const std::string& name, long long& data)
{
    if (m_json->isArray())
        data = (*m_json)[m_json_array_reading_index++].asInt64();
    else if (m_json->isMember(name))
        data = (*m_json)[name].asInt64();
}

void json_archive::read_impl(const std::string& name, unsigned long long& data)
{
    if (m_json->isArray())
        data = (*m_json)[m_json_array_reading_index++].asUInt64();
    else if (m_json->isMember(name))
        data = (*m_json)[name].asUInt64();
}

void json_archive::read_impl(const std::string& name, float& data)
{
    if (m_json->isArray())
        data = (*m_json)[m_json_array_reading_index++].asFloat();
    else if (m_json->isMember(name))
        data = (*m_json)[name].asFloat();
}

void json_archive::read_impl(const std::string& name, double& data)
{
    if (m_json->isArray())
        data = (*m_json)[m_json_array_reading_index++].asDouble();
    else if (m_json->isMember(name))
        data = (*m_json)[name].asDouble();
}

void json_archive::read_impl(const std::string& name, long double& data)
{
    if (m_json->isArray())
        data = (*m_json)[m_json_array_reading_index++].asDouble();
    else if (m_json->isMember(name))
        data = (*m_json)[name].asDouble();
}

void json_archive::read_impl(const std::string& name, std::string& data)
{
    std::string str_utf_8;
    if (m_json->isArray())
        str_utf_8 = (*m_json)[m_json_array_reading_index++].asString();
    else
        str_utf_8 = (*m_json)[name].asString();


    data = string_tools::utf8_to_gbk(str_utf_8);
}

void json_archive::read_impl(const std::string& name, char*& buffer, long& byte_count)
{
    safe_delete_array(buffer);
    byte_count = 0;

    std::string buffer_text;
    read_impl(name, buffer_text);

    auto base64_str = string_tools::from_base64(buffer_text);
    if (base64_str.empty()) return;
    byte_count = base64_str.size();
    buffer = new char[byte_count];
    for (unsigned int i = 0; i < base64_str.size(); ++i)
        buffer[i] = base64_str.at(i);
}

void json_archive::write_impl(const std::string& name, const serialize_flag& data)
{
    if (name.empty()) return;

    if (serialize_flag::sub_obj_bg == data)
    {
        Json::Value new_item(Json::objectValue);
        if (m_json->isArray())
        {
            // 数据中放对象时也要记住前一个数组对象
            Json::Value& tmp_json = m_json->append(new_item);
            int count = m_json->size();
            m_parent_nodes.push(std::make_pair(m_json, 0)); // 写入时不需要索引，直接给0
            m_json = &tmp_json;
        }
        else
        {
            m_parent_nodes.push(std::make_pair(m_json, 0)); // 写入时不需要索引，直接给0
            (*m_json)[name] = new_item;
            m_json = &((*m_json)[name]);
        }
    }
    else if (serialize_flag::sub_obj_ed == data)
    {
        // 数组时也压入元素了，因此也要弹出
        if (!m_parent_nodes.empty()/* && !m_json->isArray()*/)
        {
            std::pair<Json::Value*, int> top_item = m_parent_nodes.top();
            m_json = top_item.first;
            m_json_array_reading_index = top_item.second;
            m_parent_nodes.pop();
        }
    }
    else if (serialize_flag::array_bg == data)
    {
        Json::Value new_item(Json::arrayValue);
        if (m_json->isArray())
        {
            // 数据中放对象时也要记住前一个数组对象
            Json::Value& tmp_json = m_json->append(new_item);
            m_parent_nodes.push(std::make_pair(m_json, 0)); // 写入时不需要索引，直接给0
            m_json = &tmp_json;
            m_json_array_reading_index = 0;
        }
        else
        {
            m_parent_nodes.push(std::make_pair(m_json, 0)); // 写入时不需要索引，直接给0
            (*m_json)[name] = new_item;
            m_json = &((*m_json)[name]);
        }
    }
    else if (serialize_flag::array_ed == data)
    {
        // 数组时也压入元素了，因此也要弹出
        if (!m_parent_nodes.empty()/* && !m_json->isArray()*/)
        {
            std::pair<Json::Value*, int> top_item = m_parent_nodes.top();
            m_json = top_item.first;
            m_json_array_reading_index = top_item.second;
            m_parent_nodes.pop();
        }
    }
    else
    {
        // nothing;
    }
}

void json_archive::write_impl(const std::string& name, const bool& data)
{
    Json::Value new_item(data);
    if (m_json->isArray())
        m_json->append(new_item);
    else
        (*m_json)[name] = new_item;
}

void json_archive::write_impl(const std::string& name, const char& data)
{
    Json::Value new_item((int)data);
    if (m_json->isArray())
        m_json->append(new_item);
    else
        (*m_json)[name] = new_item;
}

void json_archive::write_impl(const std::string& name, const unsigned char& data)
{
    Json::Value new_item((unsigned int)data);
    if (m_json->isArray())
        m_json->append(new_item);
    else
        (*m_json)[name] = new_item;
}

void json_archive::write_impl(const std::string& name, const wchar_t& data)
{
    Json::Value new_item((int)data);
    if (m_json->isArray())
        m_json->append(new_item);
    else
        (*m_json)[name] = new_item;
}

void json_archive::write_impl(const std::string& name, const short& data)
{
    Json::Value new_item((int)data);
    if (m_json->isArray())
        m_json->append(new_item);
    else
        (*m_json)[name] = new_item;
}

void json_archive::write_impl(const std::string& name, const unsigned short& data)
{
    Json::Value new_item((unsigned int)data);
    if (m_json->isArray())
        m_json->append(new_item);
    else
        (*m_json)[name] = new_item;
}

void json_archive::write_impl(const std::string& name, const int& data)
{
    Json::Value new_item(data);
    if (m_json->isArray())
        m_json->append(new_item);
    else
        (*m_json)[name] = new_item;
}

void json_archive::write_impl(const std::string& name, const unsigned int& data)
{
    Json::Value new_item(data);
    if (m_json->isArray())
        m_json->append(new_item);
    else
        (*m_json)[name] = new_item;
}

void json_archive::write_impl(const std::string& name, const long& data)
{
    Json::Value new_item((long long)data);
    if (m_json->isArray())
        m_json->append(new_item);
    else
        (*m_json)[name] = new_item;
}

void json_archive::write_impl(const std::string& name, const unsigned long& data)
{
    Json::Value new_item((unsigned long long) data);
    if (m_json->isArray())
        m_json->append(new_item);
    else
        (*m_json)[name] = new_item;
}

void json_archive::write_impl(const std::string& name, const long long& data)
{
    Json::Value new_item(data);
    if (m_json->isArray())
        m_json->append(new_item);
    else
        (*m_json)[name] = new_item;
}

void json_archive::write_impl(const std::string& name, const unsigned long long& data)
{
    Json::Value new_item(data);
    if (m_json->isArray())
        m_json->append(new_item);
    else
        (*m_json)[name] = new_item;
}

void json_archive::write_impl(const std::string& name, const float& data)
{
    Json::Value new_item(data);
    if (m_json->isArray())
        m_json->append(new_item);
    else
        (*m_json)[name] = new_item;
}

void json_archive::write_impl(const std::string& name, const double& data)
{
    Json::Value new_item(data);
    if (m_json->isArray())
        m_json->append(new_item);
    else
        (*m_json)[name] = new_item;
}

void json_archive::write_impl(const std::string& name, const long double& data)
{
    Json::Value new_item((double)data);
    if (m_json->isArray())
        m_json->append(new_item);
    else
        (*m_json)[name] = new_item;
}

void json_archive::write_impl(const std::string& name, const std::string& data)
{
    // json内容必须为utf-8编码，因此要转换，但name一般约定为英文字符，因此不转码也没事
    Json::Value new_item(string_tools::gbk_to_utf8(data).c_str());
    if (m_json->isArray())
        m_json->append(new_item);
    else
        (*m_json)[name] = new_item;
}

void json_archive::write_impl(const std::string& name, char* buffer, long byte_count)
{
    std::string buffer_text = string_tools::to_base64(std::string(buffer, byte_count));
    write(name, buffer_text);
}

void json_archive::clear_parent_nodes_cache()
{
    m_json_array_reading_index = 0;
    while (!m_parent_nodes.empty()) m_parent_nodes.pop();
}









_JOY_UTILITY_END_