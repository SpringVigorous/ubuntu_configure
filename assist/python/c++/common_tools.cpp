#include "common_tools.h"
#include <windows.h>  // 包含Windows API相关的定义和声明
#include <afxwin.h>   // 包含MFC核心类的定义
#include <tlhelp32.h>
#include <iostream>
#include <array>
#include <string>
#include <sstream>
#include <ctime>
#include <algorithm>
#include <afxwin.h>  // 包含 MFC 相关的定义和声明


#include <functional> // 包含 std::function


// 在MFC界面主进程中的非界面耗时代码中合理间隔内调用此函数可以避免界面被阻塞
// 此函数只能在主界面进程中调用，不能在其它界面进程或其它线程中使用，否则会有跨线程问题
void x_do_ui_events() {
    // 处理消息队列，防止界面阻塞
    MSG msg;
    while (PeekMessage(&msg, NULL, 0, 0, PM_REMOVE)) {
        if (msg.message == WM_QUIT) {
            PostQuitMessage(msg.wParam);
            return;
        }
        TranslateMessage(&msg);  // 将虚拟键消息转换为字符消息
        DispatchMessage(&msg);   // 将消息发送到相应的窗口过程进行处理
    }
}


// 定义返回值常量
const int RESULT_HOST_EXITED = 0;
const int RESULT_STOP_FLAG_SET = 1;
const int RESULT_EXCEPTION = 2;

// 全局变量，用于设置停止等待的标志
volatile bool stop_flag = false;

// 设置停止等待的标志
void set_stop_flag() {
    stop_flag = true;
}

// 获取主进程的PID
DWORD get_host_process_id() {
    DWORD host_pid = 0;
    HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hSnapshot != INVALID_HANDLE_VALUE) {
        PROCESSENTRY32 pe;
        pe.dwSize = sizeof(PROCESSENTRY32);
        if (Process32First(hSnapshot, &pe)) {
            do {
                if (pe.th32ProcessID == GetCurrentProcessId()) {
                    // 找到当前进程的父进程ID
                    host_pid = pe.th32ParentProcessID;
                    break;
                }
            } while (Process32Next(hSnapshot, &pe));
        }
        CloseHandle(hSnapshot);
    }
    return host_pid;
}

// 阻塞式等待主进程结束
int sub_process_wait_for_host_exit() {
    DWORD host_pid = get_host_process_id();
    if (host_pid == 0) {
        std::cerr << "无法找到主进程" << std::endl;
        return RESULT_EXCEPTION;
    }

    HANDLE hHostProcess = OpenProcess(SYNCHRONIZE, FALSE, host_pid);
    if (hHostProcess == NULL) {
        std::cerr << "无法打开主进程" << std::endl;
        return RESULT_EXCEPTION;
    }

    try {
        while (!stop_flag) {
            DWORD waitResult = WaitForSingleObject(hHostProcess, 1000); // 等待1秒
            if (waitResult == WAIT_OBJECT_0) {
                // 主进程已结束
                CloseHandle(hHostProcess);
                return RESULT_HOST_EXITED;
            } else if (waitResult == WAIT_FAILED) {
                std::cerr << "WaitForSingleObject 失败" << std::endl;
                CloseHandle(hHostProcess);
                return RESULT_EXCEPTION;
            }
        }
        // 停止等待标志被设置
        CloseHandle(hHostProcess);
        return RESULT_STOP_FLAG_SET;
    } catch (...) {
        std::cerr << "发生异常" << std::endl;
        CloseHandle(hHostProcess);
        return RESULT_EXCEPTION;
    }
}

// 解析编译时的日期字符串
std::array<int, 3> parse_date(const std::string& date_str) {
    std::array<int, 3> date = {0, 0, 0};
    std::istringstream iss(date_str);
    std::string month_str;
    int day, year;
    char space;

    iss >> month_str >> space >> day >> year;

    // 将月份字符串转换为数字
    static const std::map<std::string, int> month_map = {
        {"Jan", 1}, {"Feb", 2}, {"Mar", 3}, {"Apr", 4},
        {"May", 5}, {"Jun", 6}, {"Jul", 7}, {"Aug", 8},
        {"Sep", 9}, {"Oct", 10}, {"Nov", 11}, {"Dec", 12}
    };

    auto it = month_map.find(month_str);
    if (it != month_map.end()) {
        date[0] = it->second;
    }
    date[1] = day;
    date[2] = year;

    return date;
}

