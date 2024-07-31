Option Explicit

Private Declare PtrSafe Function WaitForSingleObject Lib "kernel32" _
    (ByVal hHandle As Long, ByVal dwMilliseconds As Long) As Long

Private Declare PtrSafe Function GetExitCodeProcess Lib "kernel32" _
    (ByVal hProcess As Long, ByRef lpExitCode As Long) As Long

Private Declare PtrSafe Function CloseHandle Lib "kernel32" _
    (ByVal hObject As Long) As Long
    
Sub main()
    Dim out_dir As String, print_dir As String, result As Variant
    result = HeadingAll()
    out_dir = result(0)
    print_dir = result(1)
    

    Application.DisplayAlerts = False
    'exe 处理获取数据
    Call WaitAnalyse(out_dir)
    Dim xlApp As Object
    Dim xlBook As Object
    Dim xlSheet As Object
    Dim rngData As Object
    Dim i As Long
    Dim lastRow As Long
    Dim strExcelFilePath As String
    
    ' Excel文件路径
    strExcelFilePath = out_dir & "统计结果.xlsx"
    If Dir(strExcelFilePath) = "" Then
        Debug.Print strExcelFilePath & ":文件不存在"
        Exit Sub
    End If
    
    
    ' 创建Excel应用程序对象
    Set xlApp = CreateObject("Excel.Application")
    
    ' 打开Excel文件
    Set xlBook = xlApp.Workbooks.Open(strExcelFilePath)

    Dim fileItem, fileName As String
    fileItem = Dir(print_dir & "*.docx")
    Do While fileItem <> ""
        Dim fullName As String
        fullName = print_dir & fileItem
        fileName = GetFileName(fileItem)
        With Documents.Open(fullName)
        '两列
            Call FenceTwo
            '添加目录
            Call AddCatalog(fileName)
            '拷贝excel结果数据
            Call Fence(3)
            Call copy_xls(fileName, xlBook)
            Call AddPageNum
            Call ResetSectionNum
            ActiveDocument.Save
            ActiveDocument.Close
        End With
        fileItem = Dir
        
    Loop
      Application.DisplayAlerts = True

       
    ' 关闭Excel文件和应用程序
    xlBook.Close SaveChanges:=False
    xlApp.Quit
    
    ' 清理
    Set rngData = Nothing
    Set xlSheet = Nothing
    Set xlBook = Nothing
    Set xlApp = Nothing
       
End Sub


Sub copy_xls(xls_name As String, xlBook As Object)
    Dim xlSheet As Object
    Dim rngData As Object
    Dim i As Long, j As Long
    Dim lastRow As Long
    Dim strExcelFilePath As String
    ' 将光标移动到文档主体的末尾
   On Error Resume Next
    Set xlSheet = xlBook.Worksheets(xls_name)
    '不存在就退出
    If xlSheet Is Nothing Then
        Debug.Print "工作簿不包含工作表："; xls_name, "统计结果不存在:"; xls_name
        Exit Sub
    End If
    
    
    
    ' 获取已使用的范围
    Set rngData = xlSheet.UsedRange
    
    ' 确定最后一行
    lastRow = rngData.Rows.count
    
    ' 复制前两列数据
    'rngData.Columns(1).Resize(lastRow, 2).Copy
    
    ' 切换回Word并粘贴数据
    'ActiveDocument.range.Collapse Direction:=wdCollapseEnd
    'ActiveDocument.range.Paste

    ' 在当前插入点创建表格
    Dim tbl As table
    Set tbl = ActiveDocument.Tables.Add(range:=Selection.range, NumRows:=lastRow, NumColumns:=2)
      ' 设置表格边框样式
    With tbl.Borders
        .OutsideLineStyle = wdLineStyleSingle ' 设置外部边框线型
        .InsideLineStyle = wdLineStyleSingle  ' 设置内部边框线型
        
        .OutsideLineWidth = wdLineWidth050pt ' 设置外部边框线宽
        .InsideLineWidth = wdLineWidth050pt   ' 设置内部边框线宽
        
        .OutsideColor = RGB(0, 0, 0)          ' 设置外部边框颜色
        .InsideColor = RGB(0, 0, 0)           ' 设置内部边框颜色
        
    End With
      ' 自动调整表格的列宽以适应内容
    tbl.AutoFitBehavior (wdAutoFitContent)
    ' 填充表格数据
    For i = 1 To lastRow
        For j = 1 To 2
            tbl.Cell(i, j).range.Text = rngData.Cells(i, j)
        Next j
    Next i
    
 ' 如果表格行数超过maxRows，则删除多余的行
 Dim RowCount As Long
    RowCount = tbl.Rows.count
    If RowCount > lastRow Then
        ' 反向遍历行，从最后一行开始删除
        For i = RowCount To lastRow + 1 Step -1
            tbl.Rows(i).Delete
        Next i
    End If


