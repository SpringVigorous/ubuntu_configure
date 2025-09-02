
#include "joy_utility/interface/data_node_base.h"
#include "joy_utility/tools/string_tools.h"
#include "joy_utility/tools/import_export_tools.h"
#include "joy_utility/kenels/harchive.h"

//#ifdef _DEBUG
//#define new DEBUG_NEW
//#endif



_JOY_UTILITY_BEGIN_



//////////////////////////////////////////////////////////////////////////
IMPLEMENT_SERIAL(data_node_base, HObject)

data_node_base::data_node_base(const std::string& node_name/* = ""*/, bool auto_recycle/* = true*/,
	children_recycling_type children_recycling/* = children_recycling_type::custom*/)
{
	m_name = node_name;
	m_parent = nullptr;
	m_node_tag = string_tools::generate_guid();
	m_auto_recycle = auto_recycle;
	m_children_recycling_type = children_recycling;

	// 构造函数要不应该调用设置默认值的接口，否则会触发数据变动通知，打开或新建文件的时候就多次触发了，最好是只放
	// 到新建文件的时候触发（打开不要触发）
	// set_default_value();
}

data_node_base::data_node_base(const data_node_base& src)
{
	// 构造的时候不通知，而是延迟到挂接到数据中心时触发相应通知
	data_node_notify_guard tmp(false);

	copy(src, true);
	m_parent = nullptr;

	// 构造函数要不应该调用设置默认值的接口，否则会触发数据变动通知，打开或新建文件的时候就多次触发了，最好是只放
	// 到新建文件的时候调用此接口（打开不要调用）
	// set_default_value();
}

data_node_base::~data_node_base()
{
	// 析构的时候不通知，框架流程会恰当处理对象的移除和通知的时机，单从此处的析构函数来说是不可能知道要不要
	// 触发通知的，有可能是程序在关闭造成不就出问题了，因此此处禁用通知
	data_node_notify_guard tmp(false);
	delete_all_children();
}

data_node_base& data_node_base::operator=(const data_node_base& node)
{
	if (&node == this) return *this;

	copy(node, true);
	return *this;
}

bool data_node_base::operator==(const data_node_base& node) const
{
	if (this == &node) return true;
	return is_equal(node);
}

const data_node_base* data_node_base::operator[](size_t index) const
{
	return m_children[index];
}

data_node_base* data_node_base::operator[](size_t index)
{
	return m_children[index];
}

void data_node_base::swap(data_node_base& right, bool swap_tag/* = true*/)
{
	if (this == &right) return;

	data_node_base* tmp = clone(swap_tag);
	if (!tmp) return;

	copy(right, swap_tag);
	right.copy(*tmp, swap_tag);
}

void data_node_base::swap(data_node_base& left, data_node_base& right, bool swap_tag/* = true*/)
{
	left.swap(right, swap_tag);
}

void data_node_base::serialize_members(member_rw_interface& mt)
{
	//x_object_flag_serialization_guard tmp_object_flag("data_node_base", mt);

	int version =1;
	mt & x_wrapper_macro_named(serialize_helper::pack_version("data_node_base"), version);
	mt & x_wrapper_macro( m_node_tag);
	mt & x_wrapper_macro( m_name);
	mt & x_wrapper_macro( m_node_info);
	mt & x_wrapper_macro_enum(m_children_recycling_type);
	mt & x_wrapper_macro( m_auto_recycle);
	serialize_children(mt);


}

