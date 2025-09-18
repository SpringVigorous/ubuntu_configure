

#include "environment.hxx"



#include "handle_data/serialize/student_cereal.h"

#include "utilities/cereal_utility.h"
#include "environment.hxx"
#include <filesystem>

template<class T>
T cereal_triple(const T& data, const std::string& file_name)
{
    using filesystem_path = std::filesystem::path;

    filesystem_path json_path = environment::GlobalEnvironment::GetTestDataPath() / "joy_utility" / (file_name + ".json");
    auto xml_path = json_path.replace_extension(filesystem_path(".xml"));
    auto bin_path = json_path.replace_extension(filesystem_path(".bin"));

    UTILITIES::save_data_to_json(data, json_path);
    UTILITIES::save_data_to_xml(data, xml_path);
    UTILITIES::save_data_to_binary(data, bin_path);

    T load_data;
    UTILITIES::load_data_from_json(load_data, json_path);

    UTILITIES::load_data_from_xml(load_data, xml_path);

    UTILITIES::load_data_from_binary(load_data, bin_path);

    return load_data;

}