End Sub
Function GetProcessHandle(ByVal shellResult As Variant) As Long
    ' 将Variant转换为Long以获取进程句柄
    GetProcessHandle = CLng(shellResult)
End Function

'调用python处理数据
Sub WaitAnalyse(out_dir As String)
    Dim strExePath As String
    Dim strParams As String
    Dim objShell As Object
    
    Dim shellResult As Variant
    Dim exitCode As Long
    Dim processHandle As Long
    

    Const INFINITE As Long = -1
    exitCode = -1
    
    'Dim out_dir As String
    'out_dir = "E:/小红书竞标/参考话题/output/"
    
    ' 使用icacls命令给Everyone组添加读写权限
    'Call Shell("icacls """ & out_dir & """ /grant Everyone:(OI)(CI)F", vbHide)
    
    ' 定义EXE路径和参数
    strExePath = "E:/小红书竞标/代码/python代码/exe/ThemeCount.exe "
    strParams = " -i " & out_dir
    
    
        ' 使用Shell函数调用外部EXE程序
    shellResult = Shell(strExePath + strParams, vbNormalFocus)
    processHandle = GetProcessHandle(shellResult)
    
    ' 等待进程结束
    WaitForSingleObject processHandle, INFINITE
    
    ' 获取进程的退出代码
    GetExitCodeProcess processHandle, exitCode
    
    ' 清理资源
    CloseHandle processHandle

    Debug.Print "生成output/统计结果.xlsx:"; IIf(exitCode = 0, "成功", "失败")
    ' 运行结束后，恢复原来的权限（可选）
    'Call Shell("icacls """ & out_dir & """ /reset", vbHide)
    
    
    ' 创建Shell对象
    'Set objShell = CreateObject("WScript.Shell")
    
    ' 使用Shell对象的Run方法调用EXE，0表示等待程序结束
    'objShell.Run strExePath & " " & strParams, 0, True
    
    ' 清理
    'Set objShell = Nothing
End Sub

Function HeadingAll()
  Dim fd As FileDialog
    Dim strFolderPath As String
    
    ' 创建文件夹选择对话框
    With Application.FileDialog(msoFileDialogFolderPicker)
        
        If .Show = -1 Then ' 如果用户点击"确定"
            strFolderPath = .SelectedItems(1) ' 获取选中的文件夹路径
        End If
    
    End With

    If Len(strFolderPath) = 0 Then Exit Function
    
    Dim root_dir As String, out_dir As String, print_dir As String
    root_dir = GetRootDir(strFolderPath)
    out_dir = root_dir & "/output/"
    print_dir = root_dir & "/打印版/"
    Dim result_str(2) As String
    result_str(0) = out_dir
    result_str(1) = print_dir
    
    On Error Resume Next
    MkDir (out_dir)
    On Error Resume Next
    MkDir (print_dir)
    
    
    
    Dim fileItem
    fileItem = Dir(strFolderPath & "/*.docx")
    
        Do While fileItem <> ""
            Dim fullName As String
            fullName = strFolderPath & "/" & fileItem
            With Documents.Open(fullName)
                Call HeadingEach
 
                ActiveDocument.Save
                
                Application.DisplayAlerts = False
                '另存为 .txt，便于后续处理
                Dim txtPath As String
                txtPath = out_dir + GetFileName(fileItem) + ".txt"
                
                Dim printPath As String
                printPath = print_dir + GetFileName(fileItem) + ".docx"

                ActiveDocument.SaveAs2 fileName:=txtPath, FileFormat:=wdFormatText, _
                    LockComments:=False, Password:="", AddToRecentFiles:=True, WritePassword _
                    :="", ReadOnlyRecommended:=False, EmbedTrueTypeFonts:=False, _
                    SaveNativePictureFormat:=False, SaveFormsData:=False, SaveAsAOCELetter:= _
                    False, Encoding:=65001, InsertLineBreaks:=False, AllowSubstitutions:= _
                    False, LineEnding:=wdCRLF, CompatibilityMode:=0
                
                
                
                ActiveDocument.SaveAs fileName:=printPath, FileFormat:=wdFormatXMLDocument
                
                ActiveDocument.Close 'savechanges:=wdSaveChanges

                Application.DisplayAlerts = True
                
                fileItem = Dir
            End With
        Loop

    
    HeadingAll = result_str
