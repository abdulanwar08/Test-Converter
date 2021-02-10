@echo off  
FOR /F "tokens=1,2 delims==" %%G IN (config.properties) DO (set %%G=%%H)  

set LOGFILE=pentaho_log.log

echo "Checking Dependencies"
call pip install pipreqs
call pipreqs .
call pip install -r requirements.txt
echo "Dependencies downloaded successfully"

echo "Starting Pentaho Job.."

if %NoOfFiles%==2 (
	echo %NoOfFiles%
	echo "Multiple transformation is Initiated"
	call %base_dir%pan.bat /file:"%file_path1%" "/level=Basic" /logfile="%input%\%LOGFILE%" "-param:input=%input%"
	call %base_dir%pan.bat /file:"%file_path2%" "/level=Basic" /logfile="%input%\%LOGFILE%" "-param:input=%input%"
	) else (
	echo %NoOfFiles%
	echo "Only one transformation is Initiated"
	call %base_dir%pan.bat /file:"%file_path1%" "/level=Basic" /logfile="%input%\%LOGFILE%" "-param:input=%input%"
	)

echo "Pentaho Job Completed.."
echo "Initiate Comparison"
call "%PYTHON_HOME%\python.exe" ".\src\TestConverters.py"
echo "Execution Completed"

