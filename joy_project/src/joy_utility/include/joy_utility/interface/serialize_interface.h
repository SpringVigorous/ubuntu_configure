#pragma once
#ifndef __JOY_UTILITY_SERIALIZE_INTERFACE_H__
#define __JOY_UTILITY_SERIALIZE_INTERFACE_H__

#include <array>
#include <vector>
#include <list>
#include <stack>
#include <map>
#include <string>
#include <type_traits>
#include <utility>
#include <format>

#include "joy_utility/joy_utility_macro.h"
#include "joy_utility/tools/template_utility.h"
// 引入命名空间以简化使用（可选）
using namespace std::literals::string_literals;

_JOY_UTILITY_BEGIN_ 

class JOY_UTILITY_API serialize_helper
{
public:
	static std::string pack_flag(const std::string& name);
	static std::string pack_count(const std::string& name);
	static std::string pack_index(int index);
	static std::string pack_item(const std::string& name="");
	static std::string pack_version(const std::string& name);

};


class member_rw_interface;
//////////////////////////////////////////////////////////////////////////


// 需要支持序列化的数据结构均需从此接口派生
// 没有特殊情况（如数据中心是注册方式工作的，不用写序列化宏），派生类都要写序列化宏，否则无法正确反序列化
class JOY_UTILITY_API serialize_interface
{
public:
	serialize_interface();
	virtual ~serialize_interface();

public:
	virtual void serialize_members(member_rw_interface& mt);
};

//判断成员函数中是否存在::serialize_members(member_rw_interface & mt)
#ifndef HAS_SERIALIZE_MEMBERS_FUNCTION
	#define HAS_SERIALIZE_MEMBERS_FUNCTION
	HAS_MEM_FUNC_BASE_WITH_ARGS(serialize_members, func, member_rw_interface&);
#endif


//////////////////////////////////////////////////////////////////////////


// 序列化数据标记（务必明确给定数值，以及以后扩展及调整顺序导致序列化失败，序列化时强转为int型，注意不要超出整数范围）
enum class serialize_flag
{
	sub_obj_bg = 0,		// 子节点开始
	sub_obj_ed = 1,		// 子节点结束
	array_bg = 2,		// 数组开始
	array_ed = 3		// 数组结束
};


//////////////////////////////////////////////////////////////////////////


// 将两个参数包装成一个参数，以便于&符号重载使用的时候直接可以给传两个参数就构造成一个对象，使用者不用关系对象的组装
// 注意，由于本对象要同时适用于数据读取和写入，因此，传入的数据对象不可以是右值（包括字面值），必须为左
// 值，如果确实有需要则请直接使用序列化读写接口
template <typename T>
class x_data_wrapper
{
public:

	using Type = raw_type_t<T>;

	// 禁止隐式转换防止与序列化其它接口造成二义性
	// 为了配合x_wrapper_macro使用，防止对象过早析构导致内部存的临时对象指针无效，必须用引用，而name则
	// 可能为自动生成，本身就可能是临时对象，因此不能存为引用，否则也会有一样的问题
	explicit x_data_wrapper(const std::string& name, T& data)
	{
		m_name = name;
		m_data = &data;
	}
	//explicit x_data_wrapper(const std::string& name, const T& data)
	//{
	//	m_name = name;
	//	m_data = static_cast<T*> (&data);
	//}
	~x_data_wrapper() = default;

public:
	std::string get_name() const {
		return m_name;
	}
	Type* get_data() const {
		return   m_data;
	}

private:
	std::string m_name;
	Type* m_data = nullptr;
};


// 参见宏x_wrapper_macro_named_enum
template <typename T>
class x_data_wrapper_enum
{
public:

	using Type = raw_type_t<T>;
public:
	explicit x_data_wrapper_enum(const std::string& name, T& data)
	{
		m_name = name;
		m_data = &data;
	}
	explicit x_data_wrapper_enum(const std::string& name,const T& data)
	{
		m_name = name;
		m_data = const_cast<T*> (&data);
	}
public:
	std::string get_name() const {
		return m_name;
	}
	Type* get_data() const {
		return m_data;
	}

private:
	std::string m_name;
	Type* m_data = nullptr;
};