void data_node_base::serialize_children(member_rw_interface& mt)
{
	//x_object_flag_serialization_guard tmp_object_flag("data_node_base_childen", mt);

	int children_version = 1;
	mt& x_wrapper_macro_named(serialize_helper::pack_version("data_node_base_children"), children_version);

	if (mt.is_storing())
	{
		size_t children_count = m_children.size();
		mt & x_wrapper_macro_named(serialize_helper::pack_count("m_children"), children_count);
		x_array_flag_serialization_guard children("m_children", mt);
		for (data_node_base* x : m_children) // 内部对象为指针，序列化工具不支持，要手工序列化
		{
			x_object_flag_serialization_guard children("child_item", mt);
			bool is_nullptr = nullptr == x;
			mt& x_wrapper_macro_named(serialize_helper::pack_flag("is_nullptr"), is_nullptr); // 显式写入bool值，增强代码可读性
			if (x)
			{
				std::string class_name = x->GetRuntimeClass()->className_;
				mt& x_wrapper_macro_named(serialize_helper::pack_flag("class_name"), class_name);
				mt& x_wrapper_macro_named(serialize_helper::pack_item(),*x);

			}

		}


	}
	else
	{
		mt& x_wrapper_macro(children_version);

		size_t children_count = 0;
		mt& x_wrapper_macro_named(serialize_helper::pack_count("m_children"), children_count);
		x_array_flag_serialization_guard children("m_children", mt);


		// 原有对象要析构，不能简单的清除
		delete_all_children();

		for (size_t i = 0; i < children_count; ++i) // 内部对象为指针，序列化工具不支持，要手工序列化
		{
			x_object_flag_serialization_guard children("child_item", mt);

			bool is_nullptr = false;
			mt& x_wrapper_macro_named(serialize_helper::pack_flag("is_nullptr"), is_nullptr);
			if (is_nullptr)
			{
				m_children.push_back(nullptr);
			}
			else
			{
				std::string class_name;
				mt& x_wrapper_macro_named(serialize_helper::pack_flag("class_name"), class_name);

				HObject* obj = HRuntimeClass::CreateObject(class_name);
				if (!obj)
				{
					m_children.push_back(nullptr); // 放个空对象，保证与写入时数据个数一样多
				}
				else
				{
					data_node_base* nd = dynamic_cast<data_node_base*>(obj);
					if (!nd)
					{
						safe_delete(obj);
					}
					else
					{
						nd->m_parent = this;
						mt& x_wrapper_macro_named(serialize_helper::pack_item(), *nd);
						m_children.push_back(nd);
					}
				}
			}

		}

	}
}

void data_node_base::set_default_value()
{
	// 保持原tag不变
	// m_node_tag = "";
	m_name = "";

	// 回收类型极为重要，不是用户构造或指定时不得随意修改，且此类参数与数据类的数值不一样，此类参数属于框架管理
	// 类的参数，设置默认值应该仅对数据类的成员进行设置即可
	//m_auto_recycle = node.m_auto_recycle;
	//m_children_recycling_type = node.m_children_recycling_type;

	for (data_node_base* x : m_children)
		if (x) x->set_default_value();

	notify_if_enable(notifer_action::post_updated_node);
}

void data_node_base::copy(const data_node_base& node, bool copy_tag/* = true */)
{
	if (&node == this) return;

	if (copy_tag) m_node_tag = node.m_node_tag;

	m_name = node.m_name;
	m_auto_recycle = node.m_auto_recycle;
	m_children_recycling_type = node.m_children_recycling_type;

	// 清除过程中压制一下，清除后再统一作一次更新通知即可，递归部分也要压制消息
	{
		data_node_notify_guard tmp(false);
		delete_all_children();

		for (data_node_base* x : node.m_children)
		{
			if (!x) continue;

			const HRuntimeClass* rt = x->GetRuntimeClass();
			if (!rt) continue;

			HObject* obj = HRuntimeClass::CreateObject(rt->className_);
			if (!obj) continue;

			data_node_base* new_node = dynamic_cast<data_node_base*>(obj);
			if (!new_node)
			{
				safe_delete(obj);
				continue;
			}

			new_node->copy(*x, copy_tag);
			// new_node->operator=(*x); // 不能用=号，因为没有复制tag
			new_node->m_parent = this;

			m_children.push_back(new_node);
		}
	}

	notify_if_enable(notifer_action::post_updated_node);
}

bool data_node_base::is_equal(const data_node_base& src, bool compare_children /*= false*/) const
{
	if (m_name != src.m_name) return false;
	if (m_node_info != src.m_node_info) return false;

	// 默认实现不比较节点的回收设置参数
	// if (m_auto_recycle != src.m_auto_recycle) return false;
	// if (m_children_recycling_type != src.m_children_recycling_type) return false;

	if (compare_children)
	{
		if (m_children.size() != src.m_children.size()) return false;
		for (size_t i = 0; i < m_children.size(); ++i)
		{
			if (nullptr == m_children[i] && nullptr == src.m_children[i]) continue; // both are nullptr means equal
			if (!m_children[i] || !src.m_children[i]) return false;
			if (!m_children[i]->is_equal(*src.m_children[i], compare_children)) return false;
		}
	}

	return true;
}

void data_node_base::set_recycling_type(bool auto_recycle)
{
	// 回收类型极为重要，不是用户构造或指定时不得随意修改，且此类参数与数据类的数值不一样，此类参数属于框架管理
	// 类的参数，设置值时不应该触发数据修改通知
	m_auto_recycle = auto_recycle;
}

bool data_node_base::is_auto_recyclable() const
{
	return m_auto_recycle;
}

void data_node_base::set_children_recycling_type(children_recycling_type recycling_type)
{
	// 回收类型极为重要，不是用户构造或指定时不得随意修改，且此类参数与数据类的数值不一样，此类参数属于框架管理
	// 类的参数，设置值时不应该触发数据修改通知
	m_children_recycling_type = recycling_type;
}

