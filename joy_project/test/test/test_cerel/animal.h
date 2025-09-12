#include <gtest/gtest.h>
#include <fstream>
#include <cereal/cereal.hpp>
#include "environment.hxx"
#include <cereal/types/memory.hpp>
#include <cereal/types/polymorphic.hpp>
#include <memory>
#include "common_header/cereal_macro.h"

CEREAL_SERIALIZE_PRE_DECLEAR(Animal)
CEREAL_SERIALIZE_PRE_DECLEAR(Dog)
CEREAL_SERIALIZE_PRE_DECLEAR(Cat)

// 基类定义（无序列化代码）
class Animal {

public:
    Animal() = default;
    Animal(int _age):age(_age){}
    virtual ~Animal() = default;
    virtual void speak() const = 0;
protected:
    int age = 0;
private:
    CEREAL_SERIALIZE_DECLEAR(Animal);
};

// 派生类1（无序列化代码）
class Dog : public Animal {
public:
    Dog() = default;
    Dog(int _age,const std::string& _breed) :Animal(_age),breed(_breed) {}

    void speak() const override {
        std::cout << "Woof! Age:" << age << " Breed:" << breed << "\n";
    }
protected:
    std::string breed;
private:
    CEREAL_SERIALIZE_DECLEAR(Dog);
};

// 派生类2（无序列化代码）
class Cat : public Animal {
public:
    Cat() = default;
    Cat(int _age, bool _hasLongHair) :Animal(_age), hasLongHair(_hasLongHair) {}



    void speak() const override {
        std::cout << "Meow! Age:" << age << " LongHair:" << hasLongHair << "\n";
    }
protected:
    bool hasLongHair;
private:
    CEREAL_SERIALIZE_DECLEAR(Cat);
};





