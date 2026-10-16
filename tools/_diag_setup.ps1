# Diagnostic: launch the Setup exe, list processes, and take a full-screen capture.
param(
    [string]$Setup = 'D:\Project\XRD\PolyXRD-RutAna\dist\PolyXRD-RutAna-v1.5.0-Setup.exe',
    [string]$Out = 'D:\Project\XRD\PolyXRD-Manual\tools\shots\rutana_setup\_diag.png'
)
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms

"file exists: " + (Test-Path $Setup)
$fi = Get-Item $Setup
"size: " + $fi.Length + "  modified: " + $fi.LastWriteTime

$proc = Start-Process -FilePath $Setup -PassThru
"started pid=" + $proc.Id
Start-Sleep -Seconds 6
$proc.Refresh()
"hasExited=" + $proc.HasExited
if ($proc.HasExited) { "exitCode=" + $proc.ExitCode }

"--- processes matching setup/polyxrd ---"
Get-Process | Where-Object { $_.ProcessName -like '*PolyXRD*' -or $_.ProcessName -like '*setup*' -or $_.ProcessName -like '*is-*' -or $_.ProcessName -like '*RutAna*' } |
    Select-Object Id, ProcessName, MainWindowTitle, @{n='HWND';e={$_.MainWindowHandle}} | Format-Table -AutoSize | Out-String

$vs = [System.Windows.Forms.SystemInformation]::VirtualScreen
$bmp = New-Object System.Drawing.Bitmap $vs.Width, $vs.Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($vs.X, $vs.Y, 0, 0, $bmp.Size)
$g.Dispose()
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
"saved fullscreen -> $Out  ($($vs.Width)x$($vs.Height))"
