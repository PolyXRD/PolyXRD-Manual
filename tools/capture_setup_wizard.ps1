# Capture the real Inno Setup wizard pages of PolyXRD-RutAna-v1.5.0-Setup.exe
# using plain Win32 (EnumWindows / FindWindowEx / SendMessage BM_CLICK) and
# PrintWindow for screenshots. No UIA, no SendKeys, no foreground needed.
#
# Inno/VCL facts on this machine:
#   * Language dialog: top-level class "TSelectLanguageForm", buttons 确定/取消.
#   * Main wizard:     top-level class "TWizardForm".
#   * Buttons:         next / install / finish (class TNewButton).
#   * License radio:   TNewRadioButton; auto-launch: TNewCheckBox.
#   * BM_CLICK (0x00F5) works without foreground focus.
#
# NOTE: keep this file UTF-8 **with BOM** (PowerShell 5.1 reads BOM-less files
# as ANSI and the Chinese button captions below would be garbled).

param(
    [string]$Setup = 'D:\Project\XRD\PolyXRD-RutAna\dist\PolyXRD-RutAna-v1.5.0-Setup.exe',
    [string]$OutDir = 'D:\Project\XRD\PolyXRD-Manual\tools\shots\rutana_setup'
)

Add-Type -AssemblyName System.Drawing
Add-Type @'
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public class W {
    public delegate bool EnumProc(IntPtr h, IntPtr l);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
    [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr p, EnumProc cb, IntPtr l);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] public static extern IntPtr FindWindowEx(IntPtr p, IntPtr a, string cls, string txt);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint flags);
    [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left, Top, Right, Bottom; }

    public static string Text(IntPtr h) {
        var sb = new StringBuilder(512); GetWindowText(h, sb, 512); return sb.ToString();
    }
    public static string Class(IntPtr h) {
        var sb = new StringBuilder(256); GetClassName(h, sb, 256); return sb.ToString();
    }
    public static List<object[]> Tops() {
        var list = new List<object[]>();
        EnumWindows((h, l) => {
            if (IsWindowVisible(h)) list.Add(new object[] { h, Text(h), Class(h) });
            return true;
        }, IntPtr.Zero);
        return list;
    }
    public static List<object[]> Kids(IntPtr p) {
        var list = new List<object[]>();
        EnumChildWindows(p, (h, l) => {
            list.Add(new object[] { h, Text(h), Class(h), IsWindowVisible(h) });
            return true;
        }, IntPtr.Zero);
        return list;
    }
    public static List<object[]> VisibleKids(IntPtr p) {
        var list = new List<object[]>();
        EnumChildWindows(p, (h, l) => {
            if (IsWindowVisible(h)) list.Add(new object[] { h, Text(h), Class(h), true });
            return true;
        }, IntPtr.Zero);
        return list;
    }
    public static IntPtr FindKid(IntPtr p, string cls, string contains) {
        IntPtr cur = IntPtr.Zero;
        while (true) {
            cur = FindWindowEx(p, cur, cls, null);
            if (cur == IntPtr.Zero) return IntPtr.Zero;
            if (Text(cur).Contains(contains)) return cur;
        }
    }
    public static void Click(IntPtr h) { SendMessage(h, 0x00F5, IntPtr.Zero, IntPtr.Zero); }
    public static int CheckState(IntPtr h) { return (int)SendMessage(h, 0x00F1, IntPtr.Zero, IntPtr.Zero); }
}
'@

function Find-Top([string]$class) {
    foreach ($t in [W]::Tops()) {
        if ($t[2] -eq $class) { return , $t }
    }
    return $null
}

function Wait-Top([string]$class, [int]$timeoutSec) {
    $deadline = (Get-Date).AddSeconds($timeoutSec)
    while ((Get-Date) -lt $deadline) {
        $t = Find-Top $class
        if ($null -ne $t) { return $t }
        Start-Sleep -Milliseconds 400
    }
    return $null
}

