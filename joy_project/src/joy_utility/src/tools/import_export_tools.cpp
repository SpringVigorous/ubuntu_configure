
#include "joy_utility/tools/import_export_tools.h"

//#ifdef _DEBUG
//#define new DEBUG_NEW
//#endif
_JOY_UTILITY_BEGIN_

void test_export_xml(tinyxml2::XMLElement* root)
{
    auto doc = root->GetDocument();
    if (!doc)
        return;
    using namespace std;
    string flag{ "hello" };

    auto* node = doc->NewElement(flag.c_str());
    root->LinkEndChild(node);



    auto* sub_node = doc->NewElement("kitty");
    node->LinkEndChild(sub_node);
    sub_node->SetText("Sam");

    sub_node = doc->NewElement("Spring");
    node->LinkEndChild(sub_node);

    string sum_flag{ "Sum" };
    auto* ss_node = doc->NewElement(sum_flag.c_str());
    sub_node->LinkEndChild(ss_node);


    string auto_flag{ "Auto" };
    ss_node->SetText(auto_flag.c_str());


}









_JOY_UTILITY_END_