End Function

Function GetRootDir(cur_dir As String) As String
    Dim fso As Object
    Dim folder As Object
    Dim parentFolderPath As String
    

    Set fso = CreateObject("Scripting.FileSystemObject")
    
    ' 获取当前文档的完整路径
    Set folder = fso.GetFolder(cur_dir)
    
    ' 获取父目录
    Set folder = folder.ParentFolder
    
    ' 输出父目录的路径
    GetRootDir = folder.Path
    
    ' 清理
    Set folder = Nothing
    Set fso = Nothing

End Function

Function GetFileName(ByVal fileName As String) As String
Dim pos As Integer

pos = InStrRev(fileName, ".")
GetFileName = IIf(pos > 1, VBA.Left(fileName, pos - 1), fileName)
End Function

Sub HeadingEach()
    Application.ScreenUpdating = False
    ActiveDocument.Content.Select
    
    
    Call RecurseReplaceAll
    Call PageEdge
    Call Fence
    

    Call PreNum(GetFilePreStr())
    '字体
    Selection.Font.Size = 7

    
    Dim rng As range
    Set rng = ActiveDocument.Content

    
    rng.End = rng.start + 2
    Call modifySelection(rng)

    Set rng = ActiveDocument.Content
    With rng.Find
        .Text = "^p^p^p" ' ^p 代表一个段落标记，即换行符
        .Forward = True
        .Wrap = wdFindStop ' 如果到文档末尾仍未找到，则停止查找
        .Format = False
        .MatchCase = False
        .MatchWholeWord = True

        Do While (.Execute() = True)
        
            'Debug.Print rng.start; rng.End; rng
            
            rng.Collapse wdCollapseEnd
            Call modifySelection(rng)


            
            

        Loop
    End With
    Application.ScreenUpdating = True
End Sub

Sub modifySelection(rng As range)
    Selection.start = rng.End + 1
    Selection.HomeKey Unit:=wdLine
    Selection.EndKey Unit:=wdLine, Extend:=wdExtend
    Selection.Style = ActiveDocument.Styles("小红书笔记")
    rng.start = Selection.End + 1
    rng.End = ActiveDocument.Content.End

End Sub


Sub RecurseReplaceAll()
Call RecurseReplace("^l^l", "^l", 3)
Call RecurseReplace("^l", "^p")
Call RecurseReplace("^p.^p", "^p")
Call RecurseReplace("^p-^p", "^p")
Call RecurseReplace("^p^p^p^p", "^p^p^p", 10)
Call RecurseReplace("^p^p^p", "^p@^p@^p")
Call RecurseReplace("^p^p", "^p", 3)

Call RecurseReplace("^p@^p@^p", "^p^p^p", 3)
End Sub

Sub RecurseReplace(orgStr As String, newStr As String, Optional times As Integer = 1)

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = orgStr
        .Replacement.Text = newStr
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = False
        .MatchWholeWord = False
        .MatchByte = True
        .MatchWildcards = False
        .MatchSoundsLike = False
        .MatchAllWordForms = False
    End With
    Dim count As Long
    count = Selection.Characters.count
    Dim isSame As Boolean
    isSame = False
    
    
    
    Do While (times > 0 And Not isSame)
    times = times - 1
        Selection.Find.Execute Replace:=wdReplaceAll
        Dim curCount As Long
        curCount = Selection.Characters.count
        isSame = curCount = count
        count = curCount
    Loop
End Sub


Sub PageEdge()
    With Selection.PageSetup
        .LeftMargin = CentimetersToPoints(1.7)
        .RightMargin = CentimetersToPoints(1)
        .TopMargin = CentimetersToPoints(1)
        .BottomMargin = CentimetersToPoints(1.2)
    End With



End Sub

Sub FenceTwo()
    With Selection.PageSetup.TextColumns
        .SetCount NumColumns:=2
        .EvenlySpaced = True
        .LineBetween = True
        .Width = CentimetersToPoints(9.12)
        .Spacing = CentimetersToPoints(0.75)
    End With
End Sub

