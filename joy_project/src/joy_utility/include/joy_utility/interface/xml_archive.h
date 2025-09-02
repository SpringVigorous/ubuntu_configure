#pragma once
#ifndef __JOY_UTILITY_XML_ARCHIVE_H__
#define __JOY_UTILITY_XML_ARCHIVE_H__
#include "joy_utility/interface/serialize_interface.h"

namespace tinyxml2
{
	class XMLElement;
}


_JOY_UTILITY_BEGIN_ 


class JOY_UTILITY_API xml_archive : public member_rw_interface
{
public:
	xml_archive(tinyxml2::XMLElement* xml, bool is_storing = false);
	virtual ~xml_archive();

public:
	virtual bool is_storing();

protected:
	virtual inline void read_impl(const std::string& name, const serialize_flag& data);
	virtual inline void read_impl(const std::string& name, bool& data);
	virtual inline void read_impl(const std::string& name, char& data);
	virtual inline void read_impl(const std::string& name, unsigned char& data);
	virtual inline void read_impl(const std::string& name, wchar_t& data);
	virtual inline void read_impl(const std::string& name, short& data);
	virtual inline void read_impl(const std::string& name, unsigned short& data);
	virtual inline void read_impl(const std::string& name, int& data);
	virtual inline void read_impl(const std::string& name, unsigned int& data);
	virtual inline void read_impl(const std::string& name, long& data);
	virtual inline void read_impl(const std::string& name, unsigned long& data);
	virtual inline void read_impl(const std::string& name, long long& data);
	virtual inline void read_impl(const std::string& name, unsigned long long& data);
	virtual inline void read_impl(const std::string& name, float& data);
	virtual inline void read_impl(const std::string& name, double& data);
	virtual inline void read_impl(const std::string& name, long double& data);
	virtual inline void read_impl(const std::string& name, std::string& data);
	virtual inline void read_impl(const std::string& name, char*& buffer, long& byte_count);

	virtual inline void write_impl(const std::string& name, const serialize_flag& data);
	virtual inline void write_impl(const std::string& name, const bool& data);
	virtual inline void write_impl(const std::string& name, const char& data);
	virtual inline void write_impl(const std::string& name, const unsigned char& data);
	virtual inline void write_impl(const std::string& name, const wchar_t& data);
	virtual inline void write_impl(const std::string& name, const short& data);
	virtual inline void write_impl(const std::string& name, const unsigned short& data);
	virtual inline void write_impl(const std::string& name, const int& data);
	virtual inline void write_impl(const std::string& name, const unsigned int& data);
	virtual inline void write_impl(const std::string& name, const long& data);
	virtual inline void write_impl(const std::string& name, const unsigned long& data);
	virtual inline void write_impl(const std::string& name, const long long& data);
	virtual inline void write_impl(const std::string& name, const unsigned long long& data);
	virtual inline void write_impl(const std::string& name, const float& data);
	virtual inline void write_impl(const std::string& name, const double& data);
	virtual inline void write_impl(const std::string& name, const long double& data);
	virtual inline void write_impl(const std::string& name, const std::string& data);
	virtual inline void write_impl(const std::string& name, char* buffer, long byte_count);

private:
	tinyxml2::XMLElement* m_xml = nullptr;
	bool m_is_array_reading_mode = false;
	tinyxml2::XMLElement* m_last_child_xml = nullptr;
	std::string m_last_child_name;
	bool m_is_storing = false;

	// 仅临时标记对象，内存由外部处理
	// <0>为父对象
	// <1>为父对象是否处于数组模式读取状态
	// <2>为父对象最后一次读取时使用的节点对象
	// <3>为父对象最后一次读取时使用的节点名，对象或数组模式开始时会置为空，结束时会从栈中恢复
	// 注：因为数组模式中也不一定放的是节点名完全相同的对象，如会放入个数及各元素，因此要记住当前对象最后一次读取时的节
	// 点名，以确定下一个对象在数组模式中是否要移到兄弟节点上，节点名不同时不需要移动
	std::stack<std::tuple<tinyxml2::XMLElement*, bool, tinyxml2::XMLElement*, std::string>> m_parent_nodes;


};







_JOY_UTILITY_END_
#endif