// 参见宏x_wrapper_macro_named_buffer
class JOY_UTILITY_API x_data_wrapper_buffer
{
public:
	// 同时用于读写，长度不支持字面值，写的时候要正确设置好byte_count，读的时候，值由内部赋上buffer读取的长度
	explicit x_data_wrapper_buffer(const std::string& name, char*& buffer, long& byte_count);

public:
	std::string get_name() const;
	char*& get_buffer() const;
	long& get_byte_count() const;

private:
	std::string m_name;
	char*& m_buffer;
	long& m_byte_count;
};


// 对象构造时写入serialize_flag::sub_obj_bg标记，析构时写入serialize_flag::sub_obj_ed标记
// 一般用于类的序列化函数开始处，参数为序列化对象时使用的标识名（同一作用域不能相同），第二个参数为member_rw_interface对象mt
class JOY_UTILITY_API x_object_flag_serialization_guard
{
public:
	explicit x_object_flag_serialization_guard(const std::string& name, member_rw_interface& mt);
	~x_object_flag_serialization_guard();
	x_object_flag_serialization_guard(const x_object_flag_serialization_guard&) = delete;
	void operator=(const x_object_flag_serialization_guard&) const = delete;

private:
	std::string m_name;
	member_rw_interface* m_mt = nullptr;
	bool   is_storing;
};


// 对象构造时写入serialize_flag::array_bg标记，析构时写入serialize_flag::array_ed标记
// 参数为序列化对象时使用的标识名（同一作用域不能相同），第二个参数为member_rw_interface对象mt
class JOY_UTILITY_API x_array_flag_serialization_guard
{
public:
	explicit x_array_flag_serialization_guard(const std::string& name, member_rw_interface& mt);
	~x_array_flag_serialization_guard();
	x_array_flag_serialization_guard(const x_array_flag_serialization_guard&) = delete;
	void operator=(const x_array_flag_serialization_guard&) const = delete;

private:
	std::string m_name;
	member_rw_interface* m_mt = nullptr;
};



// 提供便利性的宏，简化常规数据的读写以及读写代码保持一致，强烈建议使用此方法实现业务层的序列化，而
// 不是使用read,write接口！！！示例如下：
// mt & x_wrapper_macro(a) & x_data_wrapper<int>("name", b); // 使用&可以连续序列化
// pair<int, std::string> test_pair;
// mt.read(x_wrapper_macro_named("pair", test_pair)); // 也可能使用读写接口
// 注意，由于以下两个宏要同时适用于数据读取和写入，因此，传入的数据对象不可以是右值（包括字面值），必须为左
// 值，如果确实有需要则请直接使用序列化读写接口
#define x_wrapper_macro_named(n, x) x_data_wrapper<decltype(x)>((n),(x))
#define x_wrapper_macro(x) x_wrapper_macro_named(#x, x)
#define x_wrapper_macro_named_enum(n, x) x_data_wrapper_enum<decltype(x)>((n),(x))
#define x_wrapper_macro_enum(x) x_wrapper_macro_named_enum(#x, x)
#define x_wrapper_macro_named_buffer(n, x, c) x_data_wrapper_buffer((n),(x),(c))
#define x_wrapper_macro_buffer(x, c) x_wrapper_macro_named_buffer(#x,x,c)


//////////////////////////////////////////////////////////////////////////
// 成员读写的接口，不同的存取方式需派生，如使用json存储要从此接口派生，同理，二进制存储或mfc的CArchive以
// 及xml格式等均要派生于此接口
// 注意，此接口不局限于以文件形式操作，保存为内存对象或将内存对象转储为文件均可使用此接口
// 强烈建议使用前面提供的简易包装宏实现业务层的序列化，而不是使用read,write接口！！！
// 示例如下：
// mt & x_wrapper_macro(123.456) & x_data_wrapper<int>("name", 001); // 使用&可以连续序列化
// pair<int, std::string> test_pair;
// mt.read(x_wrapper_macro_named("pair", test_pair)); // 也可能使用读写接口