Sub PreNum(preStr As String)

    With ActiveDocument.Styles("标题 2,小红书笔记").ParagraphFormat

        .SpaceBefore = 0
        .SpaceBeforeAuto = False
        .SpaceAfter = 0
        .SpaceAfterAuto = False
        .LineSpacingRule = wdLineSpaceMultiple
        .LineSpacing = LinesToPoints(1.73)
        
        .Alignment = wdAlignParagraphCenter

    End With
    
        With ActiveDocument.Styles("标题 2,小红书笔记").Font
        .Size = 9
        .Bold = True
        .Italic = False
        .Underline = wdUnderlineNone
        .UnderlineColor = wdColorAutomatic
        .StrikeThrough = False
        .DoubleStrikeThrough = False
        .Outline = False
        .Emboss = False
        .Shadow = False
        .Hidden = False
        .SmallCaps = False
        .AllCaps = False
        .Color = wdColorAutomatic
        .Engrave = False
        .Superscript = False
        .Subscript = False
        .Scaling = 100
        .Kerning = 1
        .Animation = wdAnimationNone
        .DisableCharacterSpaceGrid = False
        .EmphasisMark = wdEmphasisMarkNone
        .Ligatures = wdLigaturesNone
        .NumberSpacing = wdNumberSpacingDefault
        .NumberForm = wdNumberFormDefault
        .StylisticSet = wdStylisticSetDefault
        .ContextualAlternates = 0
    End With
    
    
    ActiveDocument.Styles("标题 2,小红书笔记").NoSpaceBetweenParagraphsOfSameStyle = _
        False
    With ListGalleries(wdNumberGallery).ListTemplates(1).ListLevels(1)
        .NumberFormat = preStr + "_%1."
        .NumberStyle = wdListNumberStyleArabicLZ2

        With .Font
            .Bold = wdUndefined
            .Italic = wdUndefined
            .StrikeThrough = wdUndefined
            .Subscript = wdUndefined
            .Superscript = wdUndefined
            .Shadow = wdUndefined
            .Outline = wdUndefined
            .Emboss = wdUndefined
            .Engrave = wdUndefined
            .AllCaps = wdUndefined
            .Hidden = wdUndefined
            .Underline = wdUndefined
            .Color = wdUndefined
            .Size = wdUndefined
            .Animation = wdUndefined
            .DoubleStrikeThrough = wdUndefined
            .name = ""
        End With
        .LinkedStyle = "标题 2"
    End With
    ActiveDocument.Styles("标题 2").LinkToListTemplate ListTemplate:= _
        ListGalleries(wdNumberGallery).ListTemplates(1), ListLevelNumber:=1
    With ActiveDocument.Styles("标题 2")
        .AutomaticallyUpdate = True
        .BaseStyle = "正文"
        .NextParagraphStyle = "正文"
    End With
End Sub
Function GetFilePreStr() As String
Dim org As String
org = ActiveDocument.name
Dim arr

arr = Split(org, "_")
GetFilePreStr = IIf(UBound(arr) > LBound(arr), arr(0), "1000")
End Function
'针对统计结果，自动调整表格样式
Sub AjustTable()
    ActiveDocument.Select
    Selection.WholeStory
    Selection.Font.Size = 10
    Call PageEdge
    
    With Selection.PageSetup.TextColumns
        .SetCount NumColumns:=3
        .EvenlySpaced = True
        .LineBetween = False
        .Width = CentimetersToPoints(6)
        .Spacing = CentimetersToPoints(1.27)
    End With

    Dim table As table
    ' 遍历所有表格
    For Each table In ActiveDocument.Tables
        table.Select
        Call AjustTableEach
    Next
End Sub
Sub AjustTableEach()

        Selection.ParagraphFormat.Alignment = wdAlignParagraphLeft
        Selection.Tables(1).AutoFitBehavior (wdAutoFitContent)
        With Selection.Borders(wdBorderTop)
            .LineStyle = Options.DefaultBorderLineStyle
            .LineWidth = Options.DefaultBorderLineWidth
            .Color = Options.DefaultBorderColor
        End With
        With Selection.Borders(wdBorderLeft)
            .LineStyle = Options.DefaultBorderLineStyle
            .LineWidth = Options.DefaultBorderLineWidth
            .Color = Options.DefaultBorderColor
        End With
        With Selection.Borders(wdBorderBottom)
            .LineStyle = Options.DefaultBorderLineStyle
            .LineWidth = Options.DefaultBorderLineWidth
            .Color = Options.DefaultBorderColor
        End With
        With Selection.Borders(wdBorderRight)
            .LineStyle = Options.DefaultBorderLineStyle
            .LineWidth = Options.DefaultBorderLineWidth
            .Color = Options.DefaultBorderColor
        End With
        With Selection.Borders(wdBorderHorizontal)
            .LineStyle = Options.DefaultBorderLineStyle
            .LineWidth = Options.DefaultBorderLineWidth
            .Color = Options.DefaultBorderColor
        End With
        With Selection.Borders(wdBorderVertical)
            .LineStyle = Options.DefaultBorderLineStyle
            .LineWidth = Options.DefaultBorderLineWidth
            .Color = Options.DefaultBorderColor
        End With
