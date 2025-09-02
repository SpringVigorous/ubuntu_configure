#pragma once
#ifndef __JOY_UTILITY_SAMPLE_H__
#define __JOY_UTILITY_SAMPLE_H__
#include <utility>
#include <stack>
#include "joy_utility/interface/serialize_interface.h"


namespace Json
{
	class Value;
}

_JOY_UTILITY_BEGIN_ 

class JOY_UTILITY_API json_archive : public member_rw_interface
{
public:
	json_archive(Json::Value* json, bool is_storing = false);
	virtual ~json_archive();

public:
	virtual bool is_storing();

public:
	void clear_parent_nodes_cache();

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
	Json::Value* m_json = nullptr; // 不能存为引用，jsoncpp库赋值的时候内部使用了swap，无法正常记住原对象
	int m_json_array_reading_index = 0; // 为json数组的时候用于记住当前读取的元素下标
	bool m_is_storing = false;
	
	// 仅临时标记对象，内存由外部处理，first为父json对象，second为父json对象的现场array_index（仅当为数组对象才有用）
	std::stack<std::pair<Json::Value*, int>> m_parent_nodes;
};










_JOY_UTILITY_END_
#endif
