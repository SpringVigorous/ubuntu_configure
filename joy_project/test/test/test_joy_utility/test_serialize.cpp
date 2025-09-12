#include <gtest/gtest.h>
#include <vector>
#include "joy_utility/interface/serialize_interface.h"
#include "joy_utility/interface/data_node_base.h"
#include "joy_utility/kenels/hobject.h"


#include "joy_utility/tools/import_export_tools.h"
#include "joy_utility/tools/string_tools.h"

#include <string>

#include "environment.hxx"
#include <filesystem>

//#ifdef _DEBUG
//#include <crtdbg.h>
//#define _CRTDBG_MAP_ALLOC
//_CrtSetDbgFlag(_CRTDBG_ALLOC_MEM_DF | _CRTDBG_LEAK_CHECK_DF);
//#endif

using namespace JOY_UTILITY;
using namespace std;
class Animal
{
public:
    Animal(const string& name = "", int age = 0) :name_(name), age_(age) {}
public:
    void serialize_members(member_rw_interface& mt)
    {
        //x_object_flag_serialization_guard tmp_object_flag("Animal", mt);

        int version = 1;

        mt & x_wrapper_macro_named(serialize_helper::pack_version("Animal"),version);


        mt & x_wrapper_macro(name_);
        mt & x_wrapper_macro(age_);
    }
private:
    string name_;
    int age_;
};

class Monkey:public Animal
{
public:
    Monkey(const string& name = "", int age = 0, const string& class_name = "") :Animal(name, age), num_(class_name) {}
public:
    void serialize_members(member_rw_interface& mt)
    {

        //x_object_flag_serialization_guard tmp_object_flag("Monkey", mt);


        Animal::serialize_members(mt);

        int version = 1;
        mt & x_wrapper_macro_named(serialize_helper::pack_version("Monkey"),version);


        mt & x_wrapper_macro(num_);


    }
private:
    string num_;
};
class Techer :public Animal
{
public:
    Techer(const string& name = "", int age = 0, const string& class_name = "") :Animal(name, age), num_(class_name) {}
public:
    void serialize_members(member_rw_interface& mt)
    {
        //x_object_flag_serialization_guard tmp_object_flag("Techer", mt);

        Animal::serialize_members(mt);

        int version = 1;
            mt& x_wrapper_macro_named(serialize_helper::pack_version("Techer"),version);


        mt& x_wrapper_macro(num_);

    }
private:
    string num_;
};
class School:public data_node_base
{

    DECLARE_SERIAL(School)


public:
    School(const string& name="") : num_(name)
    {

    }
public:
    void set_shool_name(const string& name)
    {
        num_ = name;
    }
public:
    void serialize_members(member_rw_interface& mt) 
    {
        //x_object_flag_serialization_guard tmp_object_flag("School", mt);

        data_node_base::serialize_members(mt);
        int version = 1;
        mt & x_wrapper_macro_named(serialize_helper::pack_version("School"),version);

        mt& x_wrapper_macro(num_);
        mt& x_wrapper_macro(students_);
        mt& x_wrapper_macro(clerks_);

    }
private:
    template<class T,class... Args>
    void emplace_back(vector<T>& lsts, Args&&...  args)
    {
        lsts.emplace_back(std::forward<Args>(args)...);
    }

public:
    template<class... Args>
    void add_techer(Args&&...  args)
    {
        emplace_back(clerks_, std::forward<Args>(args)...);
    }
    template<class... Args>
    void add_student(Args&&...  args)
    {
        emplace_back(students_, std::forward<Args>(args)...);
    }


private:
    string num_;
    vector<Monkey> students_;
    vector<Techer> clerks_;
};
IMPLEMENT_SERIAL(School,data_node_base)
using FilePath = std::filesystem::path;

School* create_school()
{
    auto jlh = new School("金锣号");
    jlh->set_recycling_type(false);
    jlh->add_student("胡旭尧", 5, "中一班");
    jlh->add_student("李占有", 5, "中一班");
    jlh->add_student("李子柒", 5, "大四班");
    jlh->add_techer("王老师", 25, "中一班");
    jlh->add_techer("赵老师", 30, "中二班");
    return jlh;
}
Animal* create_person()
{
    auto jlh = new Animal("金锣号",10);

    return jlh;
}


void create_data(data_node_base& root)
{

    auto jlh = new School("金锣号");
    jlh->set_recycling_type(false);
    jlh->add_student("胡旭尧", 5, "中一班");
    jlh->add_student("李占有", 5, "中一班");
    jlh->add_student("李子柒", 5, "大四班");
    jlh->add_techer("王老师", 25, "中一班");
    jlh->add_techer("赵老师", 30, "中二班");

    auto xzr = new School;
    //xzr->set_recycling_type(false);
    xzr->copy(*jlh, false);
    xzr->set_shool_name("小主人");
    xzr->add_techer("李子柒", 5, "大四班");



    auto sh = new School;
    sh->set_recycling_type(false);
    sh->copy(*jlh, false);
    sh->set_shool_name("申花");
    sh->add_techer("李子柒", 5, "大四班");

    xzr->add_child_node(sh);

    root.add_child_node(jlh);
    root.add_child_node(xzr);
    root.add_child_node(nullptr);
}

void test_json(data_node_base& data,const FilePath& org_path)
{
    //auto dest_path = file;
    //dest_path.replace_extension(".xml");
    
    auto json_file_path = org_path.generic_string();

    bool success = export_to_json_file(data, json_file_path);
    EXPECT_EQ(true, success);

    data_node_base temp;
    success = import_from_json_file(json_file_path, temp);

    EXPECT_EQ(true, success);
}

template<class T>
void test_xml(T& data, const FilePath& org_path)
{
    auto dest_path = org_path;
    dest_path.replace_extension(".xml");

    auto xml_file_path = dest_path.generic_string();
    bool success = false;

    success = export_to_xml_file(data, xml_file_path);
    EXPECT_EQ(true, success);

    T temp;
    success = import_from_xml_file(xml_file_path, temp);

    EXPECT_EQ(true, success);
}



TEST(joy_utility,test_cereal ) {

    data_node_base root("根节点");
    create_data(root);


    auto org_path = environment::GlobalEnvironment::GetTestDataPath() / "joy_utility" / "test_serialize.json";


    test_json(root, org_path);

    auto* jlh = create_person();

    test_xml(root, org_path);
    //test_xml(*jlh, org_path);

    delete jlh;

}