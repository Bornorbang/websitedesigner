@echo off
echo Building Tailwind CSS...
npx tailwindcss -i ./static/css/input.css -o ./static/css/tailwind.min.css --minify
echo.
echo Collecting static files...
python manage.py collectstatic --noinput
echo.
echo Done! Tailwind CSS has been compiled and collected.
pause