children_recycling_type data_node_base::get_children_recycling_type() const
{
	return m_children_recycling_type;
}

bool data_node_base::need_recycle() const
{
	// 先找离本节点最近的且子节点回收类型不为自定义方式的节点
	data_node_base* parent = m_parent;

	// nothing_to_do类型仅对直接子节点生效，不需要多级查找
	if (parent && children_recycling_type::nothing_to_do == parent->m_children_recycling_type) return false;

	while (true)
	{
		if (!parent) break;
		if (children_recycling_type::custom != parent->m_children_recycling_type) break;
		parent = parent->m_parent;
	}

	if (nullptr == parent)
		return m_auto_recycle;
	else
		return children_recycling_type::recyclable == parent->m_children_recycling_type;
}

data_node_base* data_node_base::clone(bool clone_tag/* = false*/) const
{
	// 动态创建出的对象具体全局唯一的tag
	std::string target_class_name = GetRuntimeClass()->className_;
	data_node_base* result = dynamic_cast<data_node_base*>(HRuntimeClass::CreateObject(target_class_name.c_str()));
	if (result) result->copy(*this, clone_tag); // 不会复制tag
	return result;
}



std::string data_node_base::get_node_tag() const
{
	return m_node_tag;
}

std::string data_node_base::rebuild_node_tag(bool return_new_tag /*= true*/)
{
	std::string new_tag = string_tools::generate_guid();
	std::string old_tag = get_node_tag();
	set_node_tag(new_tag);
	return (return_new_tag ? new_tag : old_tag);
}

void data_node_base::set_node_tag(const std::string& tag)
{
	m_node_tag = tag;
}

void data_node_base::swap_node_tag(data_node_base& node)
{
	std::string tmp = m_node_tag;
	m_node_tag = node.m_node_tag;
	node.m_node_tag = tmp;
}

std::string data_node_base::get_node_name() const
{
	return m_name;
}

void data_node_base::set_node_name(const std::string& name)
{
	m_name = name;
	notify_if_enable(notifer_action::post_updated_node);
}

std::string data_node_base::get_node_info() const
{
	return m_node_info;
}

void data_node_base::set_node_info(const std::string& info, bool need_notify_if_enable/* = false*/)
{
	m_node_info = info;
	if (need_notify_if_enable) notify_if_enable(notifer_action::post_updated_node);
}

bool data_node_base::has_children() const
{
	return (!m_children.empty());
}

data_node_base* data_node_base::add_child_node(data_node_base* node)
{
	if (!node) return nullptr;


	node->m_parent = this;
	m_children.push_back(node);
	node->notify_if_enable(notifer_action::post_added_node);

	return node;
}

data_node_base* data_node_base::insert_child_node(data_node_base* node, int index /*= -1*/, bool is_forward /*= true*/)
{
	if (!node) return nullptr;

	// 非法的数据或位置时直接在最后一个位置插入
	if ((int)m_children.size() <= index || m_children.empty() || index < -1)
	{
		m_children.push_back(node);
		node->m_parent = this;
		node->notify_if_enable(notifer_action::post_added_node);
		return node;
	}

	// 把特殊的-1转换为正常的下标（前面已经对子节点为空作为处理）
	int last_index = (int)m_children.size();
	if (-1 == index) index = last_index;

	// 把所有的后插入统一改为前插入，因为标准库使用的是前插入，这样转换后逻辑更简单，但有一个例外，是在最后一个元素
	// 的后面插入无法改为前插入，因为使用下标的方式是无法无法表示end()处的下标的，因此要特殊处理
	if (last_index == index && false == is_forward)
	{
		m_children.push_back(node);
		node->m_parent = this;
		node->notify_if_enable(notifer_action::post_added_node);
		return node;
	}

	// 其它的后插入操作均可转换为前插入
	if (false == is_forward)
	{
		++index;
		is_forward = true;
	}

	auto it = m_children.begin();
	advance(it, index);
	m_children.insert(it, node);
	node->m_parent = this;
	node->notify_if_enable(notifer_action::post_added_node);
	return node;
}

data_node_base* data_node_base::get_parent()
{
	return m_parent;
}

const data_node_base* data_node_base::get_parent() const
{
	return m_parent;
}

bool data_node_base::is_parent(data_node_base* node, bool find_all_parent /*= false*/)
{
	if (!node) return false;

	data_node_base* parent = const_cast<data_node_base*>(this);
	while (true)
	{
		parent = parent->get_parent();
		if (!parent) return false;

		if (parent == node) return true;
		if (!find_all_parent) return false;
	}

	return false;
}

bool data_node_base::is_parent(const std::string& node_tag, bool find_all_parent /*= false*/)
{
	return	true;
	//data_node_base* node = ;
	//return is_parent(node, find_all_parent);
}

