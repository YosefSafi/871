Write-Host "Starting Python Server (Dungeon Master)..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath "venv\Scripts\python.exe" -ArgumentList "-m uvicorn main:app --host 0.0.0.0 --port 8000" -WorkingDirectory "python_server"

Write-Host "Waiting 3 seconds for the Dungeon Master to wake up..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host "Starting C# Client (The Adventurer)..." -ForegroundColor Green
Set-Location "csharp_client"
dotnet run