class JOY_UTILITY_API member_rw_interface
{
protected:
	member_rw_interface(); // 只能由框架或派生类来构造这个对象
	member_rw_interface(const member_rw_interface& src);
	virtual ~member_rw_interface();
public:
	virtual bool is_storing() = 0;
	inline bool is_loading(){ return !is_storing(); } // 此接口不需要定义为virtual的

	// 重载&运算符，以便利用boost库序列化的代码减少移植代价，以及序列化代码的批量生成
	// 用法主要有两种，示例如下：
	// mt & x_wrapper_macro(aaaaa) & x_wrapper_macro(123.456) & x_data_wrapper<int>("name", 001);
	template <typename T>
	member_rw_interface& operator&(x_data_wrapper<T>&& data)
	{
        if (is_storing())
            write(std::forward<x_data_wrapper<T>>(data));
        else
            read(std::forward<x_data_wrapper<T>>(data));
		return *this;
	}

	template <typename T>
	member_rw_interface& operator&(x_data_wrapper_enum<T>&& data)
	{
		if (is_storing())
		{
			write(data.get_name(), (long long) (*data.get_data())); // 先取值再转为类型，不要先转类型再取值
		}
		else
		{
			long long tmp = 0;
			read(data.get_name(), tmp);
			*data.get_data() = static_cast<std::remove_reference<T>::type>(tmp);
		}

		return *this;
	}

	member_rw_interface& operator&(x_data_wrapper_buffer&& data)
	{
		if (is_storing())
			write(data.get_name(), data.get_buffer(), data.get_byte_count());
		else
			read(data.get_name(), data.get_buffer(), data.get_byte_count());

		return *this;
	}

public:

	template <typename T>
	member_rw_interface& operator&(const x_data_wrapper<T>& data)
	{
		if (is_storing())
			write(data);
		else
			read(data);
		return *this;
	}

	template <typename T>
	member_rw_interface& operator&(const x_data_wrapper_enum<T>& data)
	{
		using type = x_data_wrapper_enum<T>::Type;
		if constexpr (std::is_same_v< type, serialize_flag>)
		{
			if (is_storing())
			{
				write(data.get_name(), *data.get_data());
			}
			else
			{
				read(data.get_name(), *data.get_data());

			}
			return *this;
		}


		if (is_storing())
		{
			write(data.get_name(), (long long)(*data.get_data())); // 先取值再转为类型，不要先转类型再取值
		}
		else
		{
			long long tmp = 0;
			read(data.get_name(), tmp);
			*data.get_data() = static_cast<std::remove_reference<T>::type>(tmp);
		}

		return *this;
	}

	member_rw_interface& operator&(const x_data_wrapper_buffer& data)
	{
		if (is_storing())
			write(data.get_name(), data.get_buffer(), data.get_byte_count());
		else
			read(data.get_name(), data.get_buffer(), data.get_byte_count());

		return *this;
	}


	//////////////////////////////////////////////////////////////////////////
	// 常规函数版本

	// 由于json格式的限制，读取时必须指定节点名，xml和二进制方式则可以不用，但为了统一，强制要求传名称
	// json的限制之一是大部分库写入的节点内部使用map存储，最终序列化到文件会变成一个有序顺序，以及它不能便利的向上回溯等限制

	void read(const std::string& name, const serialize_flag& data); // 标志不会修改，因此为const
	void read(const std::string& name, bool& data);
	void read(const std::string& name, char& data);
	void read(const std::string& name, unsigned char& data);
	void read(const std::string& name, wchar_t& data);
	void read(const std::string& name, short& data);
	void read(const std::string& name, unsigned short& data);
	void read(const std::string& name, int& data);
	void read(const std::string& name, unsigned int& data);
	void read(const std::string& name, long& data);
	void read(const std::string& name, unsigned long& data);
	void read(const std::string& name, long long& data);
	void read(const std::string& name, unsigned long long& data);
	void read(const std::string& name, float& data);
	void read(const std::string& name, double& data);
	void read(const std::string& name, long double& data);

	void read(const std::string& name, std::string& data);
	void read(const std::string& name, std::wstring& data);
	