data_node_base* data_node_base::get_root_node()
{
	const data_node_base* const_self = this;
	data_node_base* result = const_cast<data_node_base*>(const_self->get_root_node());
	return result;
}

const data_node_base* data_node_base::get_root_node() const
{
	const data_node_base* self_const = this;
	if (!m_parent) return self_const; // 没有父节点说明本身就是根

	data_node_base* last_parent = m_parent;
	data_node_base* current_parent = m_parent;

	while (true)
	{
		current_parent = current_parent->get_parent();
		if (!current_parent) return last_parent;

		last_parent = current_parent;
	}

	return nullptr;
}

std::vector<data_node_base*>& data_node_base::get_children()
{
	return m_children;
}

std::vector<const data_node_base*> data_node_base::get_children() const
{
	std::vector<const data_node_base*> const_children;
	for (data_node_base* x : m_children) const_children.push_back(x);

	return const_children;
}

size_t data_node_base::get_children_count() const
{
	return m_children.size();
}

void data_node_base::resize_children(size_t sz)
{
	m_children.resize(sz, nullptr);
}

bool data_node_base::is_child_exist_by_tag(const std::string& node_tag, bool find_all_children /*= false*/)
{
	for (data_node_base* x : m_children)
	{
		if (!x) continue;
		if (x->m_node_tag == node_tag) return true;
		if (find_all_children)
		{
			bool flag = x->is_child_exist_by_tag(node_tag, true);
			if (flag) return true;
		}
	}

	return false;
}

bool data_node_base::is_child_exist_by_name(const std::string& node_name, bool find_all_children /*= false*/)
{
	for (data_node_base* x : m_children)
	{
		if (!x) continue;
		if (x->m_name == node_name) return true;
		if (find_all_children)
		{
			bool flag = x->is_child_exist_by_name(node_name, true);
			if (flag) return true;
		}
	}

	return false;
}

data_node_base* data_node_base::get_child(const std::string& node_tag, bool find_all_children/* = false*/)
{
	const data_node_base* const_self = this;
	data_node_base* result = const_cast<data_node_base*>(const_self->get_child(node_tag, find_all_children));
	return result;
}

data_node_base* data_node_base::get_child(size_t index)
{
	const data_node_base* const_self = this;
	data_node_base* result = const_cast<data_node_base*>(const_self->get_child(index));
	return result;
}

const data_node_base* data_node_base::get_child(const std::string& node_tag, bool find_all_children /*= false*/) const
{
	for (data_node_base* x : m_children)
	{
		if (!x) return nullptr;
		if (x->m_node_tag == node_tag) return x;
		if (find_all_children)
		{
			data_node_base* tmp = x->get_child(node_tag, true);
			if (tmp) return tmp;
		}
	}

	return nullptr;
}

const data_node_base* data_node_base::get_child(size_t index) const
{
	if (index >= m_children.size())
		return nullptr;
	else
		return m_children[index];
}

void data_node_base::set_child(size_t index, data_node_base* node)
{
	if (m_children.size() <= index) return;

	// 为空也改
	if (!m_children[index])
	{
		data_node_notify_guard tmp(false);
		m_children[index] = node;
	}
	else
	{
		data_node_notify_guard tmp(false);

		m_children[index]->delete_all_children();
		if (m_children[index]->need_recycle()) safe_delete(m_children[index]);

		m_children[index] = node;
		node->m_parent = this;
	}

	notify_if_enable(notifer_action::post_updated_node);
}

void data_node_base::notify_if_enable(notifer_action ac)
{
	
}

void data_node_base::post_notify_if_enable(notifer_action ac)
{
	
}

bool data_node_base::is_joined_data_center()
{
	return false;
}

data_node_base* data_node_base::release_child(size_t index)
{
	if (m_children.empty() || index >= m_children.size()) return nullptr;

	data_node_base* res = m_children[index];
	m_children[index] = nullptr;
	return res;
}

