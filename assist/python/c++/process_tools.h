//////////////////////////////////////////////////////////////////////////
// 网络上充斥着大量进程调用的代码，基本上能看到源码的都不具备商业强度的要求（仅限于教程
// 类的网页，可能有些开源的库能很优秀的做到，不过限于时间和见识暂未了解到，加之这样的库
// 就算有，估计代码量也不会少），因此，自己实现一个轻量的进程调用的库，并能通过匿名管道
// 的方式将标准输出的信息导入到框架进程中，并转到框架的输出接口进行输出，与本框架整合度
// 高，易用性好。 by WYZ
//////////////////////////////////////////////////////////////////////////

#pragma once

#include <windows.h>
#include <atlstr.h>
#include <functional>
#include <map>
#include <thread>
#include <mutex>

class  x_process_object
{
public:
	// 默认构造的是同步调用的进程（阻塞式），由于路径参数为空，因此不具备运行通用，仅出于使用便利性才给默认参数
	x_process_object(const CString& app_path_name = _T(""), const CString& param = _T(""));
	~x_process_object();

public:
	// 可执行文件的路径和名称（可以是exe,com,bat等可执行文件类型）
	CString		m_program_path_name;
	
	// 启动参数（注意:Windows的启动参数有上限，印象中是64K，请注意参数不要过长，尽量控制在300-500字节以内，通
	// 常100个字节内算比较正常，如果要传大量参数，则不适合使用此方式，可以考虑RPC或生成文件，并传文件路径等其它方式）
	// 如果某个参数中间有空格字符，则参数应该显式的在外层加上英文的引号作为参数的一部分，否则操作系统会认为是使用空
	// 格分隔的多个参数，如将一个带空格的路径作为参数时：
	// "C:\\abc def\\x.txt"
	// 应该传字符串（最外层引号不是内容，只是表示字符串的形式，）
	// "\"C:\\abc def\\x.txt\""
	// 带引号为内容的参数，系统会将其当成一个参数传送给子进行，且会自动去掉引号，不用进行特殊处理，同理，如果需要传
	// 多个参数时可使用空格分隔并合成一个字符串
	CString		m_parameter;

	// 是否等待操作完成
	bool		m_wait_for_termination;

	// 为true表示同步的状态下也不阻塞界面，否则总是阻塞，异步的情况下此参数无效
	bool		m_need_response_ui_when_waitting = true;

	// time_out仅当wait_for_termination为true时有效，为0表示不等待，为INFINITE表示一直等待直到进程结束
	std::size_t m_time_out = 0;

	// 异步调用时有效，当异步任务结束时会调用此回调函数，同步调用时不用赋值，参数为<任务名称,为退出码>
	// 异步时会切换到界面线程再调用本回调函数
	std::function<void(CString, DWORD)> m_end_call_back;
};

// 向框架添加任务对象(不对外提供已添加任务对象的任何操作，只能由框架统一管理)，任务名称仅用于全局唯一标识任务对象使用
// 如果任务是要求等待完成才返回，则正常结束返回0，否则返回相关的非0的退出码，使用任务管理器强制结束时返回非0值
// 如果任务是不要求等待，异步完成的，则会在完成时调用相应的回调函数，此接口直接返回0
// 任务对象的参数不要使用引用传递，否则异步时会因为生命周期的原因强制要求外部传入的对象不能用局部对象，这一点体验不好
// 启动后的子进程可以正常使用框架的文字输出接口，内部以管道方式传给主进程
// 由于任务允许异步调用，因此异常捕获没有意义，内部不作异常处理
// 注意：本工具不支持同时有多个相同exe的进程实例在并行执行，原因是内部使用管道进行输出回传，并设置一些子进程的配置参数
//      启动的实例名称如果已经存在，会造成管道打开失败等问题，这个问题目前暂时没有需求，因此暂不支持，如果有此类需求，
//      可考虑使用ShellExcute或CreateProcess等API手工处理
 DWORD do_process_task(const CString& task_name, const x_process_object obj); // 在新进程中执行任务
 bool has_process_task(const CString& task_name); // 当前是否有指定名称的任务
 bool has_any_task(); // 当前是否有任何在执行的任务
 void force_stop_all_tasks(int exit_code = 2); // 强行结束所有任务
 void force_stop_task(const CString& task_name, int exit_code = 2); // 强行结束指定任务


// 以非监管的方式打开指定文档（内部使用ShellExecuteEx实现，自动查找文件的关联应用程序并打开，如果没有关联应用程序，则系统自动弹出选择打开方式对话框）
// doc_full_path_name文档全路径，包含后缀名
// exe_full_path_name为指定打开这个文档所用的程序路径（包含后缀），为空字符串表示自动使用系统关联的程序打开
// need_max_size为true表示打开的程序默认最大化显示，否则由程序自由决定，以常规状态显示（大多数程序均会记住上一次用户操作后的尺寸及位置）
// need_wait为true表示强制等待打开的程序结束（或异常终止）后本函数才返回，否则启动进程后即返回
// 如果need_wait为true，则返回进程的退出码（0表示进程正常结束，详情参数微软MSDN），为false则返回值没有意义，总是返回0，无法正常启动进程返回1
 DWORD x_open_file_by_shell_execute(const CString& doc_full_path_name, const CString& exe_full_path_name = _T(""), bool need_max_size = false, bool need_wait = false);

// 以非监管的方式直接启动一个进程（内部使用ShellExecuteEx实现，比do_process_task开销小，没有管道进行进程间通信）
// exe_full_path_name为exe的文件全路径名（包含后缀）
// need_wait为true表示强制等待打开的程序结束（或异常终止）后本函数才返回，否则启动进程后即返回
// 如果need_wait为true，则返回进程的退出码（0表示进程正常结束，详情参数微软MSDN），为false则返回值没有意义，总是返回0，无法正常启动进程返回1
 DWORD x_shell_lite_process(const CString& exe_full_path_name, const CString& parameter, bool need_wait = true);


//////////////////////////////////////////////////////////////////////////


// 当本模块作为子进程被启动时，阻塞式等待主进程结束（只要主进程不存在则返回，哪怕崩溃或强制结束也一样），本功能的
// 使用需要了解一定知识，使用时可咨询WYZ
// 调本接口时务必确保执行的代码所在进程为子进程，否则无法正常判断
// 由于本接口是阻塞式的，因此，子进程需要在线程中调用，否则会阻塞主线程
// 返回0表示主进程结束了才返回的，返回1表示外部设置停止等待的标志才返回的，2表示异常情况才返回的
 int x_sub_process_wait_for_host_exit();

// 设置退出标志，以便子进程在等待主进程结束的过程中提前取消等待
// 调本接口时务必确保执行的代码所在进程为子进程，否则无法正常判断
// 本接口为非阻塞式的，外部调用本接口之后，需要等待sub_process_wait_for_host_exit的正常结束才可退出程
// 序，否则会导致等待对象崩溃
 void x_stop_sub_process_waitting();