	// buffer由内部使用new分配并由外部使用的人负责管理（连续内存），length返回解码后的buffer字节数
	void read(const std::string& name, char*& buffer, long& byte_count);

	void write(const std::string& name, const serialize_flag& data);
	void write(const std::string& name, const bool& data);
	void write(const std::string& name, const char& data);
	void write(const std::string& name, const unsigned char& data);
	void write(const std::string& name, const wchar_t& data);
	void write(const std::string& name, const short& data);
	void write(const std::string& name, const unsigned short& data);
	void write(const std::string& name, const int& data);
	void write(const std::string& name, const unsigned int& data);
	void write(const std::string& name, const long& data);
	void write(const std::string& name, const unsigned long& data);
	void write(const std::string& name, const long long& data);
	void write(const std::string& name, const unsigned long long& data);
	void write(const std::string& name, const float& data);
	void write(const std::string& name, const double& data);
	void write(const std::string& name, const long double& data);

	void write(const std::string& name, const std::string& data);
	void write(const std::string& name, const std::wstring& data);

	// 写入时要支持字符串字面值，读取时则不用，通通转为std::string进行写入操作
	void write(const std::string& name, const char* data);
	void write(const std::string& name, const wchar_t* data);
	void write(const std::string& name, char* buffer, long byte_count); // buffer由外部分配好


	//////////////////////////////////////////////////////////////////////////
	// 泛化版本
	// 对于定义类或其它未在本接口中枚举出的类要支持读写则需要serialize_interface接口派生并实现其接口

	template <typename T>
	inline void read(const std::string& name, T& data)
	{
		read_impl(name, data);
	}

	template <typename T>
	inline void write(const std::string& name, const T& data)
	{
		write_impl(name, data);
	}

	template <typename T>
	inline void read(x_data_wrapper<T>&& data)
	{
		if (!data.get_name().empty() && data.get_data())
			read(data.get_name(), *data.get_data());
	}

	template <typename T>
	inline void write(x_data_wrapper<T>&& data)
	{
		if (!data.get_name().empty() && data.get_data())
			write(data.get_name(), *data.get_data());
	}


protected:
	// 主要用于json\xml等格式的序列化，值用于内部标记，不会把数据存入标记，为扩大泛型接口匹配范围，用const引用
	virtual inline void read_impl(const std::string& name, const serialize_flag& data) = 0;

	virtual inline void read_impl(const std::string& name, bool& data) = 0;
	virtual inline void read_impl(const std::string& name, char& data) = 0;
	virtual inline void read_impl(const std::string& name, unsigned char& data) = 0;
	virtual inline void read_impl(const std::string& name, wchar_t& data) = 0;
	virtual inline void read_impl(const std::string& name, short& data) = 0;
	virtual inline void read_impl(const std::string& name, unsigned short& data) = 0;
	virtual inline void read_impl(const std::string& name, int& data) = 0;
	virtual inline void read_impl(const std::string& name, unsigned int& data) = 0;
	virtual inline void read_impl(const std::string& name, long& data) = 0;
	virtual inline void read_impl(const std::string& name, unsigned long& data) = 0;
	virtual inline void read_impl(const std::string& name, long long& data) = 0;
	virtual inline void read_impl(const std::string& name, unsigned long long& data) = 0;
	virtual inline void read_impl(const std::string& name, float& data) = 0;
	virtual inline void read_impl(const std::string& name, double& data) = 0;
	virtual inline void read_impl(const std::string& name, long double& data) = 0;
	virtual inline void read_impl(const std::string& name, std::string& data) = 0;

	// buffer由内部使用new分配并由外部使用的人负责管理（连续内存），length返回解码后的buffer字节数
	virtual inline void read_impl(const std::string& name, char*& buffer, long& byte_count) = 0;


	// 主要用于json\xml等格式的序列化，值用于内部标记，对外没有使用价值，为扩大泛型接口匹配范围，用const引用
	virtual inline void write_impl(const std::string& name, const serialize_flag& data) = 0;