void data_node_base::delete_data_node_self(bool force_remove_items/* = false*/)
{
	if (!need_recycle()) return;

	// 如果当前节点为数据根节点，则直接销毁数据中心(其实这种情况应该是不可能通过界面由用户直接点击节点删除触发的)
	//if (data_center::get_data_root() == this)
	//{
	//	// 数据中心置成员指针为空没关系，只要不是用的this即可
	//	data_center::close_file();
	//	data_center::destroy_data();
	//	return;
	//}

	// 清理子节点（不能通过删除自身来借助析构函数完成递归清理动作，因为当前节点有可能是不可自动回收的，但子节点却需要回收）
	// 内部会发相应的通知
	delete_all_children(force_remove_items);

	// 如果要删除的节点的父节点存在，则直接通过父节点进行删除并返回（没挂接到数据中心也能删除）
	data_node_base* parent = get_parent();
	if (parent)
	{
		for (size_t i = 0; i < parent->get_children_count(); ++i)
		{
			data_node_base* cur_node = parent->get_child(i);
			if (cur_node != this) continue;

			if (children_recycling_type::nothing_to_do == parent->m_children_recycling_type)
			{
				if (force_remove_items)
				{
					notify_if_enable(notifer_action::pre_removed_node);
					parent->m_children.erase(parent->m_children.begin() + i);
					notify_if_enable(notifer_action::post_removed_node);
				}

				return;
			}

			// 不能删，此时本对象还在没有执行结束，删除本对象必崩溃，放在返回前删除
			//safe_delete(parent->m_children[i]);
			notify_if_enable(notifer_action::pre_removed_node);
			parent->m_children.erase(parent->m_children.begin() + i);
			notify_if_enable(notifer_action::post_removed_node);
			break;
		}
	}

	// 如果要删除的节点的父节点不存在，则直接销毁其节点（没挂接到数据中心也能删除）
	if (need_recycle()) delete this; // 不能再置为nullptr，因为对象已经不存在了
}

void data_node_base::delete_all_children(bool force_remove_items/* = false*/)
{
	if (children_recycling_type::nothing_to_do == m_children_recycling_type && !force_remove_items) return;
	if (m_children.empty()) return;

	// 临时压制通知，提高效率，避免每个节点删除都触发通知，删除完成后统一触发一次即可
	{
		data_node_notify_guard tmp(false);
		for (data_node_base* x : m_children)
		{
			if (!x) continue;

			// 必须手工递归调用，而不是自由交析构函数来实现递归清理，因为有些节点是不能删除的，但子节点却需要删
			// 除，由于没有调用delete，不会析构，导致这类子节点未被清理掉，造成内存泄漏。
			if (x->has_children()) x->delete_all_children(force_remove_items);
			if (x->need_recycle()) safe_delete(x);
		}
	}

	m_children.clear(); // 移除所有子节点	
	notify_if_enable(notifer_action::post_updated_node); // 通知当前节点有更新
}

void data_node_base::delete_child_node(data_node_base* node,
	bool find_all_children /*= false*/, bool force_remove_items/* = false*/)
{
	if (!node) return;
	delete_child_node(node->get_node_tag(), find_all_children, force_remove_items);
}

void data_node_base::delete_child_node(const std::string& tag,
	bool find_all_children /*= false*/, bool force_remove_items/* = false*/)
{
	if (children_recycling_type::nothing_to_do == m_children_recycling_type && !force_remove_items) return;

	for (auto it = m_children.begin(); it != m_children.end(); ++it)
	{
		if (!(*it)) continue;
		if ((*it)->m_node_tag == tag)
		{
			if ((*it)->need_recycle())
			{
				// 先发出通知告之指定节点即将被删除
				(*it)->notify_if_enable(notifer_action::pre_removed_node);

				// 如果使用及时通知，则要放在delete之后，此时对象已经删除了，再调用非静态成员会崩溃，放之前则对象还没有删除，
				// 会误通知，有些窗口要根据这个信息更新界面，如果对象还没有删除，会造成数据显示错误，因此放在之前，且使用
				// post的方式来通知就完美解决问题了
				(*it)->post_notify_if_enable(notifer_action::post_removed_node);

				safe_delete(*it);
				m_children.erase(it);
			}
			else
			{
				// 不需要回收时必务必把它与数据中心的关联关系断开，以防止数据中心遍历到
				(*it)->m_parent = nullptr;
			}

			return;
		}
		else
		{
			if (find_all_children) (*it)->delete_child_node(tag, find_all_children, force_remove_items);
		}
	}
}

void data_node_base::delete_child_node(size_t index, bool force_remove_items /*= false*/)
{
	if (children_recycling_type::nothing_to_do == m_children_recycling_type && !force_remove_items) return;
	if (index >= m_children.size()) return;

	delete_child_node(m_children.begin() + index, force_remove_items);
}

