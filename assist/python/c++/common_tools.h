// 在MFC界面主进程中的非界面耗时代码中合理间隔内调用此函数可以避免界面被阻塞
// 此函数只能在主界面进程中调用，不能在其它界面进程或其它线程中使用，否则会有跨线程问题
void x_do_ui_events() ;

// 当本模块作为子进程被启动时，阻塞式等待主进程结束（只要主进程不存在则返回，哪怕崩溃或强制结束也一样），本功能的
// 使用需要了解一定知识，使用时可咨询WYZ
// 调本接口时务必确保执行的代码所在进程为子进程，否则无法正常判断
// 由于本接口是阻塞式的，因此，子进程需要在线程中调用，否则会阻塞主线程
// 返回0表示主进程结束了才返回的，返回1表示外部设置停止等待的标志才返回的，2表示异常情况才返回的
int sub_process_wait_for_host_exit();
void set_stop_flag();


// 返回当前模块编译时的日期，返回参数：<月(1-12),日(1-31),年(最小1900),时(0-59),分(0-59),秒(0-59)> 
// 注意：不是当前的时间，而是本模块被编译的时间
 std::array<int, 6> get_framework_compiling_data();
 // 判断一个窗口是不是另一个窗口的子窗口(多级父子窗口关系也能正常支持)，父窗口不可以是桌面窗口（原则上任何窗口都是桌面窗口的子窗口） 
 bool is_any_child_window(HWND parent, HWND child);


 // 将RGB颜色值的各分量统一调整一个差值，正表示调亮，负表示调暗
  COLORREF change_color_luminance(COLORREF clr, int diff_val);

  // 将颜色值转换为一个RGB表达形式的字符串，以及反向转换，各值之间默认用英文逗号隔开（可通过参数指定）
 CString color_to_rgb_string(COLORREF clr, TCHAR sp_ch = _T(','));
 COLORREF rgb_string_to_color(const CString& str, TCHAR sp_ch = _T(','));


 // 根据传入的窗口，生成基于该窗口客户区坐标系的一个dc裁剪区域，该裁剪区域会去除传入窗口中的所有子窗口区域，无法生成裁剪区域返回false
// 注意：如果子窗口为隐藏状态，则不会剪切所在区域
// 示例用法如下：
// CRect client_rt;
// GetClientRect(&client_rt);
// CRgn rgn;
// if (make_window_none_children_client_region(this, rgn)) SelectClipRgn(dc->m_hDC, rgn);
// dc->FillSolidRect(client_rt, m_back_color);
bool make_window_none_children_client_region(CWnd* wnd, CRgn& res_rgn);


// 遍历一棵树的节点
// cb_fun: 节点的回调函数(遍历到的所有节点都会调用回调函数，回调函数返回true表示停止遍历，返回false表示继续往下遍历)
// st_item: 从本节点开始遍历（只遍历本节点及其子树）
// inc_st: 是否遍历起始节点，即经过起始节点是否调用回调函数
// depth: 遍历的深度，0为只遍历起始节点，1只遍历起始节点的直接子节点，依次类推指定最多遍历多少层，为-1表示遍历整棵子树
// 注意：当传入的节点句柄为空时，内部支持多根的树全部遍历，否则只遍历指定节点所在的子树
void travel_tree_control_items(CTreeCtrl& tree, std::function<bool(CTreeCtrl&, HTREEITEM)> cb_fun,
	HTREEITEM st_item = nullptr, bool inc_st = true, int depth = -1);