	virtual inline void write_impl(const std::string& name, const bool& data) = 0;
	virtual inline void write_impl(const std::string& name, const char& data) = 0;
	virtual inline void write_impl(const std::string& name, const unsigned char& data) = 0;
	virtual inline void write_impl(const std::string& name, const wchar_t& data) = 0;
	virtual inline void write_impl(const std::string& name, const short& data) = 0;
	virtual inline void write_impl(const std::string& name, const unsigned short& data) = 0;
	virtual inline void write_impl(const std::string& name, const int& data) = 0;
	virtual inline void write_impl(const std::string& name, const unsigned int& data) = 0;
	virtual inline void write_impl(const std::string& name, const long& data) = 0;
	virtual inline void write_impl(const std::string& name, const unsigned long& data) = 0;
	virtual inline void write_impl(const std::string& name, const long long& data) = 0;
	virtual inline void write_impl(const std::string& name, const unsigned long long& data) = 0;
	virtual inline void write_impl(const std::string& name, const float& data) = 0;
	virtual inline void write_impl(const std::string& name, const double& data) = 0;
	virtual inline void write_impl(const std::string& name, const long double& data) = 0;
	virtual inline void write_impl(const std::string& name, const std::string& data) = 0;
	virtual inline void write_impl(const std::string& name, char* buffer, long byte_count) = 0; // buffer由外部分配好

protected:
	//////////////////////////////////////////////////////////////////////////
	// 对于已经有serialize_members函数的也可以直接序列化
	
	template <typename T>
	inline void read_impl(const std::string& name, T& data) // name没有意义，只用于保持原型统一
	{ 
        if constexpr (has_serialize_members_func_v<T>) {
			x_object_flag_serialization_guard tmp_object_flag(name, *this);
		    data.serialize_members(*this);
        } 
		else
		{
			static_assert(false,COMBINE_SIG_LINE("serialize_members()未实现"));
		}
    }

	template <typename T>
	inline void write_impl(const std::string& name, const T& data) // name没有意义，只用于保持原型统一
	{
        if constexpr (has_serialize_members_func_v<T>) {
			x_object_flag_serialization_guard tmp_object_flag(name, *this);
		    const_cast<T&>(data).serialize_members(*this); // 成员函数不是const的，不能通过const对象调用

        }
		else
		{
			static_assert(false, COMBINE_SIG_LINE("serialize_members()未实现"));
		}
			//write_impl(name, data);

	}

	//////////////////////////////////////////////////////////////////////////
	// 对数组进行重载(如果元素是指针，则不打算支持，否则会要求元素从HObject派生，否则指针对象序列化由用户自己实现
	// 反序列化时对象是通过Runtime创建的，如果对象不是new的，而是其它对象的引用，则不支持，综合来看，指针的序列化
	// 功能基本上起不到太多实用效果，所以不提供)

	void read_impl(const std::string& name, std::wstring& data);
	void write_impl(const std::string& name, const std::wstring& data);




	template<class T, size_t N>
	inline void read_impl(const std::string& name, std::array<T, N>& val) 
	{
		int count = 0;
		read_impl(serialize_helper::pack_count(name), count); // name没有意义，只用于保持原型统一
		read_impl(name, serialize_flag::array_bg);

		//val.clear();
		for (int i = 0; i < count && i < (int) val.size(); ++i)
		{
			read_impl(serialize_helper::pack_index(i), val[i]); // tinyxml2解析时不支持节点名为数字开头,不允许带点号
		}

		read_impl(name, serialize_flag::array_ed);
	}

	template<class T, size_t N>
	inline void write_impl(const std::string& name, const std::array<T, N>& val)
	{
		write_impl(serialize_helper::pack_count(name), (int) (val.size())); // name没有意义，只用于保持原型统一

		x_array_flag_serialization_guard tmp_object_flag(name, *this);

		for (size_t i = 0; i < val.size(); ++i)
			write_impl(serialize_helper::pack_index(i), val[i]); // tinyxml2解析时不支持节点名为数字开头,不允许带点号


	}

	// std::vector<bool>和其它的情况不一样，会有压缩存储，因此要使用特化版本
	void read_impl(const std::string& name, std::vector<bool>& val);
	void write_impl(const std::string& name, const std::vector<bool>& val);

