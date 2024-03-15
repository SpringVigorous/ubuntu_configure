import argparse

# 创建ArgumentParser对象，其中description参数用于提供程序的简短描述
parser = argparse.ArgumentParser(description='这是一个使用argparse模块处理命令行参数的例子')

# 添加一个位置参数（positional argument），这里假设我们需要用户提供一个文件名
parser.add_argument('input_file', type=str, help='输入文件的路径')

# 添加一个可选参数（optional argument）--output或-o，后面跟随一个值，表示输出文件的路径
parser.add_argument('-o', '--output', type=str, default='output.txt', help='输出文件的路径，默认为output.txt')

# 添加一个布尔标志（boolean flag）--verbose或-v，无须指定值，存在即为True
parser.add_argument('-v', '--verbose', action='store_true', help='开启详细模式')

# 解析命令行参数并存储到args变量中
args = parser.parse_args()

# 使用解析后的参数执行相应的操作
if args.verbose:
    print("详细模式已启用")
    
try:
    with open(args.input_file, 'r',encoding='utf-8-sig') as input_f:
        content = input_f.read()
        
    with open(args.output, 'w') as output_f:
        output_f.write(content)
        
except FileNotFoundError as e:
    print(f"无法打开文件: {e.filename}")
    
print(f"成功读取输入文件：{args.input_file} 并将内容写入了输出文件：{args.output}")

# 如何运行该脚本

# 假设你将上述代码保存在名为 args_example.py 的文件中，你可以通过以下方式在命令行中调用它：

# sh
# python args_example.py input.txt -o result.txt
# 或者

# sh
# python args_example.py -v input.txt
# 在第一个示例中，我们指定了输入文件为 input.txt，输出文件为 result.txt。
# 在第二个示例中，我们启用了详细模式 -v，并且指定了输入文件为 input.txt，由于没有显式指定输出文件，所以会默认使用 output.txt。
# 注意：当你在命令行下运行带有 argparse 的 Python 脚本时，可以通过 python script_name.py -h 或 python script_name.py --help 来查看帮助信息，其中包含了所有可用的选项及其说明。