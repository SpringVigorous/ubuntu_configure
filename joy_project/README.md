# joy_project

python工具集

1. PowerShell中运行
cd  F:/test/ubuntu_configure/assist/python
2.  激活环境：
myenv/Scripts/activate

运行
1.生成项目文件
python c++/create_c_project.py-r F:/test  -p joy_project -m joy_utility -f interface.serialize_interface,interface.member_rw_interface,interface.bin_archive,interface.json_archive,interface.xml_archive
python c++/create_c_project.py -r F:/test  -p joy_project -m joy_utility -f tools.string_tools,tools.xml_tools,tools.json_tools
python c++/create_c_project.py -r F:/test  -p joy_project -m joy_utility -f tools.template_utility

2.更改编码（文件夹或者文件）

python integer/alter_encoding.py -i F:/test/cmake_project/src -c utf-8-sig -f '.hpp;.cpp;.h;.cxx;.hxx;.c;.cc;.hh;.inl' --clear 
python integer/alter_encoding.py -i F:/test/joy_project/src/joy_utility -c utf-8-sig -f '.hpp;.cpp;.h;.cxx;.hxx;.c;.cc;.hh;.inl' --clear 

3.文件内容替换
python.exe integer/replace_folders_files.py -o F:/TH/th/x_framework_clone -d F:/TH/th  -r F:/test/ubuntu_configure/assist/python/c++/fold_replace_args.json



vcpkg 安装、导出
第一次时，需要导出下，后续可以直接安装到指定目录
vcpkg export jsoncpp:x64-windows --output=vcpkg --output-dir="F:/test/joy_project/3rd" --raw
直接安装到指定目录
vcpkg install jsoncpp:x64-windows --x-install-root="F:/test/joy_project/3rd/vcpkg/installed"


vcpkg install boost-locale:x64-windows --x-install-root="F:/test/joy_project/3rd/vcpkg/installed"
vcpkg install libiconv:x64-windows --x-install-root="F:/test/joy_project/3rd/vcpkg/installed"
vcpkg install cpp-base64:x64-windows --x-install-root="F:/test/joy_project/3rd/vcpkg/installed
vcpkg install tinyxml2:x64-windows --x-install-root="F:/test/joy_project/3rd/vcpkg/installed
vcpkg install gtest:x64-windows --x-install-root="F:/test/joy_project/3rd/vcpkg/installed"
vcpkg install magic-enum:x64-windows --x-install-root="F:/test/joy_project/3rd/vcpkg/installed"
vcpkg install boost-uuid:x64-windows --x-install-root="F:/test/joy_project/3rd/vcpkg/installed"

升级某个包
vcpkg upgrade tinyxml2:x64-windows --x-install-root="F:/test/joy_project/3rd/vcpkg/installed" --no-dry-run
vcpkg upgrade jsoncpp:x64-windows --x-install-root="F:/test/joy_project/3rd/vcpkg/installed" --no-dry-run

导出已安装的包
vcpkg list > installed_packages.txt cd
json格式
vcpkg list --x-json > installed_packages.json

通过python依据 上述导出的installed_packages.txt 安装包
python install_vcpkg.py