std::vector<data_node_base*>::iterator data_node_base::delete_child_node(std::vector<data_node_base*>::iterator it, bool force_remove_items /*= false*/)
{
	if (it == m_children.end()) return m_children.end();

	// 最好不要直接用it + 1，以防非随机迭代器
	std::vector<data_node_base*>::iterator ret_it = it;
	++ret_it;

	data_node_base* node = *it;

	if (children_recycling_type::nothing_to_do == m_children_recycling_type)
	{
		if (!force_remove_items) return ret_it; // 什么也不做

		if (node)
		{
			// 先发出通知告之指定节点即将被删除
			node->notify_if_enable(notifer_action::pre_removed_node);

			// 如果使用及时通知，则要放在delete之后，此时对象已经删除了，再调用非静态成员会崩溃，放之前则对象还没有删除，
			// 会误通知，有些窗口要根据这个信息更新界面，如果对象还没有删除，会造成数据显示错误，因此放在之前，且使用
			// post的方式来通知就完美解决问题了
			node->post_notify_if_enable(notifer_action::post_removed_node);
		}

		ret_it = m_children.erase(it); // 强制删除时只移除
		if (!node) notify_if_enable(notifer_action::post_updated_node); // 通知当前节点有更新

		return ret_it;
	}

	// 下标方式删除元素时，空指针也要能正常移除
	if (!node)
	{
		ret_it = m_children.erase(it);
		notify_if_enable(notifer_action::post_updated_node); // 通知当前节点有更新
		return ret_it;
	}

	// 先发出通知告之指定节点即将被删除
	node->notify_if_enable(notifer_action::pre_removed_node);

	// 如果使用及时通知，则要放在delete之后，此时对象已经删除了，再调用非静态成员会崩溃，放之前则对象还没有删除，
	// 会误通知，有些窗口要根据这个信息更新界面，如果对象还没有删除，会造成数据显示错误，因此放在之前，且使用
	// post的方式来通知就完美解决问题了
	node->post_notify_if_enable(notifer_action::post_removed_node);

	// 不论有没有回收都移除
	ret_it = m_children.erase(it);

	// 必须先移除再销毁，否则指向此元素的迭代器将被损坏！！！
	if (node->need_recycle()) safe_delete(node);

	return ret_it;
}

void data_node_base::delete_children_nodes(std::vector<data_node_base*>::iterator be,
	std::vector<data_node_base*>::iterator en, bool force_remove_items /*= false*/)
{
	if (children_recycling_type::nothing_to_do == m_children_recycling_type
		&& !force_remove_items)
		return;

	// 删除元素的时候不能用be,en作为循环，因为删除元素后会导致en失效，每次都要实时获取end()，但这里没有容器，无
	// 法获取，因此把要删除的元素先记下来，先判断要不要销毁，处理完后只能调用一次erase进行删除，否则迭代器失效，
	// 而且不能通过多次调用删除单个元素的接口来处理，这里将迭代器转为下标来处理避开这个问题

	std::vector<size_t> will_del_index;
	size_t be_index = std::distance(children_begin(), be);

	for (auto it = be; it != en; ++it)
	{
		will_del_index.push_back(be_index);
		++be_index;
	}

	// 用下标的方式删除，为防止下标变化，必须从后往前删除
	{
		data_node_notify_guard tmp(false);
		for (int i = (int)will_del_index.size() - 1; i >= 0; --i)
			delete_child_node(will_del_index[i], force_remove_items);
	}

	notify_if_enable(notifer_action::post_updated_node);
}

std::vector<data_node_base*>::iterator data_node_base::children_begin()
{
	return m_children.begin();
}

std::vector<data_node_base*>::iterator data_node_base::children_end()
{
	return m_children.end();
}

std::vector<data_node_base*>::reverse_iterator data_node_base::children_rbegin()
{
	return m_children.rbegin();
}

std::vector<data_node_base*>::reverse_iterator data_node_base::children_rend()
{
	return m_children.rend();
}

std::vector<data_node_base*>::const_iterator data_node_base::children_cbegin()
{
	return m_children.cbegin();
}

std::vector<data_node_base*>::const_iterator data_node_base::children_cend()
{
	return m_children.cend();
}

std::vector<data_node_base*>::const_reverse_iterator data_node_base::children_crbegin()
{
	return m_children.crbegin();
}

std::vector<data_node_base*>::const_reverse_iterator data_node_base::children_crend()
{
	return m_children.crend();
}

bool travel_current_node_tree_implement(int current_depth, data_node_base* current_node, std::function<bool(data_node_base*)> access_func, int depth /*= -1*/)
{
	// 如果有节点访问函数返回true，则本函数返回true，其它情况均返回false，如异常或正常结束时返回false

	if (!current_node || !access_func) return false;
	if (current_depth < 0) return false;

	bool need_access_children = false;
	bool need_access_current_node = false;
	if (0 == depth)
	{
		if (0 == current_depth) need_access_current_node = true;
	}
	else if (-1 == depth)
	{
		need_access_children = true;
		need_access_current_node = true;
	}
	else if (depth > 0)
	{
		if (current_depth <= depth) need_access_current_node = true;
		if (current_depth < depth) need_access_children = true;
	}
	else
	{
		// nothing;
	}

	if (need_access_current_node && access_func(current_node)) return true;

	if (need_access_children)
	{
		for (size_t i = 0; i < current_node->get_children_count(); ++i)
			if (travel_current_node_tree_implement(current_depth + 1,
				current_node->get_child(i), access_func, depth))
				return true;
	}

	return false;
}

