﻿#pragma once
#ifndef __JOY_UTILITY_DATA_NODE_BASE_H__
#define __JOY_UTILITY_DATA_NODE_BASE_H__
#include <filesystem>
#include <functional>
#include "joy_utility/joy_utility_macro.h"
#include "joy_utility/kenels/hobject.h"
#include "joy_utility/interface/serialize_interface.h"




_JOY_UTILITY_BEGIN_
using path_object = std::filesystem::path;



// 注意，通知仅针对数据变动，不是针对界面窗口变动触发的，界面的变动如果没有导致数据变动是不会触发通知的
enum class notifer_action
{
	post_project_loaded,		// 数据中心被加载（打开或新建）
	post_project_saved_as,		// 数据中心被另存（一般用于需要在项目不关闭的情况下响应项目名变了，因为项目名不存放在数据中心）
	pre_project_closed,			// 数据中心即将被关闭（关闭项目或退出程序，此消息不建议使用post方式触发）
	post_added_node,			// 数据中心当前节点新增后
	pre_removed_node,			// 数据中心当前节点删除前（此消息不建议使用post方式触发）
	post_removed_node,			// 数据中心当前节点删除后
	post_updated_node,			// 数据中心当前节点数据更新后
};


// 数据中心子节点的自动回收类型
// 注意，回收类型会对当前节点下的所有子节点生效，无论这个子节点是不是直接子节点
// 细节参考节点的need_recycle()方法注释内容
// 回收类型仅在回收时生效，如调用 其它时候不受此影响，如序列化，或用户自己删除等情况
// nothing_to_do类型目前仅在以下接口中生效(详情参考接口注释内容)，其它接口行为暂不受此类型影响：
//   need_recycle();
//   delete_data_node_self();
//   delete_all_children();
//   delete_child_node();
enum class children_recycling_type
{
	nothing_to_do,				// 仅当回收时有效，此时不对任何直接子节点进行析构（此类型不往更深层自动传播），也不从子节点容器中移除元素！！！全权由数据类的派生类自行处理
	non_recycle,				// 不允许框架自动回收，无论子节点指定的回收方式是什么均忽略，但节点允许从容器中移除
	recyclable,					// 由框架自动回收并析构子节点，无论子节点指定的回收方式是什么均忽略不管，且将子节点允许从容器中移除
	custom,						// 按子节点指定的回收方式处理，但子节点将从容器中移除
};





// 项目节点数据（一般接口不要从实体类派生，因此命名不带interface，此数据类框架需要动态创建，因此要支持mfc动态创建）
class JOY_UTILITY_API data_node_base : public HObject, public serialize_interface
{
	DECLARE_SERIAL(data_node_base)

public:
	// 如果auto_recycle为true则析构或需要删除的本节点时会调用delete，否则不调用
	// children_recycling为子节点的收回方式，注意，回收类型会对当前节点下的所有子节点生效，无论这个子节点是不是直接子节点
	// 如果本节点有多个父节点指定了子节点的清理方式均不为自定义方式，则以离本节点最近的父节点为指定原则，详见need_recycle()接口
	// need_clear_children为true表示清理子节点后会将子节点的容器清空，如果为false，则表示调用
	data_node_base(const std::string& node_name = "", bool auto_recycle = true,
		children_recycling_type children_recycling = children_recycling_type::custom);

	// 父节点会置为空，子节点关联关系原样拷贝,tag也会拷贝，如果要新生成tag可以使用copy并指定不复制tag或
	// 者对复制后的目标对象调用rebuild_tag()生成新的tag
	data_node_base(const data_node_base& src);
	virtual ~data_node_base();

	// 数据拷贝，注意拷贝会连同tag一起原样复制，如果要新生成tag可以使用copy并指定不复制tag或者对复制后的目
	// 标对象调用rebuild_tag()生成新的tag
	data_node_base& operator=(const data_node_base& node);

	// 调用is_equal虚函数进行比较
	bool operator==(const data_node_base& node) const;

	// 下标运算符
	const data_node_base* operator[](size_t index) const;
	data_node_base* operator[](size_t index);

	// 交换两个对象的值（具备多态性，调用时务必保证两个对象的派生类型一致）
	// swap_tag为true时此接口会将两个对象的tag也交换
	void swap(data_node_base& right, bool swap_tag = true);
	static void swap(data_node_base& left, data_node_base& right, bool swap_tag = true);

public:
	// 本节点数据序列化，默认实现为先序列化自身数据，再调用serialize_children序列化子节点数据
	virtual void serialize_members(member_rw_interface& mt); 

