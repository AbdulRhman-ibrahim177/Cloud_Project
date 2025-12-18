@echo off
REM Quick start script for Windows

echo 🚀 Starting Cloud Project Frontend...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo ✅ Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Create .env if it doesn't exist
if not exist ".env" (
    echo ⚙️  Creating .env file...
    copy .env.example .env
    echo ⚠️  Please update .env with your settings!
)

REM Apply migrations
echo 🔄 Applying database migrations...
python manage.py migrate

REM Run development server
echo.
echo ✨ Starting development server...
echo 🌐 Frontend available at: http://localhost:8000
echo.

python manage.py runserver