End Sub
'单列显示
Sub AddCatalog(name As String)
    Dim rng As range
    
    ' 创建一个 Range 对象，代表整个文档,将范围设置为文档的第一个字符
    Set rng = ActiveDocument.range(start:=0, End:=0)
       
    ' 插入一个下一页的换节符
    rng.InsertBreak Type:=wdSectionBreakNextPage
    rng.Collapse Direction:=wdCollapseStart
    Selection.SetRange start:=0, End:=0
    Call TextType
    Call Fence
    
        ' 在当前插入点添加文本“目录”
    Selection.TypeText Text:="目录:" & name
    Call ThemeType
    
    ' 设置当前段落为居中对齐
    Selection.ParagraphFormat.Alignment = wdAlignParagraphCenter
    
    ' 添加一个新行，以便后续内容不会紧跟着标题
    Selection.TypeParagraph

    ' 移动光标到下一行的开始
    'Selection.MoveDown Unit:=wdLine, count:=1
    'Selection.MoveUp Unit:=wdLine, count:=1
    Selection.Collapse Direction:=wdCollapseStart
    Call TextType

    
    'Selection.MoveDown Unit:=wdLine, count:=1
    'Selection.Collapse Direction:=wdCollapseStart
    
    ' 更新字段，确保目录是最新的
    ActiveDocument.Fields.Update
    ' 插入目录，使用Word UI的默认设置
    ActiveDocument.TablesOfContents.Add range:=Selection.range, _
                                         TableID:=1, _
                                         IncludePageNumbers:=True, _
                                         RightAlignPageNumbers:=True, _
                                         UseHyperlinks:=True
                                
   Selection.SetRange start:=ActiveDocument.Content.End, End:=ActiveDocument.Content.End
   Selection.Collapse Direction:=wdCollapseEnd
   Selection.InsertBreak Type:=wdSectionBreakNextPage
   
   Selection.SetRange start:=ActiveDocument.Content.End, End:=ActiveDocument.Content.End
   Selection.Collapse Direction:=wdCollapseEnd
   
    Set rng = ActiveDocument.Content
    
    ' 将插入点移动到文档末尾
    rng.Collapse Direction:=wdCollapseEnd
    rng.EndOf Unit:=wdStory
    
    ' 插入分节符
    'rng.InsertBreak Type:=wdSectionBreakNextPage
    
    ' 将插入点移到新节的第一行
    'rng.Collapse Direction:=wdCollapseEnd
    'rng.MoveDown Unit:=w5dLine, count:=1
    Selection.SetRange start:=rng.End, End:=rng.End
    Selection.TypeText Text:="话题统计结果:" & name
    Call ThemeType
    Selection.SetRange start:=rng.End, End:=rng.End
    Call TextType
    ' 将插入点移到新节的第一行
    'Selection.MoveDown Unit:=wdLine, count:=1
   
End Sub
'分栏
Sub Fence(Optional cols As Integer = 1)

    With Selection.PageSetup.TextColumns
        .SetCount NumColumns:=cols
        .EvenlySpaced = True
        .LineBetween = True
    End With
End Sub
'更新所有域
Sub UpdateAllFields()
    ActiveDocument.Fields.Update
End Sub
Sub StylesType(Optional typestr As String = "标题")
    Selection.Style = ActiveDocument.Styles(typestr)
End Sub

Sub ThemeType()
    Call StylesType("标题")
End Sub

Sub TextType()
    Call StylesType("正文")
