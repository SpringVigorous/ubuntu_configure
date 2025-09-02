
#include "tinyxml2.h"
#include <utility>
#include "joy_utility/interface/xml_archive.h"
#include "joy_utility/tools/string_tools.h"
#include "joy_utility/tools/xml_tools.h"
//#ifdef _DEBUG
//#define new DEBUG_NEW
//#endif
_JOY_UTILITY_BEGIN_
using namespace tinyxml2;

xml_archive::xml_archive(tinyxml2::XMLElement* xml, bool is_storing/* = false*/)
	: m_xml(xml), m_is_storing(is_storing)
{

}

xml_archive::~xml_archive()
{

}

bool xml_archive::is_storing()
{
	return m_is_storing;
}

void xml_archive::read_impl(const std::string& name, const serialize_flag& data)
{
	if (serialize_flag::sub_obj_bg == data)
	{
		auto raw_name = name.c_str();

		tinyxml2::XMLElement* node_xml = nullptr;
		if (m_is_array_reading_mode && name == m_last_child_name)
		{
			if (!m_last_child_xml)
				node_xml = m_xml->FirstChildElement(raw_name);
			else
				node_xml = m_last_child_xml->NextSiblingElement(raw_name);
		}
		else
		{
			node_xml = m_xml->FirstChildElement(raw_name);
		}

		if (!node_xml) return;

		// 本次要处理的对象确定后再登记到栈中
		m_last_child_xml = node_xml;
		m_last_child_name = name;
		if (m_is_array_reading_mode)
			m_parent_nodes.push(std::make_tuple(m_xml, true, m_last_child_xml, m_last_child_name));
		else
			m_parent_nodes.push(std::make_tuple(m_xml, false, nullptr, ""));

		// 登记后再设置为要操作的对象，以便后面操作
		m_is_array_reading_mode = false;
		m_xml = node_xml; // 注意，这里与读取数据时不一样，读取数据不用将node_xml赋给m_xml
	}
	else if (serialize_flag::sub_obj_ed == data)
	{
		auto parent = m_parent_nodes.top();
		m_xml = std::get<0>(parent);
		m_is_array_reading_mode = std::get<1>(parent);
		m_last_child_xml = std::get<2>(parent);
		m_last_child_name = std::get<3>(parent);
		m_parent_nodes.pop();
	}
	else if (serialize_flag::array_bg == data)
	{
		auto raw_name = name.c_str();
		tinyxml2::XMLElement* node_xml = nullptr;
		if (m_is_array_reading_mode && name == m_last_child_name)
		{
			if (!m_last_child_xml)
				node_xml = m_xml->FirstChildElement(raw_name);
			else
				node_xml = m_last_child_xml->NextSiblingElement(raw_name);
		}
		else
		{
			node_xml = m_xml->FirstChildElement(raw_name);
		}

		if (!node_xml) return;

		// 本次要处理的对象确定后再登记到栈中
		m_last_child_xml = node_xml;
		m_last_child_name = name;
		if (m_is_array_reading_mode)
			m_parent_nodes.push(std::make_tuple(m_xml, true, m_last_child_xml, m_last_child_name));
		else
			m_parent_nodes.push(std::make_tuple(m_xml, false, nullptr, ""));

		// 登记后再设置为要操作的对象，以便后面操作
		m_is_array_reading_mode = true;
		m_xml = node_xml; // 注意，这里与读取数据时不一样，读取数据不用将node_xml赋给m_xml
	}
	else if (serialize_flag::array_ed == data)
	{
		auto parent = m_parent_nodes.top();
		m_xml = std::get<0>(parent);
		m_is_array_reading_mode = std::get<1>(parent);
		m_last_child_xml = std::get<2>(parent);
		m_last_child_name = std::get<3>(parent);
		m_parent_nodes.pop();
	}
	else
	{
		// nothing;
	}
}

void xml_archive::read_impl(const std::string& name, bool& data)
{
	std::string data_text;
	read_impl(name, data_text);
	data = string_tools::is_equal_ignore_case(data_text,"true");
}

void xml_archive::read_impl(const std::string& name, char& data)
{
	std::string data_text;
	read_impl(name, data_text);
	data = (char)(data_text.size() > 0 ? data_text[0] : '\0');
}

void xml_archive::read_impl(const std::string& name, unsigned char& data)
{
	std::string data_text;
	read_impl(name, data_text);
	data = (unsigned char)(data_text.size() > 0 ? data_text[0] : '\0');
}

