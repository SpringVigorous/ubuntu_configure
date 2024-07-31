@echo off
setlocal enabledelayedexpansion

rem 遍历删除Debug文件夹
for /r "%~dp0" %%f in (*) do (

    if "%%~ff" neq ".git" (
        echo 删除文件: %%~ff
        @REM del /q "%~ff"
    )
)

rem 遍历删除Release文件夹
for /r "%~dp0" %%f in (*) do (
    if "%%~ff" neq ".git" (
        echo 删除文件: %%~ff
        @REM del /q "%~ff"
    )
)

rem 遍历删除.ich文件
for /r "%~dp0" %%f in (*.ich) do (
    echo 删除文件: %%~ff
    @REM del /q "%~ff"
)


pause