
#pragma once
#ifndef __DATA_PLANT_H__
#define __DATA_PLANT_H__

#include <string>

//#define CEREAL_SERIALIZE_HELPER
#include "utilities/cereal_macro.h"
#include "data/data_macro.h"


CEREAL_SERIALIZE_FRIEND_PRE_DECLEAR_(DATA, Plant)
CEREAL_SERIALIZE_FRIEND_PRE_DECLEAR_(DATA, Flower)
CEREAL_SERIALIZE_FRIEND_PRE_DECLEAR_(DATA, Tree)


_DATA_BEGIN_



class DATA_API Plant {

public:
    Plant() = default;
    Plant(int _age):age(_age){}
    virtual ~Plant() = default;
    virtual void grow() const;
protected:
    int age = 0;
private:
    //CEREAL_SERIALIZE_FRIEND_CLASS_DECLEAR();
    CEREAL_SERIALIZE_FRIEND_DECLEAR(Plant);
};


class DATA_API Flower : public Plant {
public:
    Flower() = default;
    Flower(int _age,const std::string& _breed) :Plant(_age),breed(_breed) {}
    ~Flower() = default;

    void grow() const override;
protected:
    std::string breed;
private:
    //CEREAL_SERIALIZE_FRIEND_CLASS_DECLEAR();
    CEREAL_SERIALIZE_FRIEND_DECLEAR(Flower);
};


class DATA_API Tree : public Plant {
public:
    Tree() = default;
    Tree(int _age, bool _hasLongHair) :Plant(_age), hasLongHair(_hasLongHair) {}


    ~Tree() = default;

    void grow() const override;
protected:
    bool hasLongHair;
private:
    //CEREAL_SERIALIZE_FRIEND_CLASS_DECLEAR();
    CEREAL_SERIALIZE_FRIEND_DECLEAR(Tree);
};

_DATA_END_

#endif



