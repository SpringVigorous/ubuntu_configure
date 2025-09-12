#pragma once
#ifndef __DATA_STUDENT_H__
#define __DATA_STUDENT_H__
#include <string>

//#include <cereal/access.hpp>
#include <cereal/cereal.hpp>
#include <cereal/types/polymorphic.hpp>
#include "data/data_macro.h"
#include "common_header/cereal_macro.h"


CEREAL_SERIALIZE_PRE_DECLEAR_(DATA,Person)
CEREAL_SERIALIZE_PRE_DECLEAR_(DATA,Student)

_DATA_BEGIN_
using namespace std;
class DATA_API Person
{
public:
    Person() = default;
    Person(const string& name, int age) :name_(name), age_(age) {}
    virtual ~Person() = default;
public:

    virtual void print() const;

protected:
    string name_{};
    int age_{};
private:
    CEREAL_SERIALIZE_DECLEAR(Person);
};



class DATA_API Student :public Person {
public:
    Student() = default;
    // 新增构造函数参数
    Student(const std::string& _name, int _age, int _score = 0.0)
        : Person(_name, _age), score_(_score) {}

    void print() const override;

protected:
    int score_{ };  // 新增成员
private:
    CEREAL_SERIALIZE_DECLEAR(Student);
};


_DATA_END_



#endif
