#include "x_process.h"
#include <iostream>
#include "process_tools.h"

// 全局变量，用于管理任务
std::map<CString, HANDLE> g_task_map;
std::mutex g_task_mutex;
bool g_stop_waiting = false;

x_process_object::x_process_object(const CString& app_path_name, const CString& param)
    : m_program_path_name(app_path_name), m_parameter(param), m_wait_for_termination(true)
{
}

x_process_object::~x_process_object()
{
}

DWORD do_process_task(const CString& task_name, const x_process_object obj)
{
    SECURITY_ATTRIBUTES saAttr;
    saAttr.nLength = sizeof(SECURITY_ATTRIBUTES);
    saAttr.bInheritHandle = TRUE;
    saAttr.lpSecurityDescriptor = NULL;

    HANDLE g_hChildStd_OUT_Rd = NULL;
    HANDLE g_hChildStd_OUT_Wr = NULL;

    if (!CreatePipe(&g_hChildStd_OUT_Rd, &g_hChildStd_OUT_Wr, &saAttr, 0))
    {
        return 1; // 创建管道失败
    }

    if (!SetHandleInformation(g_hChildStd_OUT_Rd, HANDLE_FLAG_INHERIT, 0))
    {
        CloseHandle(g_hChildStd_OUT_Rd);
        CloseHandle(g_hChildStd_OUT_Wr);
        return 1; // 设置管道属性失败
    }

    PROCESS_INFORMATION piProcInfo;
    STARTUPINFO siStartInfo;
    ZeroMemory(&piProcInfo, sizeof(PROCESS_INFORMATION));
    ZeroMemory(&siStartInfo, sizeof(STARTUPINFO));
    siStartInfo.cb = sizeof(STARTUPINFO);
    siStartInfo.hStdError = g_hChildStd_OUT_Wr;
    siStartInfo.hStdOutput = g_hChildStd_OUT_Wr;
    siStartInfo.hStdInput = NULL;
    siStartInfo.dwFlags |= STARTF_USESTDHANDLES;

    CString commandLine = obj.m_program_path_name + _T(" ") + obj.m_parameter;
    if (!CreateProcess(NULL, commandLine.GetBuffer(), NULL, NULL, TRUE, 0, NULL, NULL, &siStartInfo, &piProcInfo))
    {
        CloseHandle(g_hChildStd_OUT_Rd);
        CloseHandle(g_hChildStd_OUT_Wr);
        return 1; // 创建进程失败
    }

    commandLine.ReleaseBuffer();

    CloseHandle(g_hChildStd_OUT_Wr);

    if (obj.m_wait_for_termination)
    {
        DWORD result = WaitForSingleObject(piProcInfo.hProcess, obj.m_time_out);
        if (result == WAIT_OBJECT_0)
        {
            DWORD exitCode;
            if (GetExitCodeProcess(piProcInfo.hProcess, &exitCode))
            {
                if (obj.m_end_call_back)
                {
                    std::thread([task_name, exitCode, callback = obj.m_end_call_back]() {
                        callback(task_name, exitCode);
                    }).detach();
                }
                return 0; // 正常结束
            }
        }
        else if (result == WAIT_TIMEOUT)
        {
            return 1; // 超时
        }
    }

    if (obj.m_end_call_back)
    {
        std::thread([task_name, handle = piProcInfo.hProcess, callback = obj.m_end_call_back]() {
            DWORD exitCode;
            WaitForSingleObject(handle, INFINITE);
            GetExitCodeProcess(handle, &exitCode);
            callback(task_name, exitCode);
            CloseHandle(handle);
        }).detach();
    }

    g_task_mutex.lock();
    g_task_map[task_name] = piProcInfo.hProcess;
    g_task_mutex.unlock();

    CloseHandle(piProcInfo.hThread);

    return 0;
}

bool has_process_task(const CString& task_name)
{
    g_task_mutex.lock();
    bool result = g_task_map.find(task_name) != g_task_map.end();
    g_task_mutex.unlock();
    return result;
}

bool has_any_task()
{
    g_task_mutex.lock();
    bool result = !g_task_map.empty();
    g_task_mutex.unlock();
    return result;
}

