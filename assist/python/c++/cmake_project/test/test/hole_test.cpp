#include <gtest/gtest.h>
#include <filesystem>
#include <fstream>
#include <ds_common/tools/file_tools.h>
#include <ai-tools/manager/recognition_proxy_manager.h>
#include <ds_proto/model/geometry.pb.h>
#include <framework/serialize/message_converter.h>
#include <component_recognition/recognition/recognition.h>
#include <component_recognition/recognition/hole_recognition.h>
#include <data_convert/convert/entity_container_convert.h>
#include <aicad/data/data.h>

#include <data_convert/tools/convert_tools.h>

TEST(hole_symbol_tets, hole_symbol_tets) {

    const auto& path = R"(E:\save_data\ZG5HX-S-04-CZ28-02JG-02-16 地下二层结构平面布置图（二）\entities.json)";
    std::string str;
    common::tools::FileTools::ReadFile(path, str);
    geo::EntityContainer pb_entities;
    framework::serialize::MessageConverter convert;
    convert.Deserialize(str, pb_entities);
    using dctc = data::convert::tools::ConvertTools;

    AICAD::VecLayoutPtr layouts;
    dctc::DoDeConvert<data::convert::EntityContainerConvert>(pb_entities, layouts);
    const auto& data = layouts.front()->GetData();
    data->InitData(AICAD::Data::ExplodeParameter(true, false,false));
    auto block = std::make_shared<AICAD::Block>();
    block->SetBlockType(AICAD::BlockType::FS);
    auto blockdata = std::make_shared<AICAD::BlockData>(block, data);

    COMP_IDENT::HoleRecognition hole("0011.0007.0004.0000");
    hole.SetBlockDatas({blockdata});

    COMP_IDENT::RecognitionInteractPtr input_interact_data = nullptr;
    hole.ParserLocation(input_interact_data);
}