	template<typename T>
	inline void read_impl(const std::string& name, std::vector<T, std::allocator<T>>& val)
	{

		int count = 0;
		read_impl(serialize_helper::pack_count(name), count); 

		x_array_flag_serialization_guard tmp_object_flag(name, *this);


		val.resize(count);
		for (int i = 0; i < count; ++i)
			read_impl(serialize_helper::pack_index(i), val[i]); // tinyxml2解析时不支持节点名为数字开头,不允许带点号


	}

	template<typename T>
	inline void write_impl(const std::string& name, const std::vector<T, std::allocator<T>>& val)
	{
		write_impl(serialize_helper::pack_count(name), (int) (val.size())); // name没有意义，只用于保持原型统一

		x_array_flag_serialization_guard tmp_object_flag(name, *this);

		for (size_t i = 0; i < val.size(); ++i)
			write_impl(serialize_helper::pack_index(i), val[i]); // tinyxml2解析时不支持节点名为数字开头,不允许带点号

	}

	template<typename T>
	inline void read_impl(const std::string& name, std::list<T, std::allocator<T>>& val)
	{
		int count = 0;
		read_impl(serialize_helper::pack_count(name), count); // name没有意义，只用于保持原型统一


		x_array_flag_serialization_guard tmp_object_flag(name, *this);


		val.clear();
		for (int i = 0; i < count; ++i)
		{
			T item;
			read_impl(serialize_helper::pack_index(i), item); // tinyxml2解析时不支持节点名为数字开头,不允许带点号
			val.push_back(item);
		}


	}

	template<typename T>
	inline void write_impl(const std::string& name, const std::list<T, std::allocator<T>>& val) // name没有意义，只用于保持原型统一
	{
		write_impl(serialize_helper::pack_count(name), (int) (val.size()));

		x_array_flag_serialization_guard tmp_object_flag(name, *this);

		size_t index = 0;
		for (const auto& x : val)
			write_impl(std::format("item_{}",index++), x); // tinyxml2解析时不支持节点名为数字开头,不允许带点号


	}

	template<typename T1, typename T2>
	inline void read_impl(const std::string& name, std::pair<T1, T2>& val) // name没有意义，只用于保持原型统一
	{
		// tinyxml2解析时不支持节点名为数字开头,不允许带点号
		T1 key;
		read_impl(std::format("{}_key",name), key);
		
		T2 value;
		read_impl(std::format("{}_value",name), value);

		val = std::make_pair(key, value);
	}

	template<typename T1, typename T2>
	inline void write_impl(const std::string& name, const std::pair<T1, T2>& val) // name没有意义，只用于保持原型统一
	{
		// tinyxml2解析时不支持节点名为数字开头,不允许带点号
		write_impl(std::format("{}_key",name), val.first);
		write_impl(std::format("{}_value",name), val.second);
	}

	template<typename TK, typename TV>
	inline void read_impl(const std::string& name,
		std::map<TK, TV, std::less<TK>, std::allocator<std::pair<const TK, TV>>>& val) // name没有意义，只用于保持原型统一
	{
		int count = 0;
		read_impl(serialize_helper::pack_count(name), count);

		x_array_flag_serialization_guard tmp_object_flag(name, *this);


		val.clear();
		for (int i = 0; i < count; ++i)
		{
			std::pair<TK, TV> item;
			read_impl(std::format("{}_item_{}",name,i), item); // tinyxml2解析时不支持节点名为数字开头,不允许带点号
			val.insert(item);
		}


	}

	template<typename TK, typename TV>
	inline void write_impl(const std::string& name,
		const std::map<TK, TV, std::less<TK>, std::allocator<std::pair<const TK, TV>>>& val) // name没有意义，只用于保持原型统一
	{
		write_impl(serialize_helper::pack_count(name), (int) (val.size()));
		write_impl(name, serialize_flag::array_bg);

		size_t index = 0;
		for (const auto& x : val)
			write_impl(std::format("{}_item_{}",name,index++), x); // tinyxml2解析时不支持节点名为数字开头,不允许带点号

		write_impl(name, serialize_flag::array_ed);
	}



private:
	friend class serialize_interface;
};

_JOY_UTILITY_END_
#endif