void force_stop_all_tasks(int exit_code)
{
    g_task_mutex.lock();
    for (auto& pair : g_task_map)
    {
        TerminateProcess(pair.second, exit_code);
        CloseHandle(pair.second);
    }
    g_task_map.clear();
    g_task_mutex.unlock();
}

void force_stop_task(const CString& task_name, int exit_code)
{
    g_task_mutex.lock();
    auto it = g_task_map.find(task_name);
    if (it != g_task_map.end())
    {
        TerminateProcess(it->second, exit_code);
        CloseHandle(it->second);
        g_task_map.erase(it);
    }
    g_task_mutex.unlock();
}

DWORD x_open_file_by_shell_execute(const CString& doc_full_path_name, const CString& exe_full_path_name, bool need_max_size, bool need_wait)
{
    SHELLEXECUTEINFO shex;
    ZeroMemory(&shex, sizeof(shex));
    shex.cbSize = sizeof(SHELLEXECUTEINFO);
    shex.fMask = SEE_MASK_NOCLOSEPROCESS;
    shex.hwnd = NULL;
    shex.lpVerb = need_wait ? _T("open") : _T("open");
    shex.lpFile = doc_full_path_name;
    shex.lpParameters = exe_full_path_name.IsEmpty() ? NULL : exe_full_path_name;
    shex.lpDirectory = NULL;
    shex.nShow = need_max_size ? SW_SHOWMAXIMIZED : SW_SHOWNORMAL;
    shex.hInstApp = NULL;

    if (!ShellExecuteEx(&shex))
    {
        return 1; // 启动失败
    }

    if (need_wait)
    {
        WaitForSingleObject(shex.hProcess, INFINITE);
        DWORD exitCode;
        if (GetExitCodeProcess(shex.hProcess, &exitCode))
        {
            CloseHandle(shex.hProcess);
            return exitCode;
        }
    }

    return 0;
}

DWORD x_shell_lite_process(const CString& exe_full_path_name, const CString& parameter, bool need_wait)
{
    SHELLEXECUTEINFO shex;
    ZeroMemory(&shex, sizeof(shex));
    shex.cbSize = sizeof(SHELLEXECUTEINFO);
    shex.fMask = SEE_MASK_NOCLOSEPROCESS;
    shex.hwnd = NULL;
    shex.lpVerb = _T("open");
    shex.lpFile = exe_full_path_name;
    shex.lpParameters = parameter;
    shex.lpDirectory = NULL;
    shex.nShow = SW_SHOWNORMAL;
    shex.hInstApp = NULL;

    if (!ShellExecuteEx(&shex))
    {
        return 1; // 启动失败
    }

    if (need_wait)
    {
        WaitForSingleObject(shex.hProcess, INFINITE);
        DWORD exitCode;
        if (GetExitCodeProcess(shex.hProcess, &exitCode))
        {
            CloseHandle(shex.hProcess);
            return exitCode;
        }
    }

    return 0;
}

int x_sub_process_wait_for_host_exit()
{
    HANDLE hParent = OpenProcess(SYNCHRONIZE, FALSE, ::GetParentProcessId());
    if (hParent == NULL)
    {
        return 2; // 异常情况
    }

    while (WaitForSingleObject(hParent, INFINITE) == WAIT_OBJECT_0)
    {
        if (g_stop_waiting)
        {
            CloseHandle(hParent);
            return 1; // 外部设置停止等待
        }
    }

    CloseHandle(hParent);
    return 0; // 主进程结束
}

void x_stop_sub_process_waitting()
{
    g_stop_waiting = true;
}

// 辅助函数，获取父进程ID
DWORD GetParentProcessId()
{
    DWORD dwParentPID = 0;
    HANDLE hSnapShot = CreateToolhelp32Snapshot(TH32CS_SNAPALL, 0);
    PROCESSENTRY32 pe = { 0 };
    pe.dwSize = sizeof(PROCESSENTRY32);

    if (Process32First(hSnapShot, &pe))
    {
        DWORD dwCurrentPID = GetCurrentProcessId();
        while (Process32Next(hSnapShot, &pe))
        {
            if (pe.th32ProcessID == dwCurrentPID)
            {
                dwParentPID = pe.th32ParentProcessID;
                break;
            }
        }
    }

    CloseHandle(hSnapShot);
    return dwParentPID;
}