// 解析编译时的时间字符串
std::array<int, 3> parse_time(const std::string& time_str) {
    std::array<int, 3> time = {0, 0, 0};
    std::istringstream iss(time_str);
    int hour, minute, second;
    char colon;

    iss >> hour >> colon >> minute >> colon >> second;

    time[0] = hour;
    time[1] = minute;
    time[2] = second;

    return time;
}

// 返回当前模块编译时的日期和时间
std::array<int, 6> get_framework_compiling_data() {
    std::array<int, 6> compiling_data = {0, 0, 0, 0, 0, 0};

    // 获取编译时的日期和时间字符串
    std::string date_str = __DATE__;
    std::string time_str = __TIME__;

    // 解析日期和时间
    auto date = parse_date(date_str);
    auto time = parse_time(time_str);

    // 填充结果数组
    compiling_data[0] = date[0];  // 月
    compiling_data[1] = date[1];  // 日
    compiling_data[2] = date[2];  // 年
    compiling_data[3] = time[0];  // 时
    compiling_data[4] = time[1];  // 分
    compiling_data[5] = time[2];  // 秒

    return compiling_data;
}



// 递归检查 child 是否是 parent 的子窗口
bool is_any_child_window(HWND parent, HWND child) {
    if (child == nullptr || parent == nullptr) {
        return false;
    }

    // 获取 child 的父窗口
    HWND current_parent = GetParent(child);
    
    // 如果当前父窗口就是 parent，说明 child 是 parent 的子窗口
    if (current_parent == parent) {
        return true;
    }

    // 如果当前父窗口是 nullptr 或者是桌面窗口，说明 child 不是 parent 的子窗口
    if (current_parent == nullptr || current_parent == GetDesktopWindow()) {
        return false;
    }

    // 递归检查当前父窗口是否是 parent 的子窗口
    return is_any_child_window(parent, current_parent);
}

// // 示例用法
// int main() {
//     // 假设 parent 和 child 是有效的窗口句柄
//     HWND parent = /* 获取父窗口句柄 */;
//     HWND child = /* 获取子窗口句柄 */;

//     if (is_any_child_window(parent, child)) {
//         std::cout << "child 是 parent 的子窗口" << std::endl;
//     } else {
//         std::cout << "child 不是 parent 的子窗口" << std::endl;
//     }

//     return 0;
// }


// 将RGB颜色值的各分量统一调整一个差值
COLORREF change_color_luminance(COLORREF clr, int diff_val) {
    // 提取RGB分量
    int r = GetRValue(clr);
    int g = GetGValue(clr);
    int b = GetBValue(clr);

    // 调整每个分量的值
    r = std::clamp(r + diff_val, 0, 255);
    g = std::clamp(g + diff_val, 0, 255);
    b = std::clamp(b + diff_val, 0, 255);

    // 重新组合成新的COLORREF值
    return RGB(r, g, b);
}

// 将颜色值转换为一个RGB表达形式的字符串
CString color_to_rgb_string(COLORREF clr, TCHAR sp_ch = _T(',')) {
    int r = GetRValue(clr);
    int g = GetGValue(clr);
    int b = GetBValue(clr);

    CString str;
    str.Format(_T("%d%c%d%c%d"), r, sp_ch, g, sp_ch, b);
    return str;
}

