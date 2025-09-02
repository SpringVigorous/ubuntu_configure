
#include "joy_utility/interface/serialize_interface.h"
#include "joy_utility/tools/string_tools.h"
#ifdef _DEBUG
#define new DEBUG_NEW
#endif
_JOY_UTILITY_BEGIN_

serialize_interface::serialize_interface()
{

}

serialize_interface::~serialize_interface()
{

}

void serialize_interface::serialize_members(member_rw_interface& mt)
{
}

void member_rw_interface::read(const std::string& name, char*& buffer, long& byte_count)
{
	read_impl(name, buffer, byte_count);
}

void member_rw_interface::read(const std::string& name, const serialize_flag& data)
{
	read_impl(name, data);
}

void member_rw_interface::read(const std::string& name, bool& data)
{
	read_impl(name, data);
}

void member_rw_interface::read(const std::string& name, char& data)
{
	read_impl(name, data);
}

void member_rw_interface::read(const std::string& name, unsigned char& data)
{
	read_impl(name, data);
}

void member_rw_interface::read(const std::string& name, wchar_t& data)
{
	read_impl(name, data);
}

void member_rw_interface::read(const std::string& name, short& data)
{
	read_impl(name, data);
}

void member_rw_interface::read(const std::string& name, unsigned short& data)
{
	read_impl(name, data);
}

void member_rw_interface::read(const std::string& name, int& data)
{
	read_impl(name, data);
}

void member_rw_interface::read(const std::string& name, unsigned int& data)
{
	read_impl(name, data);
}

void member_rw_interface::read(const std::string& name, long& data)
{
	read_impl(name, data);
}

void member_rw_interface::read(const std::string& name, unsigned long& data)
{
	read_impl(name, data);
}

void member_rw_interface::read(const std::string& name, long long& data)
{
	read_impl(name, data);
}

void member_rw_interface::read(const std::string& name, unsigned long long& data)
{
	read_impl(name, data);
}

void member_rw_interface::read(const std::string& name, float& data)
{
	read_impl(name, data);
}

void member_rw_interface::read(const std::string& name, double& data)
{
	read_impl(name, data);
}

void member_rw_interface::read(const std::string& name, long double& data)
{
	read_impl(name, data);
}

void member_rw_interface::read(const std::string& name, std::string& data)
{
	read_impl(name, data);
}

void member_rw_interface::write_impl(const std::string& name,const std::wstring& data)
{

	auto gbk_str = string_tools::unicode_to_gbk(data);
	write_impl(name, gbk_str);
}
void member_rw_interface::read_impl(const std::string& name, std::wstring& data)
{



	std::string tmp_data;
	read_impl(name, tmp_data);
	data = string_tools::gbk_to_unicode(tmp_data);
}


void member_rw_interface::read(const std::string& name, std::wstring& data)
{
	read_impl(name, data);
}

void member_rw_interface::write(const std::string& name, char* buffer, long byte_count)
{
	write_impl(name, buffer, byte_count);
}

void member_rw_interface::write(const std::string& name, const serialize_flag& data)
{
	write_impl(name, data);
}

void member_rw_interface::write(const std::string& name, const bool& data)
{
	write_impl(name, data);
}

void member_rw_interface::write(const std::string& name, const char& data)
{
	write_impl(name, data);
}

void member_rw_interface::write(const std::string& name, const unsigned char& data)
{
	write_impl(name, data);
}

void member_rw_interface::write(const std::string& name, const wchar_t& data)
{
	write_impl(name, data);
}

void member_rw_interface::write(const std::string& name, const short& data)
{
	write_impl(name, data);
}

void member_rw_interface::write(const std::string& name, const unsigned short& data)
{
	write_impl(name, data);
}

void member_rw_interface::write(const std::string& name, const int& data)
{
	write_impl(name, data);
}

void member_rw_interface::write(const std::string& name, const unsigned int& data)
{
	write_impl(name, data);
}

void member_rw_interface::write(const std::string& name, const long& data)
{
	write_impl(name, data);
}

void member_rw_interface::write(const std::string& name, const unsigned long& data)
{
	write_impl(name, data);
}

void member_rw_interface::write(const std::string& name, const long long& data)
{
	write_impl(name, data);
}

void member_rw_interface::write(const std::string& name, const unsigned long long& data)
{
	write_impl(name, data);
}

void member_rw_interface::write(const std::string& name, const float& data)
{
	write_impl(name, data);
}