	// 定制子节点的序列化。序列化本节点数据过程中会调用此接口进行子节点的序列化，提供此接口以定制其行为
	// 对于一些场景复杂的数据节点，有此节点是固化的且派生类各不相同，有必要对其顺序、样式进行定制和版本控制
	// 内部默认实现按子节点顺序依次序列化
	virtual void serialize_children(member_rw_interface& mt);

	// 设置数据为默认值，创建节点或其它需要时调用（如新建项目后会调用），实现时请注意是否要清空原数据
	// 目前框架会在以下情况调用，其它场合根据用户需要手工调用：
	// 1.新建项目时生成数据中心后会调用
	// 2.打开项目前会调用
	// 3.对象生成后需要初始化时
	virtual void set_default_value();

	// 数据拷贝，注意拷贝会连同tag一起原样复制，如果要新生成tag可以使用copy并指定不复制tag或者对复制后的目
	// 注意：此接口实现时非内置类型的对象复制不得调用=号操作符，否则会造成死循环（=号操作符内部调用copy完成）
	// 此接口具备多态性，调用时务必保证两个对象的派生类型一致
	// 考虑到业务功能的复杂性，新增tag的复制，copy_tag为true时允许复制tag
	virtual void copy(const data_node_base& node, bool copy_tag = true);

	// 判断两个节点内容是否相同,节点标识tag不参与比较，父节点不参与比较
	// compare_children为true表示子节点也参与比较，否则不比子节点
	// 注意，默认实现不比较节点的回收设置参数
	// 此接口具备多态性，调用时务必保证两个对象的派生类型一致
	virtual bool is_equal(const data_node_base& src, bool compare_children = false) const;

public:
	// 获取或设置本节点的回收类型，此参数仅对当本节点有用，不作用于子节点（设置时不会触发数据更新的通知）
	// 如果auto_recycle为true则析构或需要删除的本节点时会调用delete，否则不调用
	void set_recycling_type(bool auto_recycle);
	bool is_auto_recyclable() const;

	// 获取或设置本节点的子节点回收类型，此参数仅对所有子节点均有效，不论是否为直接子节点（设置时不会触发数据更新的通知）
	void set_children_recycling_type(children_recycling_type recycling_type);
	children_recycling_type get_children_recycling_type() const;

	// 当前节点在清理时是否需要delete回收，如果需要则执行delete，否则仅被移除或跳过，不对其进行delete
	// 注意：此接口会检查父节点的children_recycling_type，如果父节点指定了强制回收子节点，或不回收子节点，则
	// 按父节点的指定操作执行，此时忽略本节点的自动回收设置。仅当父节点指定了自定义回收方式才会按照本节点的回收方
	// 式处理。此处说的父节点为本节点的直接父节点一直往上到根的任意一个父节点，如果有多个父节点均设置子节点回收类
	// 型为回收或不回收（不是自定义方式），则以最近的父节点为判断原则
	bool need_recycle() const;

	// 根据当前节点克隆一个相同的节点，此接口克隆出来的对象标识与原对象不一样，以以确保全局唯一性
	// 此接口克隆出的对象与当前对象的真实派生类相同，如果当前对象是data_node_base的派生类，则克隆出来的对象也是
	// 派生类对象，这一点是data_node_base拷贝构造函数做不到的
	// 此功能常用于不需要依赖派生类头文件实现派生类对象的生成
	// 生成的对象为独立对象，即并未挂接到数据中心，生成对象的内存由使用者自行管理
	// 注意：派生类请注意正确实现DECLARE_SERIAL功能
	// 考虑到业务功能的复杂性，新增tag的克隆，clone_tag为true时允许克隆tag
	data_node_base* clone(bool clone_tag = false) const;
	// 获取当前节点tag形式或名称形式的路径
	// 节点tag形式的路径表示由节点的tag组成的路径（用'\\'分隔）
	// 节点名称形式的路径表示由节点的名称组成的路径（用'\\'分隔）
	// tail_is_folder为true表示尾节点当作文件夹节点，否则表示文件节点

	// 返回节点标识
	std::string get_node_tag() const;

	// 重新生成新的tag替换掉内部的tag值，return_new_tag为true表示返回新生成的tag，为false表示返回原来的tag
	std::string rebuild_node_tag(bool return_new_tag = true);

	// 原则上为确保对象的全局唯一性tag不提供接口供外部修改，但考虑到业务功能的复杂性，新增tag的接口，如非必要请慎用！
	void set_node_tag(const std::string& tag);

