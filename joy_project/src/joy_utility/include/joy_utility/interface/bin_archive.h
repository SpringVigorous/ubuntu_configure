#pragma once
#ifndef __JOY_UTILITY_BIN_ARCHIVE_H__
#define __JOY_UTILITY_BIN_ARCHIVE_H__
#include "joy_utility/interface/serialize_interface.h"




_JOY_UTILITY_BEGIN_
class HArchive;

class JOY_UTILITY_API bin_archive : public member_rw_interface
{
public:
	bin_archive(HArchive& ar);
	virtual ~bin_archive();

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
	HArchive& m_ar;
};


//////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////











_JOY_UTILITY_END_
#endif