function Snap([IntPtr]$h, [string]$name) {
    $r = New-Object W+RECT
    [void][W]::GetWindowRect($h, [ref]$r)
    $w = $r.Right - $r.Left; $ht = $r.Bottom - $r.Top
    if ($w -le 0 -or $ht -le 0) { Write-Host "SKIP $name"; return }
    $bmp = New-Object System.Drawing.Bitmap $w, $ht
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $hdc = $g.GetHdc()
    [void][W]::PrintWindow($h, $hdc, 2)
    $g.ReleaseHdc($hdc)
    $g.Dispose()
    $bmp.Save((Join-Path $OutDir $name), [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose()
    Write-Host "saved $name  ${w}x${ht}"
}

function Click-Kid([IntPtr]$parent, [string]$contains, [string]$cls) {
    $h = [W]::FindKid($parent, $cls, $contains)
    if ($h -eq [IntPtr]::Zero) {
        Write-Host "WARN: kid not found ($cls / '$contains'); children:"
        foreach ($k in [W]::Kids($parent)) { Write-Host ("   {0} '{1}'" -f $k[2], $k[1]) }
        return $false
    }
    [W]::Click($h)
    Write-Host ("clicked '{0}' ({1})" -f [W]::Text($h), $cls)
    return $true
}

# ---- clean leftovers ---------------------------------------------------------
Get-Process -ErrorAction SilentlyContinue |
    Where-Object { $_.ProcessName -like 'PolyXRD-RutAna*' } |
    ForEach-Object { Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 1

# ---- run installer -----------------------------------------------------------
Start-Process -FilePath $Setup | Out-Null
Write-Host 'installer launched'

# ---- page 0: language --------------------------------------------------------
$lang = Wait-Top 'TSelectLanguageForm' 90
if ($null -eq $lang) { Write-Host 'FAIL: language dialog not found'; exit 1 }
Start-Sleep -Milliseconds 800
Snap $lang[0] 'setup_00_language.png'
[void](Click-Kid $lang[0] '确定' 'TNewButton')
Start-Sleep -Milliseconds 2000

# ---- main wizard: heading-driven page loop -----------------------------------
$wiz = Wait-Top 'TWizardForm' 30
if ($null -eq $wiz) { Write-Host 'FAIL: wizard form not found'; exit 1 }
Start-Sleep -Milliseconds 1500

# map a visible TNewStaticText heading to a page key
function Get-Heading([IntPtr]$hw) {
    foreach ($k in [W]::VisibleKids($hw)) {
        if ($k[2] -ne 'TNewStaticText') { continue }
        $t = $k[1]
        if ($t -match '^许可协议')            { return 'license' }
        if ($t -match '^选择目标位置|位置$')   { return 'dir' }
        if ($t -match '^选择附加任务|附加任务') { return 'tasks' }
        if ($t -match '^准备安装')            { return 'ready' }
        if ($t -match '^正在安装|正在安装')     { return 'installing' }
    }
    return 'unknown'
}

$donePages = @{}
$deadline = (Get-Date).AddSeconds(300)
$page = 'unknown'
while ((Get-Date) -lt $deadline) {
    $page = Get-Heading $wiz[0]
    if ($page -eq 'installing') { break }
    if (-not $donePages.ContainsKey($page)) {
        if ($page -eq 'license') {
            Snap $wiz[0] 'setup_01_license.png'
            foreach ($k in [W]::VisibleKids($wiz[0])) {
                if ($k[2] -eq 'TNewRadioButton' -and ($k[1] -match '同意' -or $k[1] -match '接受')) {
                    [W]::Click($k[0])
                    Write-Host ("license accepted: '{0}'" -f $k[1])
                    break
                }
            }
            Start-Sleep -Milliseconds 900
            Snap $wiz[0] 'setup_02_license_accepted.png'
        }
        elseif ($page -eq 'dir')        { Snap $wiz[0] 'setup_03_dir.png' }
        elseif ($page -eq 'tasks')      { Snap $wiz[0] 'setup_04_tasks.png' }
        elseif ($page -eq 'ready')      { Snap $wiz[0] 'setup_05_ready.png' }
        else                            { Snap $wiz[0] ("setup_x_" + $page + ".png") }
        $donePages[$page] = $true
    }
    if ($page -eq 'ready') {
        # install now (click before logging: caption is read live below)
        $btn = [W]::FindKid($wiz[0], 'TNewButton', '安装')
        if ($btn -ne [IntPtr]::Zero) { [W]::Click($btn); Write-Host "clicked 安装" }
        break
    }
    $btn = [W]::FindKid($wiz[0], 'TNewButton', '下一步')
    if ($btn -eq [IntPtr]::Zero) { Start-Sleep -Milliseconds 500; continue }
    [W]::Click($btn)
    Write-Host "clicked 下一步 (page=$page)"
    Start-Sleep -Milliseconds 1500
}

# page: installing progress (shoot fast, install may be quick on overwrite)
Snap $wiz[0] 'setup_06_installing.png'

# finished page: wait for the finish button
$fin = [IntPtr]::Zero
$deadline = (Get-Date).AddSeconds(240)
while ((Get-Date) -lt $deadline) {
    Start-Sleep -Seconds 3
    $fin = [W]::FindKid($wiz[0], 'TNewButton', '完成')
    if ($fin -ne [IntPtr]::Zero) { break }
}
if ($fin -ne [IntPtr]::Zero) {
    Start-Sleep -Milliseconds 800
    Write-Host 'finished page visible kids:'
    foreach ($k in [W]::VisibleKids($wiz[0])) {
        Write-Host ("   {0} '{1}'" -f $k[2], $k[1])
    }
    Snap $wiz[0] 'setup_07_finished.png'
    # leave auto-launch as-is (documented default); click Finish
    [W]::Click($fin)
    Write-Host 'clicked Finish'
    Start-Sleep -Seconds 4
} else {
    Write-Host 'WARN: finished page never appeared'
}

# stop anything that auto-launched / any installer leftover
Get-Process -ErrorAction SilentlyContinue |
    Where-Object { $_.ProcessName -like 'PolyXRD-RutAna*' } |
    ForEach-Object { Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue }

Write-Host 'DONE'