void member_rw_interface::write(const std::string& name, const double& data)
{
	write_impl(name, data);
}

void member_rw_interface::write(const std::string& name, const long double& data)
{
	write_impl(name, data);
}

void member_rw_interface::write(const std::string& name, const std::string& data)
{
	write_impl(name, data);
}


void member_rw_interface::write(const std::string& name, const std::wstring& data)
{
	write_impl(name, string_tools::unicode_to_gbk(data));
}

void member_rw_interface::write(const std::string& name, const char* data)
{
	write_impl(name,std::string(data));
}

void member_rw_interface::write(const std::string& name, const wchar_t* data)
{
	write_impl(name, std::wstring(data));
}

void member_rw_interface::read_impl(const std::string& name, std::vector<bool>& val)
{
	read_impl(name, serialize_flag::array_bg);

	int count = 0;
	read_impl("count", count); // name没有意义，只用于保持原型统一

	val.resize(count);
	for (int i = 0; i < count; ++i)
	{
		bool tmp = false;
		read_impl(serialize_helper::pack_index(i), tmp); // tinyxml2解析时不支持节点名为数字开头,不允许带点号
		val[i] = tmp;
	}

	read_impl(name, serialize_flag::array_ed);
}

void member_rw_interface::write_impl(const std::string& name, const std::vector<bool>& val)
{
	write_impl(name, serialize_flag::array_bg);

	write_impl("count", (int) (val.size())); // name没有意义，只用于保持原型统一
	for (size_t i = 0; i < val.size(); ++i)
		write_impl(serialize_helper::pack_index(i), (const bool&) val[i]); // tinyxml2解析时不支持节点名为数字开头,不允许带点号

	write_impl(name, serialize_flag::array_ed);
}


//////////////////////////////////////////////////////////////////////////


member_rw_interface::member_rw_interface()
{

}

member_rw_interface::member_rw_interface(const member_rw_interface& src)
{

}

member_rw_interface::~member_rw_interface()
{

}

//////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////




//////////////////////////////////////////////////////////////////////////




x_object_flag_serialization_guard::x_object_flag_serialization_guard(const std::string& name, member_rw_interface& mt)
{
	m_name = name;
	m_mt = &mt;

	if (m_mt->is_storing())
		m_mt->write(m_name, serialize_flag::sub_obj_bg);
	else
			m_mt->read(m_name, serialize_flag::sub_obj_bg);
}

x_object_flag_serialization_guard::~x_object_flag_serialization_guard()
{
	if (m_mt->is_storing())
		m_mt->write(m_name, serialize_flag::sub_obj_ed);
	else
			m_mt->read(m_name, serialize_flag::sub_obj_ed);
}

x_array_flag_serialization_guard::x_array_flag_serialization_guard(const std::string& name, member_rw_interface& mt)
{
	m_name = name;
	m_mt = &mt;

	if (m_mt->is_storing())
		m_mt->write(m_name, serialize_flag::array_bg);
	else
		m_mt->read(m_name, serialize_flag::array_bg);
}

x_array_flag_serialization_guard::~x_array_flag_serialization_guard()
{
	if (m_mt->is_storing())
		m_mt->write(m_name, serialize_flag::array_ed);
	else
		m_mt->read(m_name, serialize_flag::array_ed);
}

x_data_wrapper_buffer::x_data_wrapper_buffer(const std::string& name, char*& buffer, long& byte_count)
	: m_name(name), m_buffer(buffer), m_byte_count(byte_count)
{

}

std::string x_data_wrapper_buffer::get_name() const
{
	return m_name;
}

char*& x_data_wrapper_buffer::get_buffer() const
{
	return m_buffer;
}

long& x_data_wrapper_buffer::get_byte_count() const
{
	return m_byte_count;
}


std::string serialize_helper::pack_flag(const std::string& name)
{
	return std::format("__{}__", name);
}

std::string serialize_helper::pack_count(const std::string& name)
{
	return std::format("__{}_count__", name);
}

std::string serialize_helper::pack_item(const std::string& name)
{
	if (name.empty())
		return "__item__";
	return std::format("__{}_item__", name);

}
std::string serialize_helper::pack_version(const std::string& name)
{
	return std::format("__{}_version__", name);

}
std::string serialize_helper::pack_index( int index)
{
	return std::format("__item_{}__",index);

}







_JOY_UTILITY_END_

