@echo off
echo === Git Update ===
git status --porcelain || exit /b 1
git add . || exit /b 1
for /f "tokens=2 delims==" %%a in ('wmic OS get localdatetime /value') do set dt=%%a
set ts=%dt:~0,4%-%dt:~4,2%-%dt:~6,2% %dt:~8,2%:%dt:~10,2%
git commit -m "Update: %ts%" || exit /b 1
git push origin main || exit /b 1
echo Done.
