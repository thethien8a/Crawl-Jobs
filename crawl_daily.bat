@echo off
setlocal
cd /d D:\Practice\Scrapy\CrawlJob

if not exist logs mkdir logs
if not exist outputs mkdir outputs

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH-mm-ss"') do set TS=%%i

REM If you use a virtual environment, uncomment and adjust the path below
REM call Path_to_venv\activate.bat

REM Use full path to python.exe if needed (uncomment and adjust)
REM "C:\\Users\\YOU\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" run_spider.py --spider all --keyword "developer" --output "outputs\jobs_%TS%.json" >> "logs\crawl_%TS%.log" 2>&1

python run_spider.py --spider all --keyword "phan tich du lieu" --output "outputs\jobs_%TS%.json" >> "logs\crawl_%TS%.log" 2>&1

endlocal