	// 互两个节点的tag（不会触发节点数据修改的通知，如有需要请手工触发）
	void swap_node_tag(data_node_base& node);

	// 返回或设置树节点的名称，此名称一般用于界面显示
	std::string get_node_name() const;
	void set_node_name(const std::string& name);

	// 返回或设置节点信息，允许用户外部存储任何节点注释、信息等少量信息，内容含义的解释由用户决定
	std::string get_node_info() const;

	// 修改节点附加信息，此信息更多的是用于用户特殊信息存储，修改数据时框架默认不发通知
	void set_node_info(const std::string& info, bool need_notify_if_enable = false);

	// 插入一个节点，节点对象内存由本类接管,并返回添加后的节点，以便提高使用者的便利性
	// 注意，子节点或子树的任何节点不得是数据中心中已经存在的节点
	data_node_base* add_child_node(data_node_base* node);

	// 在指定索引的节点前/后插入子节点
	// 如果为-1表示在最后一个元素向前、向后插入，如果指定的下标不存在，则直接插入到最后一个元素后面
	// 注意，子节点或子树的任何节点不得是数据中心中已经存在的节点
	data_node_base* insert_child_node(data_node_base* node, int index = -1, bool is_forward = true);

	// 得到直接父节点（不允许设置，有框架维护，如果需要请借助set_child间接实现）
	data_node_base* get_parent();
	const data_node_base* get_parent() const;

	// 判断节点是否是本节点的父节点,find_all_parent为true表示会递归往上找，否则只找直接父节点
	bool is_parent(data_node_base* node, bool find_all_parent = false);
	bool is_parent(const std::string& node_tag, bool find_all_parent = false);

	// 得到本节点所在子树的根（如果树已经挂在数据中心上了，则返回的节点与直接从数据中心取得的数据节点是同一节点，
	// 否则仅为当前树的根节点，建议如果数据是用户自己创建并维护但还不属于数据中心的，则调用此函数，如果是数据中
	// 心中的节点，则尽量直接调用数据中心获取数据根节点，因为从数据中心取的时间复杂度为O(1)，本接口的时间复杂度
	// 为O(n)）
	data_node_base* get_root_node();
	const data_node_base* get_root_node() const;

	// 得到子节点，节点由项目中心及内部维护
	std::vector<data_node_base*>& get_children();
	std::vector<const data_node_base*> get_children() const; // 此接口不能返回引用类型

	// 根据tag得到节点，find_all_children为false表示仅从本节点的直接子节点中找，true表示递归查找所有子节点
	// 如果条件允许的情况下，可考虑使用路径方式获取节点将会更高效，详情参见相应接口
	data_node_base* get_child(const std::string& node_tag, bool find_all_children = false);
	const data_node_base* get_child(const std::string& node_tag, bool find_all_children = false) const;

	// 是否有子节点
	bool has_children() const;

	// 获得或设置当前节点的直接子节点个数,设置借口与STL的resize行为一致,已有数据保持不变，多的删除，不够的补nullptr
	size_t get_children_count() const;
	void resize_children(size_t sz);

	// 指定的子节点是否存在，find_all_children为false表示仅从本节点的直接子节点中找，true表示递归查找所有子节点
	bool is_child_exist_by_tag(const std::string& node_tag, bool find_all_children = false);
	bool is_child_exist_by_name(const std::string& node_name, bool find_all_children = false);

	// 从当前节点的直接子节点中返回指定索引的节点(从0开始)
	data_node_base* get_child(size_t index);
	const data_node_base* get_child(size_t index) const;

	// 改写指定索引的元素
	void set_child(size_t index, data_node_base* node);

	// 通知框架数据中心的当前节点触发了消息，如果通知被禁用或节点没有挂接到数据中心上，是不会触发通知的
	void notify_if_enable(notifer_action ac);

	// 以post方式通知框架数据中心的当前节点触发了消息（主要用于有界面联动更新时确保界面创建的机制完成再触发更新）
	// 当通知被触发时可能节点已经被删除了，这时将不会触发，如果进行的操作可能有这种情况发生（如删除节点时），请
	// 尽量使用数据中心直接发post通知更稳妥
	void post_notify_if_enable(notifer_action ac);

	// 判断本节点是否已经挂接到数据中心
	bool is_joined_data_center();

	// 释放指定节点的控制权并返回原节点
	// 释放时不删除节点内存，也不移除，仅用nullptr替换掉原节点
	data_node_base* release_child(size_t index);

