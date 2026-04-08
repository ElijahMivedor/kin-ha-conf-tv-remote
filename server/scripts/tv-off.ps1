$port = New-Object System.IO.Ports.SerialPort "COM4", 9600, [System.IO.Ports.Parity]::None, 8, [System.IO.Ports.StopBits]::One
$port.Open()
Start-Sleep -Milliseconds 500

$port.Write("POWR0000`r`n")
Write-Host "Turning off..."
Start-Sleep -Seconds 5

$port.Close()
Write-Host "Done."
