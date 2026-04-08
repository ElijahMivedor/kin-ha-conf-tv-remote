$port = New-Object System.IO.Ports.SerialPort "COM4", 9600, [System.IO.Ports.Parity]::None, 8, [System.IO.Ports.StopBits]::One
$port.Open()
Start-Sleep -Milliseconds 500

$port.Write("POWR0001`r`n")
Write-Host "Turning on..."
Start-Sleep -Seconds 25

$port.Write("INPS0010`r`n")
Write-Host "Switching to HDMI 1..."
Start-Sleep -Milliseconds 1000

$port.Close()
Write-Host "Done."