void xml_archive::read_impl(const std::string& name, wchar_t& data)
{
	std::string data_text;
	read_impl(name, data_text);
	data = (wchar_t)(data_text.size() > 0 ? data_text[0] : L'\0');
}

void xml_archive::read_impl(const std::string& name, short& data)
{
	std::string data_text;
	read_impl(name, data_text);
	data = (short)std::stoi(data_text);
}

void xml_archive::read_impl(const std::string& name, unsigned short& data)
{
	std::string data_text;
	read_impl(name, data_text);
	data = (unsigned short)std::stoi(data_text);
}

void xml_archive::read_impl(const std::string& name, int& data)
{
	std::string data_text;
	read_impl(name, data_text);
	data = std::stoi(data_text);
}

void xml_archive::read_impl(const std::string& name, unsigned int& data)
{
	std::string data_text;
	read_impl(name, data_text);
	data = (unsigned int)std::stol(data_text, nullptr, 10);
}

void xml_archive::read_impl(const std::string& name, long& data)
{
	std::string data_text;
	read_impl(name, data_text);
	data = std::stol(data_text);
}

void xml_archive::read_impl(const std::string& name, unsigned long& data)
{
	std::string data_text;
	read_impl(name, data_text);
	data = std::stoul(data_text, nullptr, 10);
}

void xml_archive::read_impl(const std::string& name, long long& data)
{
	std::string data_text;
	read_impl(name, data_text);
	data = std::stoll(data_text);
}

void xml_archive::read_impl(const std::string& name, unsigned long long& data)
{
	std::string data_text;
	read_impl(name, data_text);
	data = std::stoull(data_text, nullptr, 10);
}

void xml_archive::read_impl(const std::string& name, float& data)
{
	std::string data_text;
	read_impl(name, data_text);
	data = (float)std::stof(data_text);
}

void xml_archive::read_impl(const std::string& name, double& data)
{
	std::string data_text;
	read_impl(name, data_text);
	data = std::stof(data_text);
}

void xml_archive::read_impl(const std::string& name, long double& data)
{
	std::string data_text;
	read_impl(name, data_text);
	data = std::stold(data_text, nullptr);
}

void xml_archive::read_impl(const std::string& name, std::string& data)
{
	data = "";
	if (name.empty()) return;

	auto raw_name = name.c_str();
	// 数组的内部元素读取过程中不会夹杂非数组对象的读取，因此逻辑可以简单一点
	tinyxml2::XMLElement* node_xml = nullptr;
	if (m_is_array_reading_mode && name == m_last_child_name)
	{
		if (!m_last_child_xml)
			node_xml = m_xml->FirstChildElement(raw_name);
		else
			node_xml = m_last_child_xml->NextSiblingElement(raw_name);

		m_last_child_xml = node_xml;
		m_last_child_name = name;
	}
	else if (m_is_array_reading_mode && name != m_last_child_name)
	{
		// 数组数据可能会放一些总个数，版本号之类的附加数据，这时虽然处于数组模式，但不是逐一往下读的，不用找兄弟节点
		node_xml = m_xml->FirstChildElement(raw_name);
		m_last_child_xml = node_xml;
		m_last_child_name = name;
	}
	else
	{
		node_xml = m_xml->FirstChildElement(raw_name);
		m_last_child_xml = nullptr;
		m_last_child_name = "";
	}

	if (!node_xml) return;

	const char* text_buffer = node_xml->GetText();
	std::string text = (text_buffer ? text_buffer : "");
	// safe_delete(text_buffer); // 不能删除，xml内部会处理

	xml_tree_encoding encoding = get_xml_tree_encoding(node_xml);
	if (xml_tree_encoding::utf_8 == encoding)
		data = string_tools::utf8_to_gbk(text);
	else
		data = text;
}

void xml_archive::read_impl(const std::string& name, char*& buffer, long& byte_count)
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
		buffer[i] = base64_str[i];
}

