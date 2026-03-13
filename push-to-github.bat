@echo off
REM Push to GitHub

cd /d E:\AI-Employee-FTE

echo Adding all files...
git add -A

echo Committing changes...
git commit -m "feat: Add web dashboard for Replit demo"

echo Pushing to GitHub...
git push origin main

echo Done!
echo Check: https://github.com/HassaanDeveloper/AI-Employee-FTE
pause
