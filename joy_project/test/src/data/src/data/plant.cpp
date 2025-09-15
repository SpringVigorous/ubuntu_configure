
#include "data/plant.h"

//#ifdef _DEBUG
//#define new DEBUG_NEW
//#endif
_DATA_BEGIN_

void Plant::grow() const {};



void Flower::grow() const {
    std::cout << "Woof! Age:" << age << " Breed:" << breed << "\n";
}


void Tree::grow() const  {
    std::cout << "Meow! Age:" << age << " LongHair:" << hasLongHair << "\n";
}




_DATA_END_