bool travel_current_cosnt_node_tree_implement(int current_depth, const data_node_base* current_node, std::function<bool(const data_node_base*)> access_func, int depth /*= -1*/)
{
	// 如果有节点访问函数返回true，则本函数返回true，其它情况均返回false，如异常或正常结束时返回false

	if (!current_node || !access_func) return false;
	if (current_depth < 0) return false;

	bool need_access_children = false;
	bool need_access_current_node = false;
	if (0 == depth)
	{
		if (0 == current_depth) need_access_current_node = true;
	}
	else if (-1 == depth)
	{
		need_access_children = true;
		need_access_current_node = true;
	}
	else if (depth > 0)
	{
		if (current_depth <= depth) need_access_current_node = true;
		if (current_depth < depth) need_access_children = true;
	}
	else
	{
		// nothing;
	}

	if (need_access_current_node && access_func(current_node)) return true;

	if (need_access_children)
	{
		for (size_t i = 0; i < current_node->get_children_count(); ++i)
			if (travel_current_cosnt_node_tree_implement(current_depth + 1,
				current_node->get_child(i), access_func, depth))
				return true;
	}

	return false;
}

void data_node_base::travel_current_node_tree(std::function<bool(data_node_base*)> access_func, int depth /*= -1*/)
{
	travel_current_node_tree_implement(0, this, access_func, depth); // 当前为根，第0层
}

void data_node_base::travel_current_node_tree(std::function<bool(const data_node_base*)> access_func, int depth /*= -1*/) const
{
	travel_current_cosnt_node_tree_implement(0, this, access_func, depth); // 当前为根，第0层
}

bool data_node_base::import_data(int type, const std::string& full_path_name)
{
	//CWaitCursor wait_cur;

	if (full_path_name.empty()) return false;

	// 序列化过程中先禁用通知功能
	{
		data_node_notify_guard tmp_guard(false);

		delete_all_children();

		if (0 == type)
		{
			//CFile new_file;
			//BOOL flag = new_file.Open(full_path_name, CFile::modeRead | CFile::modeNoTruncate);
			//if (!flag) return false;

			//CArchive mfc_ar(&new_file, CArchive::load);
			//bin_archive ar(mfc_ar);
			//serialize_members(ar); // 参数为引用，具有多态性
			//mfc_ar.Close();
			//new_file.Close();
			import_from_bin_file(full_path_name, *this);

		}
		else if (1 == type)
		{
			import_from_json_file(full_path_name, *this);

		}
		else if (2 == type)
		{
			//tinyxml2::XMLDocument doc;
			//if (tinyxml2::XML_SUCCESS != doc.LoadFile(string_tools::CString_to_string(full_path_name).c_str())) return false;

			//tinyxml2::XMLElement* xml = doc.FirstChildElement("xml_root"); // 写入的时候最外层会强制加上此节点，否则无法序列化
			//if (!xml) return false;

			//xml_archive ar(xml, false);
			//serialize_members(ar);

			import_from_xml_file(full_path_name, *this);


		}
		else
		{
			return false;
		}
	}

	notify_if_enable(notifer_action::post_updated_node);

	return true;
}




bool data_node_base::import_data(const std::string& value, int type)
{
	if (value.empty()) return false;

	// 序列化过程中先禁用通知功能
	{
		data_node_notify_guard tmp_guard(false);

		delete_all_children();

		if (0 == type)
		{
			//// base64编码不含东亚编码，转换为通用字符串时不要调用字符串转换函数，直接强转，效率要高好几倍，因为字符串
			//// 转换函数要根据本地化信息来转换编码
			//string bin_data_base_64;
			//for (int i = 0; i < value.GetLength(); ++i)
			//	bin_data_base_64 += (char)value[i];

			//if (!import_data(bin_data_base_64)) return false;
		}
		else if (1 == type)
		{
			//string full_json_text = string_tools::CString_to_string(value);
			//Json::Value json_obj;
			//Json::Reader reader;
			//if ( & x_wrapper_macro( json_obj)) return false; // json内容必须为utf-8编码
			//json_archive ar(&json_obj, false);
			//serialize_members(ar);
		}
		else if (2 == type)
		{
			//tinyxml2::XMLDocument doc;
			//string full_xml_text = string_tools::CString_to_string(value);
			//if (tinyxml2::XML_SUCCESS != doc.LoadFile(full_xml_text.c_str())) return false;

			//tinyxml2::XMLElement* xml = doc.FirstChildElement("xml_root"); // 写入的时候最外层会强制加上此节点，否则无法序列化
			//if (!xml) return false;

			//xml_archive ar(xml, false);
			//serialize_members(ar);
		}
		else
		{
			return false;
		}
	}

	notify_if_enable(notifer_action::post_updated_node);

	return true;
}