End Sub
Sub AddPageNumbersToFooter()
    Dim rngHeaderFooter As range
    Dim pgNum As PageNumber
    Dim sec As Section
    For Each sec In ActiveDocument.Sections
            ' 设置页脚范围
        Set rngHeaderFooter = sec.Footers(wdHeaderFooterPrimary).range
        
        ' 清除页脚中已有的内容
        rngHeaderFooter.Cells.ClearContents
        
        Dim pageCount As Long
        pageCount = sec.Information(wdLastPageNumberOfSection) - sec.Information(wdFirstPageNumberOfSection) + 1
        ' 添加文本到页脚，例如 "第 X 页，共 Y 页"
        With rngHeaderFooter
            .Collapse Direction:=wdCollapseEnd
            
            
            ' 添加页码
            Set pgNum = .PageNumbers.Add(PageNumberAlignment:=wdAlignPageNumberCenter)
            
            .InsertAfter Text:=" / " + Str(pageCount)
            
            ' 添加总页数
            .InsertField FieldName:="NumPages", FieldCode:="NUMPAGES \* MERGEFORMAT "
        End With
    
    Next
    ' 更新域以显示正确的页码
    ActiveDocument.Fields.Update
End Sub
Sub AddPageNum()
'
' 宏2 宏
'
'
    If ActiveWindow.View.SplitSpecial <> wdPaneNone Then
        ActiveWindow.Panes(2).Close
    End If
    If ActiveWindow.ActivePane.View.Type = wdNormalView Or ActiveWindow. _
        ActivePane.View.Type = wdOutlineView Then
        ActiveWindow.ActivePane.View.Type = wdPrintView
    End If
    ActiveWindow.ActivePane.View.SeekView = wdSeekCurrentPageFooter
    
    On Error Resume Next
    Application.Templates( _
        "C:\Users\Administrator\AppData\Roaming\Microsoft\Document Building Blocks\2052\15\Built-In Building Blocks.dotx" _
        ).BuildingBlockEntries("普通数字 2").Insert Where:=Selection.range, RichText _
        :=True
    If ActiveWindow.ActivePane.View.Type = wdNormalView Or ActiveWindow. _
        ActivePane.View.Type = wdOutlineView Then
        If ActiveWindow.Panes.count = 2 Then
            ActiveWindow.Panes(2).Close
        End If
        ActiveWindow.View.SplitSpecial = wdPaneCurrentPageHeader
    Else
        ActiveWindow.View.SeekView = wdSeekCurrentPageHeader
    End If
    If ActiveWindow.ActivePane.View.Type = wdNormalView Or ActiveWindow. _
        ActivePane.View.Type = wdOutlineView Then
        If ActiveWindow.Panes.count = 2 Then
            ActiveWindow.Panes(2).Close
        End If
        ActiveWindow.View.SplitSpecial = wdPaneCurrentPageHeader
    Else
        ActiveWindow.View.SeekView = wdSeekCurrentPageHeader
    End If
    If ActiveWindow.ActivePane.View.Type = wdNormalView Or ActiveWindow. _
        ActivePane.View.Type = wdOutlineView Then
        If ActiveWindow.Panes.count = 2 Then
            ActiveWindow.Panes(2).Close
        End If
        ActiveWindow.View.SplitSpecial = wdPaneCurrentPageHeader
    Else
        ActiveWindow.View.SeekView = wdSeekCurrentPageHeader
    End If
    If ActiveWindow.ActivePane.View.Type = wdNormalView Or ActiveWindow. _
        ActivePane.View.Type = wdOutlineView Then
        If ActiveWindow.Panes.count = 2 Then
            ActiveWindow.Panes(2).Close
        End If
        ActiveWindow.View.SplitSpecial = wdPaneCurrentPageHeader
    Else
        ActiveWindow.View.SeekView = wdSeekCurrentPageHeader
    End If
    If ActiveWindow.ActivePane.View.Type = wdNormalView Or ActiveWindow. _
        ActivePane.View.Type = wdOutlineView Then
        If ActiveWindow.Panes.count = 2 Then
            ActiveWindow.Panes(2).Close
        End If
        ActiveWindow.View.SplitSpecial = wdPaneCurrentPageHeader
    Else
        ActiveWindow.View.SeekView = wdSeekCurrentPageHeader
    End If
    
    ActiveWindow.ActivePane.View.SeekView = wdSeekMainDocument
End Sub
Sub ResetSectionNum()
    Dim sec As Variant
    For Each sec In ActiveDocument.Sections
        With sec.Headers(1).PageNumbers
        .NumberStyle = wdPageNumberStyleArabic
        .HeadingLevelForChapter = 0
        .IncludeChapterNumber = False
        .ChapterPageSeparator = wdSeparatorHyphen
        .RestartNumberingAtSection = True
        .StartingNumber = 1
        End With
    
    Next
    Call UpdateAllFields

End Sub



Sub TabTitle()
    Selection.TypeText Text:="话题数目统计"
    Selection.ParagraphFormat.Alignment = wdAlignParagraphCenter
    Call ThemeType
End Sub
