:: This is a batch file for Snapdragon. So we can simply command
:: python selenium_dragon.py linode <n> to play.bat <n>
:: Or play <n> if we put play.bat in a folder known by the Path system
:: environment variable.
@echo off

:: Use the absolute path to Selenium executable
set selenium_exe=C:\Users\User\Yuming\Selenium\dist\selenium_dragon.exe

:: Check if an argument was passed
if "%1"=="" goto prompt_input

:: If an argument was passed, use it
echo Running: %selenium_exe% linode %1
%selenium_exe% linode %1
goto end

:prompt_input
:: Prompt the user for input
echo How many songs would you like to play? (Enter a positive integer):
set /p n=Please enter the number:

:: Check if input was provided
if "%n%"=="" (
    echo Error: No input provided.
    pause
    exit /b 1
)

:: Run the Selenium executable with user input
echo Running: %selenium_exe% linode %n%
%selenium_exe% linode %n%

:end
:: Keep the CMD window open to show any errors
pause
