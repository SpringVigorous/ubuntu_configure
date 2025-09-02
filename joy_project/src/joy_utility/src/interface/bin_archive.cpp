
#include "joy_utility/interface/bin_archive.h"
#include "joy_utility/kenels/harchive.h"

#include "joy_utility/kenels/hobject.h"
//#ifdef _DEBUG
//#define new DEBUG_NEW
//#endif
_JOY_UTILITY_BEGIN_
bin_archive::bin_archive(HArchive& ar) : m_ar(ar)
{

}

bin_archive::~bin_archive()
{

}

bool bin_archive::is_storing()
{
	return m_ar.IsStoring();
}

void bin_archive::read_impl(const std::string& name, const serialize_flag& data)
{
	UNUSED_ALWAYS(name);

	// write_impl写了值，则读取的时候也得配对读取，读取后丢弃不用即可
	int tmp = 0;
	m_ar >> tmp;
}

void bin_archive::read_impl(const std::string& name, bool& data)
{
	UNUSED_ALWAYS(name);
	m_ar >> data;
}

void bin_archive::read_impl(const std::string& name, char& data)
{
	UNUSED_ALWAYS(name);
	m_ar >> data;
}

void bin_archive::read_impl(const std::string& name, unsigned char& data)
{
	UNUSED_ALWAYS(name);
	m_ar >> data;
}

void bin_archive::read_impl(const std::string& name, wchar_t& data)
{
	UNUSED_ALWAYS(name);
	m_ar >> data;
}

void bin_archive::read_impl(const std::string& name, short& data)
{
	UNUSED_ALWAYS(name);
	m_ar >> data;
}

void bin_archive::read_impl(const std::string& name, unsigned short& data)
{
	UNUSED_ALWAYS(name);
	m_ar >> data;
}

void bin_archive::read_impl(const std::string& name, int& data)
{
	UNUSED_ALWAYS(name);
	m_ar >> data;
}

void bin_archive::read_impl(const std::string& name, unsigned int& data)
{
	UNUSED_ALWAYS(name);
	m_ar >> data;
}

void bin_archive::read_impl(const std::string& name, long& data)
{
	UNUSED_ALWAYS(name);
	m_ar >> data;
}

void bin_archive::read_impl(const std::string& name, unsigned long& data)
{
	UNUSED_ALWAYS(name);
	m_ar >> data;
}

void bin_archive::read_impl(const std::string& name, long long& data)
{
	UNUSED_ALWAYS(name);
	m_ar >> data;
}

void bin_archive::read_impl(const std::string& name, unsigned long long& data)
{
	UNUSED_ALWAYS(name);
	m_ar >> data;
}

void bin_archive::read_impl(const std::string& name, float& data)
{
	UNUSED_ALWAYS(name);
	m_ar >> data;
}

void bin_archive::read_impl(const std::string& name, double& data)
{
	UNUSED_ALWAYS(name);
	m_ar >> data;
}

void bin_archive::read_impl(const std::string& name, long double& data)
{
	UNUSED_ALWAYS(name);

	// 微软编译器为了兼容以前的DOS程序，限定了long double与double一样宽为64bit，与gcc,clang的128bit并不一样
	double tmp = 0.0;
	m_ar >> tmp;
	data = tmp;
}

void bin_archive::read_impl(const std::string& name, std::string& data)
{
	UNUSED_ALWAYS(name);
	m_ar >> data;
}

void bin_archive::read_impl(const std::string& name, char*& buffer, long& byte_count)
{
	UNUSED_ALWAYS(name);
	m_ar >> byte_count;
	if (byte_count <= 0)
	{
		buffer = nullptr;
		return;
	}

	buffer = new char[byte_count];
	memset(buffer, 0, byte_count);
	m_ar.Read(buffer, byte_count);
}

void bin_archive::write_impl(const std::string& name, const serialize_flag& data)
{
	UNUSED_ALWAYS(name);
	m_ar << (int)data;
}

void bin_archive::write_impl(const std::string& name, const bool& data)
{
	UNUSED_ALWAYS(name);
	m_ar << data;
}

void bin_archive::write_impl(const std::string& name, const char& data)
{
	UNUSED_ALWAYS(name);
	m_ar << data;
}

void bin_archive::write_impl(const std::string& name, const unsigned char& data)
{
	UNUSED_ALWAYS(name);
	m_ar << data;
}

void bin_archive::write_impl(const std::string& name, const wchar_t& data)
{
	UNUSED_ALWAYS(name);
	m_ar << data;
}

void bin_archive::write_impl(const std::string& name, const short& data)
{
	UNUSED_ALWAYS(name);
	m_ar << data;
}

void bin_archive::write_impl(const std::string& name, const unsigned short& data)
{
	UNUSED_ALWAYS(name);
	m_ar << data;
}

void bin_archive::write_impl(const std::string& name, const int& data)
{
	UNUSED_ALWAYS(name);
	m_ar << data;
}

void bin_archive::write_impl(const std::string& name, const unsigned int& data)
{
	UNUSED_ALWAYS(name);
	m_ar << data;
}

void bin_archive::write_impl(const std::string& name, const long& data)
{
	UNUSED_ALWAYS(name);
	m_ar << data;
}

void bin_archive::write_impl(const std::string& name, const unsigned long& data)
{
	UNUSED_ALWAYS(name);
	m_ar << data;
}

void bin_archive::write_impl(const std::string& name, const long long& data)
{
	UNUSED_ALWAYS(name);
	m_ar << data;
}

void bin_archive::write_impl(const std::string& name, const unsigned long long& data)
{
	UNUSED_ALWAYS(name);
	m_ar << data;
}

void bin_archive::write_impl(const std::string& name, const float& data)
{
	UNUSED_ALWAYS(name);
	m_ar << data;
}

void bin_archive::write_impl(const std::string& name, const double& data)
{
	UNUSED_ALWAYS(name);
	m_ar << data;
}

void bin_archive::write_impl(const std::string& name, const long double& data)
{
	UNUSED_ALWAYS(name);

	// 微软编译器为了兼容以前的DOS程序，限定了long double与double一样宽为64bit，与gcc,clang的128bit并不一样
	double tmp = (double)data;
	m_ar << tmp;
}

void bin_archive::write_impl(const std::string& name, const std::string& data)
{
	UNUSED_ALWAYS(name);
	m_ar << data;
}

void bin_archive::write_impl(const std::string& name, char* buffer, long byte_count)
{
	UNUSED_ALWAYS(name);
	m_ar << byte_count;
	if (byte_count > 0) m_ar.Write((void*)buffer, byte_count);
}












_JOY_UTILITY_END_