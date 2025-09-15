
#pragma once
#ifndef __DATA_ANIMAL_H__
#define __DATA_ANIMAL_H__
#include <string>
#include "utilities/cereal_macro.h"
#include "data/data_macro.h"


_DATA_BEGIN_


class DATA_API Animal {

public:
    Animal() = default;
    Animal(int _age):age(_age){}
    virtual ~Animal() = default;
    virtual void speak() const;
protected:
    int age = 0;
private:
    CEREAL_SERIALIZE_MEMBER_DECLEAR();
};


class DATA_API Dog : public Animal {
public:
    Dog() = default;
    Dog(int _age,const std::string& _breed) :Animal(_age),breed(_breed) {}
    ~Dog() = default;
    void speak() const override;
protected:
    std::string breed;
private:
    CEREAL_SERIALIZE_MEMBER_DECLEAR();
};


class DATA_API Cat : public Animal {
public:
    Cat() = default;
    Cat(int _age, bool _hasLongHair) :Animal(_age), hasLongHair(_hasLongHair) {}
    ~Cat() = default;



    void speak() const override;
protected:
    bool hasLongHair;
private:
    CEREAL_SERIALIZE_MEMBER_DECLEAR();
};




_DATA_END_

#endif