void xml_archive::write_impl(const std::string& name, const serialize_flag& data)
{
	if (!m_xml) return;

	tinyxml2::XMLDocument* doc = m_xml->GetDocument();
	if (!doc) return;
	auto raw_name = name.c_str();

	XMLNode* parent_node = m_xml->Parent();
	XMLElement* parent_xml = parent_node ? parent_node->ToElement() : nullptr;

	if (serialize_flag::sub_obj_bg == data)
	{
		XMLElement* new_node = doc->NewElement(raw_name);
		if (!new_node) return;

		m_xml->InsertEndChild(new_node);
		m_xml = new_node;
	}
	else if (serialize_flag::sub_obj_ed == data)
	{
		if (parent_xml) m_xml = parent_xml;
	}
	else if (serialize_flag::array_bg == data)
	{
		// 创建数组本身
		XMLElement* new_node = doc->NewElement(raw_name);
		if (!new_node) return;

		m_xml->InsertEndChild(new_node);
		m_xml = new_node;
	}
	else if (serialize_flag::array_ed == data)
	{
		if (parent_xml) m_xml = parent_xml;
	}
	else
	{
		// nothing;
	}
}

void xml_archive::write_impl(const std::string& name, const bool& data)
{
	std::string data_text = (data ? "true" : "false");
	write_impl(name, data_text);
}

void xml_archive::write_impl(const std::string& name, const char& data)
{
	std::string data_text;
	data_text += data;
	write_impl(name, data_text);
}

void xml_archive::write_impl(const std::string& name, const unsigned char& data)
{
	std::string data_text;
	data_text += data;
	write_impl(name, data_text);
}

void xml_archive::write_impl(const std::string& name, const wchar_t& data)
{
	std::string data_text;
	data_text += data;
	write_impl(name, data_text);
}

void xml_archive::write_impl(const std::string& name, const short& data)
{
	std::string data_text = string_tools::num_to_string(data);
	write_impl(name, data_text);
}

void xml_archive::write_impl(const std::string& name, const unsigned short& data)
{
	std::string data_text = string_tools::num_to_string(data);
	write_impl(name, data_text);
}

void xml_archive::write_impl(const std::string& name, const int& data)
{
	std::string data_text = string_tools::num_to_string(data);
	write_impl(name, data_text);
}

void xml_archive::write_impl(const std::string& name, const unsigned int& data)
{
	std::string data_text = string_tools::num_to_string(data);
	write_impl(name, data_text);
}

void xml_archive::write_impl(const std::string& name, const long& data)
{
	std::string data_text = string_tools::num_to_string(data);
	write_impl(name, data_text);
}

void xml_archive::write_impl(const std::string& name, const unsigned long& data)
{
	std::string data_text = string_tools::num_to_string(data);
	write_impl(name, data_text);
}

void xml_archive::write_impl(const std::string& name, const long long& data)
{
	std::string data_text = string_tools::num_to_string(data);
	write_impl(name, data_text);
}

void xml_archive::write_impl(const std::string& name, const unsigned long long& data)
{
	std::string data_text = string_tools::num_to_string(data);
	write_impl(name, data_text);
}

void xml_archive::write_impl(const std::string& name, const float& data)
{
	std::string data_text = string_tools::num_to_string(data);
	write_impl(name, data_text);
}

void xml_archive::write_impl(const std::string& name, const double& data)
{
	std::string data_text = string_tools::num_to_string(data);
	write_impl(name, data_text);
}

void xml_archive::write_impl(const std::string& name, const long double& data)
{
	std::string data_text = string_tools::num_to_string(data);
	write_impl(name, data_text);
}

void xml_archive::write_impl(const std::string& name, const std::string& data)
{
	std::string name_str;
	std::string data_str;
	xml_tree_encoding encoding = get_xml_tree_encoding(m_xml);
	if (xml_tree_encoding::utf_8 == encoding)
	{
		name_str = string_tools::gbk_to_utf8(name);
		data_str = string_tools::gbk_to_utf8(data);
	}
	else
	{
		name_str = name;
		data_str = data;
	}


	// xml格式为了与json匹配，且适应大数据对象，所有数据均写到新节点的value中，而不是当前节点的attribute中
	// xml当序列化数组的时候，子节点的节点名均相同，此时按同名的兄弟节点添加到末尾，否则按子节点添加
	// m_parent_xml->SetAttribute(name, data_str.c_str());
	tinyxml2::XMLDocument* doc = (m_xml ? m_xml->GetDocument() : nullptr);
	if (!doc) return;

	tinyxml2::XMLElement* new_node = doc->NewElement(name_str.c_str());
	if (!new_node) return;

	new_node->InsertEndChild(doc->NewText(data_str.c_str()));
	m_xml->InsertEndChild(new_node);
}

void xml_archive::write_impl(const std::string& name, char* buffer, long byte_count)
{
	std::string buffer_text(buffer, byte_count);
	
	write(name, string_tools::to_base64(buffer_text));
}









_JOY_UTILITY_END_