	// 删除自身节点及所有子节点（如果是数据中心的根节点也会删除）并发出通知
	// 本接口内部会先判断如果有无父节点，如果有则先清理本对象，再将其从父节点中移除，清理本对象通
	// 过delete_all_children()接口完成，细节可参考其注释
	// force_remove_items仅当指定的children回收类型为nothing_to_do时有效，如果为true表示仅将要回收的
	// 节点从容器中移除而不析构，否则不析构也不移除
	void delete_data_node_self(bool force_remove_items = false);

	// 删除所有子树，删除节点时并不发出通知，完全删除后触发一次父节点的更新通知，删除过程如下：
	// 1.依次获取要删除的子节点
	// 2.如果当前节点为数据根节点，则直接销毁数据中心(其实这种情况应该是不可能通过界面由用户直接点击节点删除触发的)
	// 3.如果要删除的节点的父节点存在，则直接通过父节点进行删除并返回（没挂接到数据中心也能删除）
	// 4.如果要删除的节点的父节点不存在，则直接销毁其节点（没挂接到数据中心也能删除）
	// 注意：如果当前节点为栈上对象，删除自身会崩溃
	//		如果当前对象或子节点为不自动回收类型，则跳过不调用delete，但如果是子节点仍然会从子节点元素中移除
	//		清理子节点时也会考虑指定children回收类型
	// force_remove_items仅当指定的children回收类型为nothing_to_do时有效，如果为true表示仅将要回收的
	// 节点从容器中移除而不析构，否则不析构也不移除
	void delete_all_children(bool force_remove_items = false);

	// 删除一个子节点及其关联的子节点（如果是数据的根也删除），如果要删除的节点有子节点，则一并删除，删除过程如下：
	// 1.先发出通知告之指定节点即将被删除
	// 2.如果当前节点为数据根节点，则直接销毁数据中心
	// 3.如果要删除的节点的父节点存在，则直接通过父节点进行删除并返回（没挂接到数据中心也能删除）
	// 4.如果要删除的节点的父节点不存在，则直接销毁其节点（没挂接到数据中心也能删除）
	// 如果find_all_children为false表示仅从当前节点的子节点中查找node，找不到则返回，如果为true表示会递归查找
	// 当前节点的整个子树，查到则从找到的节点开始删除子树
	// 注意：从父节点中移除本对象时会受父节点所指定的children回收类型影响，清理子节点时也会考虑指定children回收类型
	// force_remove_items仅当指定的children回收类型为nothing_to_do时有效，如果为true表示仅将要回收的
	// 节点从容器中移除而不析构，否则不析构也不移除
	void delete_child_node(data_node_base* node, bool find_all_children = false, bool force_remove_items = false);
	void delete_child_node(const std::string& tag, bool find_all_children = false, bool force_remove_items = false);
	void delete_child_node(size_t index, bool force_remove_items = false);

	// 根据迭代器移除一个节点，返回它移除前的后一个元素的迭代器，如果没有则返回end()
	// 注意，传入的迭代器必须是子节点的迭代器，移除失败也务必保证返回下一个节点的迭代器
	std::vector<data_node_base*>::iterator delete_child_node(
		std::vector<data_node_base*>::iterator it, bool force_remove_items = false);

	// 删除多个节点,并在结束后触发一次本节点的更新通知
	void delete_children_nodes(std::vector<data_node_base*>::iterator be,
		std::vector<data_node_base*>::iterator en, bool force_remove_items = false);

	// 返回children的相关迭代器，便于外部访问（仅当前节点的直接子节点，不会递归遍历所有子节点）
	std::vector<data_node_base*>::iterator children_begin();
	std::vector<data_node_base*>::iterator children_end();
	std::vector<data_node_base*>::reverse_iterator children_rbegin();
	std::vector<data_node_base*>::reverse_iterator children_rend();
	std::vector<data_node_base*>::const_iterator children_cbegin();
	std::vector<data_node_base*>::const_iterator children_cend();
	std::vector<data_node_base*>::const_reverse_iterator children_crbegin();
	std::vector<data_node_base*>::const_reverse_iterator children_crend();
	// 从当前节点遍历整棵子树
	// find_all_children为true表示递归查找所有子树
	// depth表示递归的深度，-1表示不限定直到全部遍历完，0表示不遍历当前节点的子树，大于0表示最多往下遍历n层(层数不计当前节点层)
	// 指定的节点访问函数如果返回true表示终止遍历，否则按参数的原则继续遍历
	void travel_current_node_tree(std::function<bool(data_node_base*)> access_func, int depth = -1);
	void travel_current_node_tree(std::function<bool(const data_node_base*)> access_func, int depth = -1) const;

