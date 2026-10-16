# Debug: dump the full UIA descendant tree of the Inno wizard window.
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$auto = [System.Windows.Automation.AutomationElement]
$tree = [System.Windows.Automation.TreeScope]

$cond = New-Object System.Windows.Automation.PropertyCondition(
    $auto::ControlTypeProperty, [System.Windows.Automation.ControlType]::Window)
$wins = $auto::RootElement.FindAll($tree::Children, $cond)
foreach ($w in $wins) {
    $n = $w.Current.Name
    if ($n -match '安装|PolyXRD' -and $w.Current.ClassName -ne 'CabinetWClass') {
        Write-Host ("WINDOW '{0}' class={1} pid={2}" -f $n, $w.Current.ClassName, $w.Current.ProcessId)
        $all = $w.FindAll($tree::Descendants,
            [System.Windows.Automation.Condition]::TrueCondition)
        foreach ($e in $all) {
            Write-Host ("  {0}  '{1}'  enabled={2}" -f $e.Current.ControlType.ProgrammaticName, $e.Current.Name, $e.Current.IsEnabled)
        }
    }
}
