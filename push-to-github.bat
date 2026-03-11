@echo off
REM Push AI Employee FTE to GitHub

cd /d E:\AI-Employee-FTE

echo Adding all files to Git...
git add -A

echo Committing changes...
git commit -m "feat: Complete AI Employee FTE Platinum Tier"

echo Pushing to GitHub...
git push origin main

echo Done!
pause
