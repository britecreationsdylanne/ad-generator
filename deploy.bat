@echo off
echo ========================================
echo BriteCo Ad Generator - Deploy to Cloud
echo ========================================
echo.

REM Check if gcloud is installed
where gcloud >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Google Cloud CLI not found!
    echo Please install it from: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

echo Deploying to Google Cloud Run...
echo This may take 3-5 minutes.
echo.

gcloud run deploy briteco-ad-generator ^
  --source . ^
  --platform managed ^
  --region us-central1 ^
  --memory 2Gi ^
  --timeout 300 ^
  --set-secrets=ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest,OPENAI_API_KEY=OPENAI_API_KEY:latest,GOOGLE_API_KEY=GOOGLE_API_KEY:latest

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Deployment successful!
    echo ========================================
    echo.
    echo Your app URL will be shown above.
    echo Share this URL with your team!
) else (
    echo.
    echo Deployment failed. Check the error messages above.
)

pause