bool data_node_base::export_data(int type, const std::string& full_path_name)
{
	//CWaitCursor wait_cur;

	if (full_path_name.empty()) return false;



	// 序列化过程中先禁用通知功能
	{
		data_node_notify_guard tmp_guard(false);

		if (0 == type)
		{
			//CFile new_file;
			//BOOL flag = new_file.Open(full_path_name, CFile::modeCreate | CFile::modeWrite);
			//if (!flag) return false;

			//CArchive mfc_ar(&new_file, CArchive::store);
			//bin_archive ar(mfc_ar);
			//serialize_members(ar);
			//mfc_ar.Close();
			//new_file.Close();
		}
		else if (1 == type)
		{
			//Json::Value json;
			//json_archive serialize_ar(&json, true);
			//serialize_members(serialize_ar);
			//string res = json.toStyledString();

			//ofstream new_file(string_tools::CString_to_string(full_path_name), ios::out);
			//if (!new_file.is_open() && !new_file.good()) return false;

			//new_file & x_wrapper_macro( res.length());
			//new_file.close();
		}
		else if (2 == type)
		{
			//const char* declaration = "<?xml version=\"1.0\" encoding=\"utf-8\"?>";
			//tinyxml2::XMLDocument doc;
			//doc.Parse(declaration);// 清空内容并生成一个带默认声明的xml文档（这种方式比使用接口添加声明更简单）

			//tinyxml2::XMLElement* new_node = doc.NewElement("xml_root"); // 写入的时候最外层会强制加上此节点，否则无法序列化
			//if (!new_node) return false;

			//xml_archive ar(new_node, true);
			//serialize_members(ar);
			//doc.InsertEndChild(new_node);

			//tinyxml2::XMLError err = doc.SaveFile(string_tools::CString_to_string(full_path_name).c_str());
			//if (tinyxml2::XML_NO_ERROR != err) return false;
		}
		else
		{
			return false;
		}
	}

	return true;
}




bool data_node_base::export_data(std::string& value, int type)
{
	value = "";

	//// 序列化过程中先禁用通知功能
	//data_node_notify_guard tmp_guard(false);

	//if (0 == type)
	//{
	//	string bin_data_base_64;
	//	if (!export_data(bin_data_base_64)) return false;
	//	if (bin_data_base_64.length() <= 0) return false;

	//	// base64编码不含东亚编码，转换为通用字符串时不要调用字符串转换函数，直接强转，效率要高好几倍，因为字符串
	//	// 转换函数要根据本地化信息来转换编码
	//	for (size_t i = 0; i < bin_data_base_64.length(); ++i)
	//		value += (TCHAR)bin_data_base_64[i];
	//}
	//else if (1 == type)
	//{
	//	Json::Value json;
	//	json_archive serialize_ar(&json, true);
	//	serialize_members(serialize_ar);
	//	string res = json.toStyledString();
	//	value = string_tools::string_to_CString(res);
	//}
	//else if (2 == type)
	//{
	//	const char* declaration = "<?xml version=\"1.0\" encoding=\"utf-8\"?>";
	//	tinyxml2::XMLDocument doc;
	//	doc.Parse(declaration);// 清空内容并生成一个带默认声明的xml文档（这种方式比使用接口添加声明更简单）

	//	tinyxml2::XMLElement* new_node = doc.NewElement("xml_root"); // 写入的时候最外层会强制加上此节点，否则无法序列化
	//	if (!new_node) return false;

	//	xml_archive ar(new_node, true);
	//	serialize_members(ar);
	//	doc.InsertEndChild(new_node);

	//	tinyxml2::XMLPrinter printer;
	//	doc.Accept(&printer);
	//	string res = printer.CStr();

	//	// base64编码不含东亚编码，转换为通用字符串时不要调用字符串转换函数，直接强转，效率要高好几倍，因为字符串
	//	// 转换函数要根据本地化信息来转换编码
	//	for (size_t i = 0; i < res.length(); ++i)
	//		value += (TCHAR)res[i];
	//}
	//else
	//{
	//	return false;
	//}

	return true;
}

bool data_node_base::take_snapshot(const std::string& name)
{
	if (!is_joined_data_center()) return false;

	// ...

	return false;
}


data_node_notify_guard::data_node_notify_guard(bool enable)
{
	m_old_enable = enable;
}

data_node_notify_guard::~data_node_notify_guard()
{
	
}





_JOY_UTILITY_END_