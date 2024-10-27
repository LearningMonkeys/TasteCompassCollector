@echo off

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists.
)

echo Activating virtual environment...
call venv\Scripts\activate

if exist "requirements.txt" (
    echo Installing packages from requirements.txt...
    pip install -r requirements.txt
) else (
    echo requirements.txt not found. Please make sure to provide it.
    exit /b 1
)

echo Setup complete. The virtual environment is activated.
