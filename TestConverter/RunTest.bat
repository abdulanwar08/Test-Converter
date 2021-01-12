@echo off  
FOR /F "tokens=1,2 delims==" %%G IN (config.properties) DO (set %%G=%%H)  

set LOGFILE=pentaho_log.log
call :LOG > %LOGFILE%
exit /B

:LOG
echo "Starting Job.."


if %ExecutableFiles%==2 (
	echo "Multiple transformation is Initiated"
	call %base_dir%pan.bat /file:"%file_path1%" "/level=Basic" "-param:input=%input%"
	call %base_dir%pan.bat /file:"%file_path2%" "/level=Basic" "-param:input=%input%"
	) else (
	call %base_dir%pan.bat /file:"%file_path1%" "/level=Basic" "-param:input=%input%"
	)

echo "Pentaho Job Completed.."
call "%PYTHON_HOME%\python.exe" ".\src\TestConverters.py"