	// 实现当前节点及子节点的数据导入，导出功能，主要用于内存数据的转储及辅助调试用，因此内部并未进行异常捕捉，如有
	// 需要请在外部调用此接口时自行使用
	// type为0表示二进制格式，1表示json格式，2表示xml格式
	// path_name内部不会添加文件后缀，请自行添加
	// 成功返回true，否则返回false
	bool import_data(int type, const std::string& full_path_name);
	bool export_data(int type, const std::string& full_path_name);



	// 以json或xml方式导入或导出字符串形式的数据，type为0表示二进制格式，1表示json格式，2表示xml格式，为了与前面的构成合法重载，故意调整参数顺序
	// 当类型为二进制方式时，结果会将二进制内存块按base64编码处理后并返回字符串形式，强烈建议没有特殊原因时，要转
	// 换为二进制的base编码时，如果数据量大，请务必使用std::string形式，而不是本接口，目的是在unicode模式下
	// 可以节省一半的内存，详情参考其接口注释
	bool import_data(const std::string& value, int type);
	bool export_data(std::string& value, int type);

	// 对当前数据节点拍快照，成功返回true，否则返回false（更多的快照操作接口见数据中心类）
	bool take_snapshot(const std::string& name);

private:
	std::string m_node_tag = {}; // 全局唯一的节点标识，不允许修改，连框架也不允许改，只在对象构造时生成
	std::string m_name = {};
	std::vector<data_node_base*> m_children;
	data_node_base* m_parent; // 缓存父节点以提高遍历的速度和灵活性
	std::string m_node_info = {}; // 节点信息，允许用户外部存储任何节点注释、信息等少量信息，内容含义的解释由用户决定
	children_recycling_type m_children_recycling_type; // 子节点的收回方式，注意，回收类型会对当前节点下的所有子节点生效，无论这个子节点是不是直接子节点
	bool m_auto_recycle = false; // 为true则析构或需要删除的本节点时会调用delete，否则不调用，此参数仅对当本节点有用，不作用于子节点


};



// 提供的数组包装类，以便数组能方便的挂接到数据中心
// 要求T类型必须为框架序列化支持的类型或具备void serialize_members(member_rw_interface& mt)接口的自定义类
template<typename T>
class data_node_vector_wrapper : public data_node_base
{
public:
	std::string m_serialize_name; // 序列化对象名

public:
	data_node_vector_wrapper(const std::string& serialize_name = "data_node_vector_wrapper", const std::string& node_name = "",
		bool auto_recycle = true, children_recycling_type children_recycling = children_recycling_type::recyclable)
		: data_node_base(node_name, auto_recycle, children_recycling)
	{
		m_serialize_name = serialize_name;
	}

	virtual ~data_node_vector_wrapper() {}

public:
	virtual void serialize_members(member_rw_interface& mt)
	{
		x_object_flag_serialization_guard tmp_object_flag(m_serialize_name, mt);
		data_node_base::serialize_members(mt);

		int version = 1;

		if (mt.is_storing())
		{
			mt& x_wrapper_macro(version);

			mt& x_wrapper_macro(m_serialize_name);
		}
		else
		{
			mt& x_wrapper_macro(version);

			if (1 == version)
			{
				mt& x_wrapper_macro(m_serialize_name);
			}
		}
	}

public:
	T* get_wrapped_data(size_t index)
	{
		return dynamic_cast<T*>(get_child(index));
	}

	const T* get_wrapped_data(size_t index) const
	{
		return dynamic_cast<const T*>(get_child(index));
	}

	T* get_wrapped_data(const std::string& node_tag, bool find_all_children = false)
	{
		return dynamic_cast<T*>(get_child(node_tag, find_all_children));
	}

	const T* get_wrapped_data(const std::string& node_tag, bool find_all_children = false) const
	{
		return dynamic_cast<const T*>(get_child(node_tag, find_all_children));
	}

public:
	const T* operator[](size_t index) const
	{
		return dynamic_cast<const T*>(get_child(index));
	}

	T* operator[](size_t index)
	{
		return dynamic_cast<T*>(get_child(index));
	}
};


// 自动守护数据通知状态，尽量优先使用此对象来控制通知是否启用，避免手工调用通知接口中的方法
// 类使用raii机制在构造函数中设置状态，析构函数自动恢复
class JOY_UTILITY_API data_node_notify_guard
{
public:
	data_node_notify_guard(bool enable);
	data_node_notify_guard(const data_node_notify_guard&) = delete;
	~data_node_notify_guard();

private:
	bool m_old_enable;
};






_JOY_UTILITY_END_
#endif