// 将RGB表达形式的字符串转换为颜色值
COLORREF rgb_string_to_color(const CString& str, TCHAR sp_ch = _T(',')) {
    std::istringstream iss(str.GetString());
    int r, g, b;
    char separator;

    iss >> r;
    while (iss >> separator) {
        if (separator != sp_ch) {
            throw std::runtime_error("Invalid separator in RGB string");
        }
        if (!(iss >> g)) {
            throw std::runtime_error("Invalid RGB string format");
        }
        if (!(iss >> separator) || separator != sp_ch) {
            throw std::runtime_error("Invalid separator in RGB string");
        }
        if (!(iss >> b)) {
            throw std::runtime_error("Invalid RGB string format");
        }
        break;
    }

    if (iss.fail()) {
        throw std::runtime_error("Invalid RGB string format");
    }

    return RGB(r, g, b);
}


bool make_window_none_children_client_region(CWnd* wnd, CRgn& res_rgn) {
    if (!wnd) {
        return false;
    }

    // 获取窗口的客户区矩形
    CRect client_rect;
    if (!wnd->GetClientRect(&client_rect)) {
        return false;
    }

    // 创建一个矩形区域作为初始裁剪区域
    res_rgn.CreateRectRgnIndirect(&client_rect);

    // 获取窗口的所有子窗口
    CWnd* pChild = wnd->GetWindow(GW_CHILD);
    while (pChild) {
        // 检查子窗口是否可见
        if (pChild->IsWindowVisible()) {
            // 获取子窗口的客户区矩形
            CRect child_rect;
            if (pChild->GetClientRect(&child_rect)) {
                // 将子窗口的客户区矩形转换为客户区坐标系
                pChild->MapWindowPoints(wnd, &child_rect);

                // 创建一个子窗口的矩形区域
                CRgn child_rgn;
                child_rgn.CreateRectRgnIndirect(&child_rect);

                // 从裁剪区域中减去子窗口的矩形区域
                res_rgn.CombineRgn(res_rgn, child_rgn, RGN_DIFF);
            }
        }

        // 获取下一个子窗口
        pChild = pChild->GetNextWindow();
    }

    // 检查裁剪区域是否为空
    if (res_rgn.GetRegionData(NULL, 0, NULL) == 0) {
        return false;
    }

    return true;
}


// 辅助递归函数
void travel_tree_control_items_recursive(CTreeCtrl& tree, std::function<bool(CTreeCtrl&, HTREEITEM)> cb_fun, HTREEITEM item, bool inc_item, int depth) {
    if (inc_item && cb_fun(tree, item)) {
        return; // 回调函数返回 true，停止遍历
    }

    if (depth == 0) {
        return; // 达到最大深度，停止遍历
    }

    HTREEITEM child = tree.GetFirstItem(item);
    while (child) {
        travel_tree_control_items_recursive(tree, cb_fun, child, true, depth - 1);
        child = tree.GetNextSiblingItem(child);
    }
}

// 主函数
void travel_tree_control_items(CTreeCtrl& tree, std::function<bool(CTreeCtrl&, HTREEITEM)> cb_fun, HTREEITEM st_item, bool inc_st, int depth) {
    if (st_item == nullptr) {
        // 如果起始节点为空，遍历所有根节点
        HTREEITEM root = tree.GetRootItem();
        while (root) {
            travel_tree_control_items_recursive(tree, cb_fun, root, inc_st, depth);
            root = tree.GetNextSiblingItem(root);
        }
    } else {
        // 从指定的起始节点开始遍历
        travel_tree_control_items_recursive(tree, cb_fun, st_item, inc_st, depth);
    }
}

// // 示例用法
// void CMyTreeCtrl::OnLButtonDown(UINT nFlags, CPoint point) {
//     // 获取点击位置的节点
//     HTREEITEM hit_item = HitTest(point);
//     if (hit_item == nullptr) {
//         return;
//     }

//     // 定义回调函数
//     auto callback = [](CTreeCtrl& tree, HTREEITEM item) -> bool {
//         CString text;
//         tree.GetItemText(item, text);
//         AfxMessageBox(text); // 显示节点文本
//         return false; // 继续遍历
//     };

//     // 遍历从点击位置开始的子树
//     travel_tree_control_items(*this, callback, hit_item, true, -1);
// }