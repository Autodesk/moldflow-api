# Exercises the Moldflow CLI in a user-journey order: session, discovery, project/mesh/solver/loads/plots
# dry-runs, optional live Synergy + project lifecycle, batch JSON scripting, then regression (expected failures).
#
# By default, when live project smoke is enabled (omit -SkipRealSmoke and -SkipProjectSmoke), the script runs
# a customer-style workflow: write a small ASCII STL, import, mesh, place an injection NDBC (create_ndbc_at_xyz),
# then analyze_now (solve) and probe plot/results APIs. Start-Process -Wait only waits for the CLI process;
# Synergy's analyze_now/solve COM call is asynchronous, so after the STL solve invoke this script polls
# study_doc.is_analysis_running until idle and then waits for result files to appear before exercising
# result/plot/probe APIs (see -AnalysisWaitMaxSeconds / -AnalysisPollSeconds).
# Use -SkipSTLWorkflow for mesh_type-only project checks.
# (The old opt-in switch -STLWorkflow is unnecessary; use -SkipSTLWorkflow only when you want the slimmer path.)
param(
    [string]$MoldflowExe = "moldflow",
    [int]$PauseSeconds = 0,
    [switch]$FailFast,
    [switch]$SkipRealSmoke,
    [switch]$SkipProjectSmoke,
    [switch]$SkipSTLWorkflow,

    # After STL analyze_now (solve), poll is_analysis_running until false and wait for result files.
    [int]$AnalysisWaitMaxSeconds = 7200,
    [int]$AnalysisPollSeconds = 5
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$artifactRoot = Join-Path $repoRoot "demo_models"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$artifactDir = Join-Path $artifactRoot "cli_eval_$timestamp"
$script:DescribeCache = @{}
$script:Launcher = $null

function Format-CommandText {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Executable,

        [AllowEmptyCollection()]
        [string[]]$FixedArgs,

        [Parameter(Mandatory = $true)]
        [string[]]$Args
    )

    $parts = @($Executable) + $FixedArgs + $Args
    $renderedParts = $parts | ForEach-Object {
        if ($_ -match '\s') {
            '"{0}"' -f $_
        }
        else {
            $_
        }
    }

    return ($renderedParts -join ' ')
}

function Resolve-CliLauncher {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PreferredExecutable
    )

    $resolvedCli = Get-Command $PreferredExecutable -ErrorAction SilentlyContinue
    if ($null -ne $resolvedCli) {
        return [pscustomobject]@{
            Executable = $resolvedCli.Source
            FixedArgs  = @()
            Label      = $resolvedCli.Source
        }
    }

    $resolvedPython = Get-Command "python" -ErrorAction SilentlyContinue

    if ($null -eq $resolvedPython) {
        throw "Could not find '$PreferredExecutable' or 'python' on PATH."
    }

    return [pscustomobject]@{
        Executable = $resolvedPython.Source
        FixedArgs  = @("-m", "moldflow_cli")
        Label      = "$($resolvedPython.Source) -m moldflow_cli"
    }
}

function Get-OptionalPropertyValue {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Object,

        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    if ($null -eq $Object) {
        return $null
    }

    if ($Object -is [System.Collections.IDictionary]) {
        if ($Object.Contains($Name)) {
            return $Object[$Name]
        }

        return $null
    }

    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) {
        return $null
    }

    return $property.Value
}

function Get-ObjectProperties {
    param(
        [AllowNull()]
        [object]$Object
    )

    if ($null -eq $Object) {
        return @()
    }

    if ($Object -is [System.Collections.IDictionary]) {
        $properties = @()
        foreach ($key in $Object.Keys) {
            $properties += [pscustomobject]@{
                Name  = [string]$key
                Value = $Object[$key]
            }
        }

        return $properties
    }

    return @($Object.PSObject.Properties)
}

function Test-IsEnumerableLike {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Value
    )

    return ($Value -is [System.Collections.IEnumerable]) -and -not ($Value -is [string]) -and -not ($Value -is [System.Collections.IDictionary])
}

function Get-CollectionCount {
    param(
        [AllowNull()]
        [object]$Value
    )

    if ($null -eq $Value) {
        return 0
    }

    if ($Value -is [System.Array]) {
        return $Value.Count
    }

    if ($Value -is [System.Collections.ICollection]) {
        return $Value.Count
    }

    if (Test-IsEnumerableLike -Value $Value) {
        return @($Value).Count
    }

    return 1
}

function Read-TextFileLines {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path $Path)) {
        return @()
    }

    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
    try {
        $reader = New-Object System.IO.StreamReader($stream, [System.Text.Encoding]::UTF8, $true)
        try {
            $text = $reader.ReadToEnd()
        }
        finally {
            $reader.Dispose()
        }
    }
    finally {
        $stream.Dispose()
    }

    if ([string]::IsNullOrEmpty($text)) {
        return @()
    }

    return @($text -split "`r?`n")
}

function Invoke-MoldflowCliCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Title,

        [Parameter(Mandatory = $true)]
        [string[]]$Args,

        [ValidateSet("success", "failure")]
        [string]$ExpectedOutcome = "success",

        [switch]$CaptureTrace,

        [switch]$Quiet
    )

    $safeTitle = (("{0}" -f ($Title -replace '[^A-Za-z0-9]+', '_')).Trim('_'))
    if ([string]::IsNullOrWhiteSpace($safeTitle)) {
        $safeTitle = "cli_step"
    }

    $stdoutPath = Join-Path $artifactDir ("{0}_stdout.log" -f $safeTitle)
    $stderrPath = Join-Path $artifactDir ("{0}_stderr.log" -f $safeTitle)

    if (-not $Quiet) {
        Write-Output ""
        Write-Output "=== $Title ==="
        Write-Output (Format-CommandText -Executable $script:Launcher.Executable -FixedArgs $script:Launcher.FixedArgs -Args $Args)
    }

    if (Test-Path $stdoutPath) {
        Remove-Item -Path $stdoutPath -Force
    }
    if (Test-Path $stderrPath) {
        Remove-Item -Path $stderrPath -Force
    }

    # Use PowerShell's native argv handling rather than Start-Process -ArgumentList.
    # This preserves spaces inside single arguments and raw JSON payloads without
    # re-joining them into a single command line string.
    Push-Location $repoRoot
    try {
        # Wait blocks until the CLI process exits. mesh_now may run for a long time while COM works.
        # analyze_now can return before the solver finishes; the eval script polls is_analysis_running after STL solve.
        & $script:Launcher.Executable @($script:Launcher.FixedArgs + $Args) 1> $stdoutPath 2> $stderrPath
        $exitCode = if ($null -ne $LASTEXITCODE) { [int]$LASTEXITCODE } else { 0 }
    }
    finally {
        Pop-Location
    }

    $stdout = @()
    if (Test-Path $stdoutPath) {
        $stdout = @(Read-TextFileLines -Path $stdoutPath)
    }

    $stderr = @()
    if (Test-Path $stderrPath) {
        $stderr = @(Read-TextFileLines -Path $stderrPath)
    }

    if (-not $Quiet) {
        if (@($stdout).Count -gt 0) {
            $stdout | ForEach-Object { Write-Output $_ }
        }

        if (@($stderr).Count -gt 0) {
            $stderrLabel = if ($CaptureTrace) { "[trace]" } else { "[stderr]" }
            Write-Output $stderrLabel
            $stderr | ForEach-Object { Write-Output $_ }
        }
    }

    $passed = ($ExpectedOutcome -eq "success" -and $exitCode -eq 0) -or ($ExpectedOutcome -eq "failure" -and $exitCode -ne 0)
    $result = [pscustomobject]@{
        Title           = $Title
        Args            = $Args
        ExpectedOutcome = $ExpectedOutcome
        ExitCode        = $exitCode
        Passed          = $passed
        StdOut          = @($stdout)
        StdErr          = @($stderr)
        StdOutPath      = $stdoutPath
        StdErrPath      = $stderrPath
        TracePath       = $stderrPath
    }

    if (-not $Quiet) {
        if ($passed) {
            Write-Output ("[pass] exit code {0}" -f $exitCode)
        }
        else {
            Write-Output ("[fail] expected {0}, got exit code {1}" -f $ExpectedOutcome, $exitCode)
        }
    }

    if ($FailFast -and -not $passed) {
        throw "Step failed: $Title"
    }

    if ($PauseSeconds -gt 0 -and -not $Quiet) {
        Write-Output ("[pause {0}s]" -f $PauseSeconds)
        Start-Sleep -Seconds $PauseSeconds
    }

    return $result
}

function Wait-MoldflowCliAnalysisIdle {
    <#
    .SYNOPSIS
        Poll study_doc.is_analysis_running until false, then wait for result files.

    .NOTES
        Invoke JSON marks ok=false when result is boolean false, so polling uses --no-fail-on-false.
        Set AnalysisWaitMaxSeconds to 0 on the script to skip this wait (not recommended for STL results probes).
    #>
    param(
        [int]$MaxWaitSeconds = 7200,
        [int]$PollSeconds = 5
    )

    if ($MaxWaitSeconds -le 0) {
        Write-Output ""
        Write-Output "=== Wait for analysis (skipped: AnalysisWaitMaxSeconds <= 0) ==="
        return
    }

    $analysisPollArgs = @(
        "invoke",
        "synergy.study_doc.is_analysis_running",
        "--json-output",
        "--no-fail-on-false"
    )
    $resultsPollArgs = @(
        "invoke",
        "synergy.plot_manager.get_number_of_results_files",
        "--json-output",
        "--no-fail-on-false"
    )
    $deadline = (Get-Date).AddSeconds($MaxWaitSeconds)

    Write-Output ""
    Write-Output ("=== Wait for analysis/results (max {0}s, interval {1}s) ===" -f $MaxWaitSeconds, $PollSeconds)

    while ($true) {
        if ((Get-Date) -gt $deadline) {
            throw (
                "Timeout after {0}s: Synergy analysis still reported running (is_analysis_running). " -f $MaxWaitSeconds +
                "Increase -AnalysisWaitMaxSeconds or inspect Synergy."
            )
        }

        $poll = Invoke-MoldflowCliCommand -Title "poll is_analysis_running" -Args $analysisPollArgs -Quiet
        if ($poll.ExitCode -ne 0) {
            throw ("Poll is_analysis_running failed with exit code {0}." -f $poll.ExitCode)
        }

        $raw = ($poll.StdOut -join "").Trim()
        if ([string]::IsNullOrWhiteSpace($raw)) {
            Start-Sleep -Seconds $PollSeconds
            continue
        }

        $envelope = $raw | ConvertFrom-Json
        $running = $envelope.result
        if ($null -eq $running) {
            throw "Poll is_analysis_running: JSON envelope missing 'result'."
        }

        if ($running -eq $false) {
            Write-Output "[pass] analysis idle (is_analysis_running is false)"
            break
        }

        Write-Output ("[wait] analysis running (is_analysis_running=true), sleeping {0}s..." -f $PollSeconds)
        Start-Sleep -Seconds $PollSeconds
    }

    while ($true) {
        if ((Get-Date) -gt $deadline) {
            throw (
                "Timeout after {0}s: result files still unavailable after analysis became idle. " -f $MaxWaitSeconds +
                "Inspect Synergy analysis completion and study results."
            )
        }

        $poll = Invoke-MoldflowCliCommand -Title "poll get_number_of_results_files" -Args $resultsPollArgs -Quiet
        if ($poll.ExitCode -ne 0) {
            throw ("Poll get_number_of_results_files failed with exit code {0}." -f $poll.ExitCode)
        }

        $raw = ($poll.StdOut -join "").Trim()
        if ([string]::IsNullOrWhiteSpace($raw)) {
            Start-Sleep -Seconds $PollSeconds
            continue
        }

        $envelope = $raw | ConvertFrom-Json
        $count = $envelope.result
        if ($null -eq $count) {
            throw "Poll get_number_of_results_files: JSON envelope missing 'result'."
        }

        if ([int]$count -gt 0) {
            Write-Output ("[pass] results ready (get_number_of_results_files={0})" -f $count)
            return
        }

        Write-Output ("[wait] results not ready (get_number_of_results_files={0}), sleeping {1}s..." -f $count, $PollSeconds)
        Start-Sleep -Seconds $PollSeconds
    }
}

function Test-CapturedOutputCompatibility {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Result,

        [Parameter(Mandatory = $true)]
        [string]$Stream,

        [AllowEmptyCollection()]
        [string[]]$ExpectedText = @()
    )

    $streamsToCheck = switch ($Stream) {
        "stdout" { @("stdout") }
        "stderr" { @("stderr") }
        "both" { @("stdout", "stderr") }
        default { throw "Unsupported compatibility stream '$Stream'." }
    }

    foreach ($streamName in $streamsToCheck) {
        $propName = if ($streamName -eq "stdout") { "StdOut" } else { "StdErr" }
        $propObj = $Result.PSObject.Properties[$propName]
        if ($null -eq $propObj) {
            return [pscustomobject]@{
                Passed  = $false
                Message = "Result object missing property '$propName'."
            }
        }
        $lines = @($propObj.Value)
        if (@($lines).Count -eq 0) {
            return [pscustomobject]@{
                Passed  = $false
                Message = "Captured $streamName output was empty."
            }
        }

        $text = ($lines -join "`n")
        if ([regex]::IsMatch($text, '[\u2500-\u257F]')) {
            return [pscustomobject]@{
                Passed  = $false
                Message = "Captured $streamName output still contains Unicode box-drawing characters."
            }
        }

        foreach ($snippet in @($ExpectedText)) {
            if (-not $text.Contains($snippet)) {
                return [pscustomobject]@{
                    Passed  = $false
                    Message = "Captured $streamName output did not include expected text '$snippet'."
                }
            }
        }
    }

    return [pscustomobject]@{
        Passed  = $true
        Message = "Captured $Stream output stayed ASCII-safe."
    }
}

function Convert-StdOutToJson {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Result,

        [Parameter(Mandatory = $true)]
        [string]$Label
    )

    $text = (($Result.StdOut -join "`n").Trim())
    if ([string]::IsNullOrWhiteSpace($text)) {
        throw "No JSON output captured for '$Label'."
    }

    try {
        return $text | ConvertFrom-Json
    }
    catch {
        throw "Failed to parse JSON output for '$Label': $($_.Exception.Message)"
    }
}

function Get-ListPayload {
    $result = Invoke-MoldflowCliCommand -Title "discovery list json" -Args @("list", "--json") -Quiet
    if (-not $result.Passed) {
        throw "Unable to collect CLI target list."
    }

    return @(Convert-StdOutToJson -Result $result -Label "list --json")
}

function Get-DescribePayload {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Target
    )

    if ($script:DescribeCache.ContainsKey($Target)) {
        return $script:DescribeCache[$Target]
    }

    $result = Invoke-MoldflowCliCommand -Title ("discovery describe {0}" -f $Target) -Args @("describe", $Target, "--json") -Quiet
    if (-not $result.Passed) {
        return $null
    }

    $payload = Convert-StdOutToJson -Result $result -Label ("describe {0}" -f $Target)
    $script:DescribeCache[$Target] = $payload
    return $payload
}

function Test-ContainsComplexValue {
    param(
        [AllowNull()]
        [object]$Value
    )

    if ($null -eq $Value) {
        return $false
    }

    if ($Value -is [string] -or $Value -is [ValueType]) {
        return $false
    }

    if ($Value -is [System.Collections.IDictionary]) {
        return $true
    }

    if (@(Get-ObjectProperties -Object $Value).Count -gt 0) {
        return $true
    }

    if (Test-IsEnumerableLike -Value $Value) {
        return $true
    }

    return $false
}

function Test-ExampleMapIsPrimitiveOnly {
    param(
        [AllowNull()]
        [object]$Map
    )

    if ($null -eq $Map) {
        return $false
    }

    $properties = @(Get-ObjectProperties -Object $Map)
    foreach ($property in $properties) {
        if (Test-ContainsComplexValue -Value $property.Value) {
            return $false
        }
    }

    return @($properties).Count -gt 0
}

function Test-ExampleMapHasComplexValues {
    param(
        [AllowNull()]
        [object]$Map
    )

    if ($null -eq $Map) {
        return $false
    }

    foreach ($property in (Get-ObjectProperties -Object $Map)) {
        if (Test-ContainsComplexValue -Value $property.Value) {
            return $true
        }
    }

    return $false
}

function Get-ParamInfoMap {
    param(
        [Parameter(Mandatory = $true)]
        [object]$DescribePayload
    )

    $map = @{}
    $params = Get-OptionalPropertyValue -Object $DescribePayload -Name "params"
    foreach ($param in @($params)) {
        $map[$param.name] = $param
    }

    if (-not $map.ContainsKey("value") -and (Get-OptionalPropertyValue -Object $DescribePayload -Name "mode") -eq "property_assignment") {
        $map["value"] = [pscustomobject]@{
            name       = "value"
            annotation = "str"
        }
    }

    return $map
}

function Get-SampleValue {
    param(
        [string]$Annotation,
        [string]$NameHint,
        [switch]$ForJson
    )

    $annotationText = [string]$Annotation
    $hint = ([string]$NameHint).ToLowerInvariant()

    if ($annotationText -match 'EntList') {
        if ($ForJson) {
            return @{ entity_string = "N1,N2" }
        }

        return "N1,N2"
    }

    if ($annotationText -match 'VectorArray') {
        if ($ForJson) {
            return @{ xyz = @(@(0.0, 0.0, 0.0), @(1.0, 0.0, 0.0)) }
        }

        return "0,0,0;1,0,0"
    }

    if ($annotationText -match 'Vector') {
        if ($ForJson) {
            return @{ xyz = @(0.0, 0.0, 1.0) }
        }

        return "0,0,1"
    }

    if ($annotationText -match 'DoubleArray|IntegerArray|StringArray') {
        if ($ForJson) {
            if ($annotationText -match 'StringArray') {
                return @{ values = @("alpha", "beta") }
            }

            return @{ values = @(1.0, 2.5) }
        }

        if ($annotationText -match 'StringArray') {
            return "alpha,beta"
        }

        return "1.0,2.5"
    }

    if ($annotationText -match 'bool') {
        if ($ForJson) {
            return $true
        }

        return "true"
    }

    if ($annotationText -match 'int') {
        if ($ForJson) {
            return 7
        }

        return "7"
    }

    if ($annotationText -match 'float|double') {
        if ($ForJson) {
            return 1.5
        }

        return "1.5"
    }

    if ($hint -match 'path|file') {
        return "C:/Temp/demo.mfproj"
    }

    if ($hint -match 'plot|dataset|study|project|name|label') {
        return "Demo"
    }

    if ($hint -match 'mesh_type|type') {
        return "3D"
    }

    if ($ForJson) {
        return "demo"
    }

    return "demo"
}

function Resolve-ExampleValue {
    param(
        [Parameter(Mandatory = $true)]
        [AllowNull()]
        [object]$Value,

        [Parameter(Mandatory = $true)]
        [AllowEmptyString()]
        [string]$CurrentKey,

        [Parameter(Mandatory = $true)]
        [hashtable]$ParamInfo,

        [switch]$ForJson
    )

    if ($null -eq $Value) {
        $param = $null
        if ($ParamInfo.ContainsKey($CurrentKey)) {
            $param = $ParamInfo[$CurrentKey]
        }

        $annotation = if ($null -ne $param) { [string](Get-OptionalPropertyValue -Object $param -Name "annotation") } else { "" }
        return Get-SampleValue -Annotation $annotation -NameHint $CurrentKey -ForJson:$ForJson
    }

    if ($Value -is [string]) {
        if ($Value -match '^<([^>]+)>$') {
            $token = $matches[1]
            $param = $null
            if ($ParamInfo.ContainsKey($CurrentKey)) {
                $param = $ParamInfo[$CurrentKey]
            }
            elseif ($ParamInfo.ContainsKey($token)) {
                $param = $ParamInfo[$token]
            }

            $annotation = if ($null -ne $param) { [string](Get-OptionalPropertyValue -Object $param -Name "annotation") } else { "" }
            return Get-SampleValue -Annotation $annotation -NameHint $token -ForJson:$ForJson
        }

        return $Value
    }

    if ($Value -is [System.Collections.IDictionary]) {
        $out = @{}
        foreach ($key in $Value.Keys) {
            $out[$key] = Resolve-ExampleValue -Value $Value[$key] -CurrentKey ([string]$key) -ParamInfo $ParamInfo -ForJson:$ForJson
        }

        return $out
    }

    if (@(Get-ObjectProperties -Object $Value).Count -gt 0 -and -not (Test-IsEnumerableLike -Value $Value)) {
        $out = @{}
        foreach ($property in (Get-ObjectProperties -Object $Value)) {
            $out[$property.Name] = Resolve-ExampleValue -Value $property.Value -CurrentKey $property.Name -ParamInfo $ParamInfo -ForJson:$ForJson
        }

        return $out
    }

    if (Test-IsEnumerableLike -Value $Value) {
        $items = @()
        foreach ($item in $Value) {
            $items += Resolve-ExampleValue -Value $item -CurrentKey $CurrentKey -ParamInfo $ParamInfo -ForJson:$ForJson
        }

        return $items
    }

    return $Value
}

function Get-InvokeCliArgs {
    param(
        [Parameter(Mandatory = $true)]
        [object]$DescribePayload
    )

    $examples = Get-OptionalPropertyValue -Object $DescribePayload -Name "invoke_examples"
    $cliArgs = @(Get-OptionalPropertyValue -Object $examples -Name "cli_args")
    $paramInfo = Get-ParamInfoMap -DescribePayload $DescribePayload
    $resolvedArgs = @()

    foreach ($arg in $cliArgs) {
        if ($arg -match '^(?<name>[^=]+)=(?<value>.*)$') {
            $name = $matches['name']
            $value = $matches['value']
            if ($value -match '^<([^>]+)>$') {
                $token = $matches[1]
                $param = $null
                if ($paramInfo.ContainsKey($name)) {
                    $param = $paramInfo[$name]
                }
                elseif ($paramInfo.ContainsKey($token)) {
                    $param = $paramInfo[$token]
                }

                $annotation = if ($null -ne $param) { [string](Get-OptionalPropertyValue -Object $param -Name "annotation") } else { "" }
                $sample = Get-SampleValue -Annotation $annotation -NameHint $token
                $resolvedArgs += ("{0}={1}" -f $name, $sample)
            }
            else {
                $resolvedArgs += $arg
            }
        }
        else {
            $resolvedArgs += $arg
        }
    }

    return $resolvedArgs
}

function Get-InvokeJsonPayload {
    param(
        [Parameter(Mandatory = $true)]
        [object]$DescribePayload
    )

    $examples = Get-OptionalPropertyValue -Object $DescribePayload -Name "invoke_examples"
    $preferred = Get-OptionalPropertyValue -Object $examples -Name "params_json"
    if ($null -eq $preferred) {
        $preferred = Get-OptionalPropertyValue -Object $DescribePayload -Name "params_json_template"
    }

    $paramInfo = Get-ParamInfoMap -DescribePayload $DescribePayload
    return Resolve-ExampleValue -Value $preferred -CurrentKey "" -ParamInfo $paramInfo -ForJson
}

function ConvertTo-StepPrefixedCliArgs {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Target,

        [Parameter(Mandatory = $true)]
        [string[]]$Args
    )

    $stepName = ($Target -split '\.')[-1].ToUpperInvariant()
    $prefixed = @()
    foreach ($arg in $Args) {
        if ($arg -match '^(?<name>[^=]+)=(?<value>.*)$') {
            $name = $matches['name']
            $value = $matches['value']
            if ($name -match '\.') {
                $prefixed += $arg
            }
            else {
                $prefixed += ("{0}.{1}={2}" -f $stepName, $name, $value)
            }
        }
        else {
            $prefixed += $arg
        }
    }

    return $prefixed
}

function ConvertTo-NestedStepJsonPayload {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Target,

        [Parameter(Mandatory = $true)]
        [object]$Payload
    )

    $stepName = ($Target -split '\.')[-1].ToUpperInvariant()
    return @{ $stepName = $Payload }
}

function New-JsonArtifact {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory = $true)]
        [string]$BaseName,

        [Parameter(Mandatory = $true)]
        [AllowNull()]
        [object]$Payload
    )

    $path = Join-Path $artifactDir ("{0}.json" -f $BaseName)
    $jsonText = $Payload | ConvertTo-Json -Depth 20
    if ($PSCmdlet.ShouldProcess($path, "Create JSON artifact")) {
        Set-Content -Path $path -Value $jsonText -Encoding UTF8
    }
    return $path
}

function Show-JsonArtifactPreview {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string]$Label
    )

    Write-Output ""
    Write-Output ("=== {0} ===" -f $Label)
    Write-Output ("Path: {0}" -f $Path)
    $lines = @(Read-TextFileLines -Path $Path)
    if (@($lines).Count -eq 0) {
        Write-Output "(empty file)"
        return
    }
    $lines | ForEach-Object { Write-Output $_ }
}

function ConvertTo-NativeJsonArgument {
    param(
        [Parameter(Mandatory = $true)]
        [AllowNull()]
        [object]$Payload
    )

    return ($Payload | ConvertTo-Json -Depth 20 -Compress)
}

function ConvertTo-CliPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $full = [System.IO.Path]::GetFullPath($Path)
    return ($full -replace '\\', '/')
}

function New-DemoAsciiStlBox {
    <#
    Writes a watertight axis-aligned box (mm) as ASCII STL for Moldflow import demos.

    Supports -WhatIf / -Confirm via ShouldProcess on the file write. Nested helper uses
    PositionalBinding=$false so static analysis does not treat it as positionally invocable.
    #>
    [CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Low')]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [double]$SizeX = 100.0,
        [double]$SizeY = 60.0,
        [double]$SizeZ = 15.0
    )

    $c = [System.Globalization.CultureInfo]::InvariantCulture
    function LocalFormat([double]$v) { return $v.ToString($c) }

    function Write-StlFacet {
        [CmdletBinding(PositionalBinding = $false)]
        param(
            [Parameter(Mandatory = $true)]
            [System.Text.StringBuilder]$Sb,

            [Parameter(Mandatory = $true)]
            [double]$nx,

            [Parameter(Mandatory = $true)]
            [double]$ny,

            [Parameter(Mandatory = $true)]
            [double]$nz,

            [Parameter(Mandatory = $true)]
            [double[]]$p1,

            [Parameter(Mandatory = $true)]
            [double[]]$p2,

            [Parameter(Mandatory = $true)]
            [double[]]$p3
        )
        [void]$Sb.AppendLine(("  facet normal {0} {1} {2}" -f (LocalFormat $nx), (LocalFormat $ny), (LocalFormat $nz)))
        [void]$Sb.AppendLine("    outer loop")
        [void]$Sb.AppendLine(("      vertex {0} {1} {2}" -f (LocalFormat $p1[0]), (LocalFormat $p1[1]), (LocalFormat $p1[2])))
        [void]$Sb.AppendLine(("      vertex {0} {1} {2}" -f (LocalFormat $p2[0]), (LocalFormat $p2[1]), (LocalFormat $p2[2])))
        [void]$Sb.AppendLine(("      vertex {0} {1} {2}" -f (LocalFormat $p3[0]), (LocalFormat $p3[1]), (LocalFormat $p3[2])))
        [void]$Sb.AppendLine("    endloop")
        [void]$Sb.AppendLine("  endfacet")
    }

    $x0 = 0.0; $x1 = $SizeX
    $y0 = 0.0; $y1 = $SizeY
    $z0 = 0.0; $z1 = $SizeZ

    $b000 = @($x0, $y0, $z0); $b100 = @($x1, $y0, $z0); $b110 = @($x1, $y1, $z0); $b010 = @($x0, $y1, $z0)
    $t000 = @($x0, $y0, $z1); $t100 = @($x1, $y0, $z1); $t110 = @($x1, $y1, $z1); $t010 = @($x0, $y1, $z1)

    $sb = New-Object System.Text.StringBuilder
    [void]$sb.AppendLine("solid moldflow_cli_demo")
    Write-StlFacet -Sb $sb -nx 0 -ny 0 -nz -1 -p1 $b000 -p2 $b110 -p3 $b100
    Write-StlFacet -Sb $sb -nx 0 -ny 0 -nz -1 -p1 $b000 -p2 $b010 -p3 $b110
    Write-StlFacet -Sb $sb -nx 0 -ny 0 -nz 1 -p1 $t000 -p2 $t100 -p3 $t110
    Write-StlFacet -Sb $sb -nx 0 -ny 0 -nz 1 -p1 $t000 -p2 $t110 -p3 $t010
    Write-StlFacet -Sb $sb -nx -1 -ny 0 -nz 0 -p1 $b000 -p2 $t000 -p3 $t010
    Write-StlFacet -Sb $sb -nx -1 -ny 0 -nz 0 -p1 $b000 -p2 $t010 -p3 $b010
    Write-StlFacet -Sb $sb -nx 1 -ny 0 -nz 0 -p1 $b100 -p2 $t110 -p3 $t100
    Write-StlFacet -Sb $sb -nx 1 -ny 0 -nz 0 -p1 $b100 -p2 $b110 -p3 $t110
    Write-StlFacet -Sb $sb -nx 0 -ny -1 -nz 0 -p1 $b000 -p2 $t100 -p3 $t000
    Write-StlFacet -Sb $sb -nx 0 -ny -1 -nz 0 -p1 $b000 -p2 $b100 -p3 $t100
    Write-StlFacet -Sb $sb -nx 0 -ny 1 -nz 0 -p1 $b010 -p2 $t010 -p3 $t110
    Write-StlFacet -Sb $sb -nx 0 -ny 1 -nz 0 -p1 $b010 -p2 $t110 -p3 $b110
    [void]$sb.AppendLine("endsolid moldflow_cli_demo")
    if ($PSCmdlet.ShouldProcess($Path, "Write demo ASCII STL box")) {
        [System.IO.File]::WriteAllText($Path, $sb.ToString(), [System.Text.UTF8Encoding]::new($false))
    }
}

function Find-RepresentativeTarget {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Category,

        [Parameter(Mandatory = $true)]
        [object[]]$Rows,

        [Parameter(Mandatory = $true)]
        [scriptblock]$Predicate,

        [Parameter(Mandatory = $true)]
        [scriptblock]$QuickFilter,

        [string[]]$PreferredTargets = @(),

        [string[]]$UsedTargets = @()
    )

    foreach ($target in $PreferredTargets) {
        $row = $Rows | Where-Object { $_.target -eq $target } | Select-Object -First 1
        if ($null -eq $row) {
            continue
        }

        $describe = Get-DescribePayload -Target $row.target
        if ($null -eq $describe) {
            continue
        }

        if (& $Predicate $row $describe) {
            return [pscustomobject]@{
                Category = $Category
                Row      = $row
                Describe  = $describe
            }
        }
    }

    $candidates = $Rows | Where-Object { (& $QuickFilter $_) -and ($UsedTargets -notcontains $_.target) } | Sort-Object target
    foreach ($row in $candidates) {
        $describe = Get-DescribePayload -Target $row.target
        if ($null -eq $describe) {
            continue
        }

        if (& $Predicate $row $describe) {
            return [pscustomobject]@{
                Category = $Category
                Row      = $row
                Describe  = $describe
            }
        }
    }

    return $null
}

function Add-Case {
    param(
        [AllowEmptyCollection()]
        [System.Collections.Generic.List[object]]$Cases,

        [Parameter(Mandatory = $true)]
        [string]$Group,

        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [string[]]$Args,

        [ValidateSet("success", "failure")]
        [string]$ExpectedOutcome = "success",

        [switch]$CaptureTrace,

        [string]$CompatibilityStream,

        [AllowEmptyCollection()]
        [string[]]$CompatibilityExpectedText = @(),

        [string]$WorkflowPhase = ""
    )

    $null = $Cases.Add([pscustomobject]@{
        WorkflowPhase             = $WorkflowPhase
        Group                     = $Group
        Name                      = $Name
        Args                      = $Args
        ExpectedOutcome           = $ExpectedOutcome
        CaptureTrace              = $CaptureTrace.IsPresent
        CompatibilityStream       = $CompatibilityStream
        CompatibilityExpectedText = @($CompatibilityExpectedText)
    })
}

Push-Location $repoRoot
try {
    # Full import/solve/results path only when Synergy + project lifecycle smoke is active.
    $runSTLWorkflow = -not $SkipSTLWorkflow -and -not $SkipRealSmoke -and -not $SkipProjectSmoke

    $null = New-Item -ItemType Directory -Path $artifactDir -Force

    if ($env:PYTHONPATH) {
        $env:PYTHONPATH = "$repoRoot\src;$($env:PYTHONPATH)"
    }
    else {
        $env:PYTHONPATH = "$repoRoot\src"
    }

    $script:Launcher = Resolve-CliLauncher -PreferredExecutable $MoldflowExe

    Write-Output "Moldflow CLI workflow demo (user-journey order + regression checks)"
    Write-Output "Launcher: $($script:Launcher.Label)"
    Write-Output "Repo source override: $repoRoot\src"
    Write-Output "Artifacts: $artifactDir"
    Write-Output ""
    Write-Output "Story: connect to the CLI, discover targets, document/dry-run typical study work"
    Write-Output "(open/create project, mesh, solver status, loads, plots), then optional live Synergy"
    Write-Output "steps, a batch JSON 'script', and finally intentional error cases."
    if ($runSTLWorkflow) {
        Write-Output "STL workflow (default with live project): demo block STL will be written, imported, analyzed, and result/plot APIs queried."
    }
    elseif (-not $SkipRealSmoke -and -not $SkipProjectSmoke -and $SkipSTLWorkflow) {
        Write-Output "STL workflow skipped (-SkipSTLWorkflow): using mesh_type-only project_live checks."
    }

    $rows = Get-ListPayload
    $usedTargets = @()
    $selectedTargets = @{}

    $selectionSpecs = @(
        @{
            Category         = "zero_arg_method"
            PreferredTargets = @("synergy.study_doc.is_analysis_running", "synergy.study_doc.mesh_status")
            QuickFilter      = { param($row) $row.kind -eq "method" }
            Predicate        = {
                param($row, $describe)
                $row.kind -eq "method" -and (Get-CollectionCount -Value (Get-OptionalPropertyValue -Object $describe -Name "params")) -eq 0 -and $null -eq (Get-OptionalPropertyValue -Object $describe -Name "type")
            }
        },
        @{
            Category         = "primitive_method"
            PreferredTargets = @("synergy.open_project")
            QuickFilter      = { param($row) $row.kind -eq "method" -and $row.target -match '^synergy\.[^.]+$' }
            Predicate        = {
                param($row, $describe)
                $row.kind -eq "method" -and
                (Get-CollectionCount -Value (Get-OptionalPropertyValue -Object $describe -Name "params")) -gt 0 -and
                (Test-ExampleMapIsPrimitiveOnly -Map (Get-OptionalPropertyValue -Object (Get-OptionalPropertyValue -Object $describe -Name "invoke_examples") -Name "params_json"))
            }
        },
        @{
            Category         = "complex_method"
            PreferredTargets = @("synergy.boundary_conditions.create_volume_loads", "boundary_conditions.create_edge_loads")
            QuickFilter      = { param($row) $row.kind -eq "method" }
            Predicate        = {
                param($row, $describe)
                $row.kind -eq "method" -and
                (Get-CollectionCount -Value (Get-OptionalPropertyValue -Object $describe -Name "params")) -gt 0 -and
                (Test-ExampleMapHasComplexValues -Map (Get-OptionalPropertyValue -Object (Get-OptionalPropertyValue -Object $describe -Name "invoke_examples") -Name "params_json"))
            }
        },
        @{
            Category         = "nested_method"
            PreferredTargets = @("synergy.plot_manager.find_plot_by_name")
            QuickFilter      = { param($row) $row.kind -eq "method" -and $row.target -match '^synergy\.[^.]+\.[^.]+$' }
            Predicate        = {
                param($row, $describe)
                $row.kind -eq "method" -and $row.target -match '^synergy\.[^.]+\.[^.]+$' -and (Get-CollectionCount -Value (Get-OptionalPropertyValue -Object $describe -Name "params")) -gt 0
            }
        },
        @{
            Category         = "readonly_property"
            PreferredTargets = @()
            QuickFilter      = { param($row) $row.kind -eq "property" }
            Predicate        = { param($row, $describe) $row.kind -eq "property" }
        },
        @{
            Category         = "settable_property"
            PreferredTargets = @("synergy.study_doc.mesh_type")
            QuickFilter      = { param($row) $row.kind -eq "settable_property" }
            Predicate        = { param($row, $describe) $row.kind -eq "settable_property" }
        }
    )

    foreach ($spec in $selectionSpecs) {
        $selected = Find-RepresentativeTarget -Category $spec.Category -Rows $rows -Predicate $spec.Predicate -QuickFilter $spec.QuickFilter -PreferredTargets $spec.PreferredTargets -UsedTargets $usedTargets
        if ($null -ne $selected) {
            $selectedTargets[$spec.Category] = $selected
            $usedTargets += $selected.Row.target
        }
    }

    Write-Output ""
    Write-Output "Selected representative targets"
    foreach ($category in $selectionSpecs.Category) {
        $selected = Get-OptionalPropertyValue -Object $selectedTargets -Name $category
        if ($null -eq $selected) {
            Write-Output ("- {0}: not found" -f $category)
            continue
        }

        Write-Output ("- {0}: {1}" -f $category, $selected.Row.target)
    }

    $primitive = $selectedTargets["primitive_method"]
    $primitiveTarget = $null
    $primitiveDescribe = $null
    $primitiveCliArgs = $null
    $primitiveJsonPayload = $null
    $primitiveJsonFile = $null
    $primitiveJsonOutFile = $null
    if ($null -ne $primitive) {
        $primitiveTarget = $primitive.Row.target
        $primitiveDescribe = $primitive.Describe
        $primitiveCliArgs = @(Get-InvokeCliArgs -DescribePayload $primitiveDescribe)
        $primitiveJsonPayload = Get-InvokeJsonPayload -DescribePayload $primitiveDescribe
        $primitiveJsonFile = New-JsonArtifact -BaseName "primitive_params" -Payload $primitiveJsonPayload
        $primitiveJsonOutFile = Join-Path $artifactDir "primitive_dry_run.json"
    }

    $complex = $selectedTargets["complex_method"]
    $complexTarget = $null
    $complexDescribe = $null
    $complexCliArgs = $null
    $complexJsonPayload = $null
    $complexJsonFile = $null
    if ($null -ne $complex) {
        $complexTarget = $complex.Row.target
        $complexDescribe = $complex.Describe
        $complexCliArgs = @(Get-InvokeCliArgs -DescribePayload $complexDescribe)
        $complexJsonPayload = Get-InvokeJsonPayload -DescribePayload $complexDescribe
        $complexJsonFile = New-JsonArtifact -BaseName "complex_params" -Payload $complexJsonPayload
    }

    $nested = $selectedTargets["nested_method"]
    $nestedTarget = $null
    $nestedDescribe = $null
    $nestedCliArgs = $null
    $nestedJsonPayload = $null
    $nestedPrefixedCliArgs = $null
    $nestedStepJsonPayload = $null
    if ($null -ne $nested) {
        $nestedTarget = $nested.Row.target
        $nestedDescribe = $nested.Describe
        $nestedCliArgs = @(Get-InvokeCliArgs -DescribePayload $nestedDescribe)
        $nestedJsonPayload = Get-InvokeJsonPayload -DescribePayload $nestedDescribe
        $nestedPrefixedCliArgs = @(ConvertTo-StepPrefixedCliArgs -Target $nestedTarget -Args $nestedCliArgs)
        $nestedStepJsonPayload = ConvertTo-NestedStepJsonPayload -Target $nestedTarget -Payload $nestedJsonPayload
    }

    $probeChainTarget = "synergy.plot_manager.find_plot_by_name.get_probe_plot_probe_line"
    $probeChainDescribe = Get-DescribePayload -Target $probeChainTarget
    $probeChainCliArgs = @(
        "find_plot_by_name.plot_name=My Plot"
        "get_probe_plot_probe_line.index=0"
        "get_probe_plot_probe_line.start_pt.x=0"
        "get_probe_plot_probe_line.start_pt.y=0"
        "get_probe_plot_probe_line.start_pt.z=0"
        "get_probe_plot_probe_line.end_pt.x=10"
        "get_probe_plot_probe_line.end_pt.y=0"
        "get_probe_plot_probe_line.end_pt.z=0"
    )
    $probeChainJsonPayload = @{
        find_plot_by_name = @{
            plot_name = "My Plot"
        }
        get_probe_plot_probe_line = @{
            index    = 0
            start_pt = @{
                x = 0
                y = 0
                z = 0
            }
            end_pt   = @{
                x = 10
                y = 0
                z = 0
            }
        }
    }

    $zeroArg = $selectedTargets["zero_arg_method"]
    $zeroArgTarget = $null
    if ($null -ne $zeroArg) {
        $zeroArgTarget = $zeroArg.Row.target
    }

    $readonlyProperty = $selectedTargets["readonly_property"]
    $readonlyTarget = $null
    if ($null -ne $readonlyProperty) {
        $readonlyTarget = $readonlyProperty.Row.target
    }

    $settableProperty = $selectedTargets["settable_property"]
    $settableTarget = $null
    $settableDescribe = $null
    $settableCliArgs = $null
    $settableJsonPayload = $null
    if ($null -ne $settableProperty) {
        $settableTarget = $settableProperty.Row.target
        $settableDescribe = $settableProperty.Describe
        $settableCliArgs = @(Get-InvokeCliArgs -DescribePayload $settableDescribe)
        $settableJsonPayload = Get-InvokeJsonPayload -DescribePayload $settableDescribe
    }

    $realBatchFile = $null
    $realBatchJsonOut = $null
    if (-not $SkipRealSmoke) {
        $realBatchPayload = @(
            @{ target = "synergy.build" },
            @{ target = "synergy.version" }
        )
        $realBatchFile = New-JsonArtifact -BaseName "real_batch_requests" -Payload $realBatchPayload
        $realBatchJsonOut = Join-Path $artifactDir "real_batch_results.json"
    }

    $batchFile = $null
    $batchJsonOut = $null
    if ($null -ne $primitive -and $null -ne $complex) {
        $batchPayload = @(
            @{
                target = $primitive.Row.target
                args = @(Get-InvokeCliArgs -DescribePayload $primitive.Describe)
            },
            @{
                target = $complex.Row.target
                params_json = (Get-InvokeJsonPayload -DescribePayload $complex.Describe)
            }
        )
        if ($null -ne $settableProperty) {
            $batchPayload += @{
                target = $settableProperty.Row.target
                params_json = (Get-InvokeJsonPayload -DescribePayload $settableProperty.Describe)
            }
        }
        $batchFile = New-JsonArtifact -BaseName "batch_requests" -Payload $batchPayload
        $batchJsonOut = Join-Path $artifactDir "batch_results.json"
    }

    $realProjectName = "CliEval_$timestamp"
    $realStudyName = "CliSmokeStudy"
    $realMeshTypeJson = @{ value = "3D" }

    $wfSession = "1) Session -- help and installed package version"
    $wfDiscover = "2) Discover -- filter list output toward project / mesh / boundary work"
    $wfProjectFile = "3) Project file workflow -- compare new vs open, then describe + dry-run open_project"
    $wfMesh = "4) Study mesh -- mesh_type describe + planned assignment (dry-run)"
    $wfSolver = "5) Solver state -- study_doc probes (multi-describe + is_analysis_running)"
    $wfBC = "6) Boundary loads -- describe BC method + shorthand/JSON dry-runs"
    $wfPlots = "7) Post results -- nested plot_manager targets"
    $wfAppMeta = "8) Read-only app metadata on synergy"
    $wfLive = "9) Live Synergy -- real reads, trace, small property batch"
    $wfProjectLive = "10) Live project -- create project/study, adjust mesh, poll analysis flag"
    $wfSTL = "10b) STL workflow -- import generated solid, solve, inspect results/plot APIs (default; -SkipSTLWorkflow for mesh-only)"
    $wfBatchScript = "11) Automation -- batch JSON script (dry-run, file output, misuse checks)"
    $wfReg = "12) Regression -- invalid flag mixes and hidden targets (expect failures)"

    $cases = New-Object 'System.Collections.Generic.List[object]'

    Add-Case -Cases $cases -Group "session" -Name "root help" -WorkflowPhase $wfSession -Args @("--help") -CompatibilityStream "stdout" -CompatibilityExpectedText @("Options", "Commands")
    Add-Case -Cases $cases -Group "session" -Name "version" -WorkflowPhase $wfSession -Args @("version")

    Add-Case -Cases $cases -Group "discover" -Name "list human filtered open_project" -WorkflowPhase $wfDiscover -Args @("list", "--filter", "synergy.open_project")
    Add-Case -Cases $cases -Group "discover" -Name "list json filtered open_project" -WorkflowPhase $wfDiscover -Args @("list", "--filter", "synergy.open_project", "--json")
    Add-Case -Cases $cases -Group "discover" -Name "list yaml filtered open_project" -WorkflowPhase $wfDiscover -Args @("list", "--filter", "synergy.open_project", "--yaml")
    Add-Case -Cases $cases -Group "discover" -Name "list json mesh and open filters" -WorkflowPhase $wfDiscover -Args @("list", "--json", "-f", "open_project", "-f", "mesh_type")
    Add-Case -Cases $cases -Group "discover" -Name "list json boundary-related filters" -WorkflowPhase $wfDiscover -Args @("list", "--json", "-f", "boundary", "-f", "volume")
    Add-Case -Cases $cases -Group "discover" -Name "list empty filter human" -WorkflowPhase $wfDiscover -Args @("list", "--filter", "definitely_no_such_target")

    if ($null -ne $primitive) {
        Add-Case -Cases $cases -Group "project_io" -Name "workflow describe new_project vs open_project" -WorkflowPhase $wfProjectFile -Args @("describe", "synergy.new_project", "synergy.open_project")
        Add-Case -Cases $cases -Group "project_io" -Name "describe open_project bare target" -WorkflowPhase $wfProjectFile -Args @("describe", "open_project")
        Add-Case -Cases $cases -Group "project_io" -Name "describe open_project mixed case json" -WorkflowPhase $wfProjectFile -Args @("describe", "OPEN_PROJECT", "--json")
        Add-Case -Cases $cases -Group "project_io" -Name "describe open_project human" -WorkflowPhase $wfProjectFile -Args @("describe", $primitiveTarget)
        Add-Case -Cases $cases -Group "project_io" -Name "describe open_project json" -WorkflowPhase $wfProjectFile -Args @("describe", $primitiveTarget, "--json")
        Add-Case -Cases $cases -Group "project_io" -Name "describe open_project yaml" -WorkflowPhase $wfProjectFile -Args @("describe", $primitiveTarget, "--yaml")
        Add-Case -Cases $cases -Group "project_io" -Name "describe open_project schema" -WorkflowPhase $wfProjectFile -Args @("describe", $primitiveTarget, "--schema")

        Add-Case -Cases $cases -Group "project_io" -Name "dry-run open_project bare target" -WorkflowPhase $wfProjectFile -Args (@("invoke", "open_project", "--dry-run") + $primitiveCliArgs)
        Add-Case -Cases $cases -Group "project_io" -Name "dry-run open_project mixed case target" -WorkflowPhase $wfProjectFile -Args (@("invoke", "OPEN_PROJECT", "--dry-run") + $primitiveCliArgs)
        Add-Case -Cases $cases -Group "project_io" -Name "dry-run open_project human" -WorkflowPhase $wfProjectFile -Args (@("invoke", $primitiveTarget, "--dry-run") + $primitiveCliArgs)
        Add-Case -Cases $cases -Group "project_io" -Name "dry-run open_project json alias" -WorkflowPhase $wfProjectFile -Args (@("invoke", $primitiveTarget, "--dry-run", "--json") + $primitiveCliArgs)
        Add-Case -Cases $cases -Group "project_io" -Name "dry-run open_project json-output" -WorkflowPhase $wfProjectFile -Args (@("invoke", $primitiveTarget, "--dry-run", "--json-output") + $primitiveCliArgs)
        Add-Case -Cases $cases -Group "project_io" -Name "dry-run open_project inline params-json" -WorkflowPhase $wfProjectFile -Args @("invoke", $primitiveTarget, "--dry-run", "--params-json", (ConvertTo-NativeJsonArgument -Payload $primitiveJsonPayload))
        Add-Case -Cases $cases -Group "project_io" -Name "dry-run open_project params-json file short -J" -WorkflowPhase $wfProjectFile -Args @("invoke", $primitiveTarget, "--dry-run", "-J", $primitiveJsonFile)
        Add-Case -Cases $cases -Group "project_io" -Name "dry-run open_project params-json file" -WorkflowPhase $wfProjectFile -Args @("invoke", $primitiveTarget, "--dry-run", "--params-json-file", $primitiveJsonFile)
        Add-Case -Cases $cases -Group "project_io" -Name "dry-run open_project json-file-output" -WorkflowPhase $wfProjectFile -Args (@("invoke", $primitiveTarget, "--dry-run", "--json-file-output", $primitiveJsonOutFile) + $primitiveCliArgs)
        Add-Case -Cases $cases -Group "project_io" -Name "dry-run open_project trace" -WorkflowPhase $wfProjectFile -Args (@("invoke", $primitiveTarget, "--dry-run", "--trace", "--json-output") + $primitiveCliArgs) -CaptureTrace
    }

    if ($null -ne $settableProperty) {
        Add-Case -Cases $cases -Group "mesh" -Name "describe mesh_type human" -WorkflowPhase $wfMesh -Args @("describe", $settableTarget)
        Add-Case -Cases $cases -Group "mesh" -Name "describe mesh_type json" -WorkflowPhase $wfMesh -Args @("describe", $settableTarget, "--json")
        Add-Case -Cases $cases -Group "mesh" -Name "dry-run mesh_type args" -WorkflowPhase $wfMesh -Args (@("invoke", $settableTarget, "--dry-run") + $settableCliArgs)
        Add-Case -Cases $cases -Group "mesh" -Name "dry-run mesh_type params-json" -WorkflowPhase $wfMesh -Args @("invoke", $settableTarget, "--dry-run", "--params-json", (ConvertTo-NativeJsonArgument -Payload $settableJsonPayload))
    }

    if ($null -ne $primitive -and $null -ne $zeroArg) {
        Add-Case -Cases $cases -Group "solver" -Name "describe open_project and is_analysis_running json" -WorkflowPhase $wfSolver -Args @("describe", $primitive.Row.target, $zeroArgTarget, "--json")
    }
    if ($null -ne $zeroArg) {
        Add-Case -Cases $cases -Group "solver" -Name "describe is_analysis_running human" -WorkflowPhase $wfSolver -Args @("describe", $zeroArgTarget)
        Add-Case -Cases $cases -Group "solver" -Name "dry-run is_analysis_running human" -WorkflowPhase $wfSolver -Args @("invoke", $zeroArgTarget, "--dry-run")
        Add-Case -Cases $cases -Group "solver" -Name "dry-run is_analysis_running json-output" -WorkflowPhase $wfSolver -Args @("invoke", $zeroArgTarget, "--dry-run", "--json-output")
    }

    if ($null -ne $complex) {
        Add-Case -Cases $cases -Group "loads" -Name "describe create_volume_loads human" -WorkflowPhase $wfBC -Args @("describe", $complexTarget)
        Add-Case -Cases $cases -Group "loads" -Name "describe create_volume_loads json" -WorkflowPhase $wfBC -Args @("describe", $complexTarget, "--json")
        Add-Case -Cases $cases -Group "loads" -Name "dry-run volume loads shorthand" -WorkflowPhase $wfBC -Args (@("invoke", $complexTarget, "--dry-run") + $complexCliArgs)
        Add-Case -Cases $cases -Group "loads" -Name "dry-run volume loads params-json" -WorkflowPhase $wfBC -Args @("invoke", $complexTarget, "--dry-run", "--params-json", (ConvertTo-NativeJsonArgument -Payload $complexJsonPayload))
        Add-Case -Cases $cases -Group "loads" -Name "dry-run volume loads params-json file" -WorkflowPhase $wfBC -Args @("invoke", $complexTarget, "--dry-run", "--params-json-file", $complexJsonFile)
    }

    if ($null -ne $nested) {
        Add-Case -Cases $cases -Group "plots" -Name "describe find_plot_by_name human" -WorkflowPhase $wfPlots -Args @("describe", $nestedTarget)
        Add-Case -Cases $cases -Group "plots" -Name "describe find_plot_by_name json" -WorkflowPhase $wfPlots -Args @("describe", $nestedTarget, "--json")
        Add-Case -Cases $cases -Group "plots" -Name "dry-run find_plot mixed case target" -WorkflowPhase $wfPlots -Args (@("invoke", "PLOT_MANAGER.FIND_PLOT_BY_NAME", "--dry-run") + $nestedCliArgs)
        Add-Case -Cases $cases -Group "plots" -Name "dry-run find_plot direct args" -WorkflowPhase $wfPlots -Args (@("invoke", $nestedTarget, "--dry-run") + $nestedCliArgs)
        Add-Case -Cases $cases -Group "plots" -Name "dry-run find_plot step-prefixed args" -WorkflowPhase $wfPlots -Args (@("invoke", $nestedTarget, "--dry-run") + $nestedPrefixedCliArgs)
        Add-Case -Cases $cases -Group "plots" -Name "dry-run find_plot step json" -WorkflowPhase $wfPlots -Args @("invoke", $nestedTarget, "--dry-run", "--params-json", (ConvertTo-NativeJsonArgument -Payload $nestedStepJsonPayload))
    }
    if ($null -ne $probeChainDescribe) {
        Add-Case -Cases $cases -Group "plots" -Name "dry-run probe plot probe line raw chain args" -WorkflowPhase $wfPlots -Args (@("invoke", $probeChainTarget, "--dry-run") + $probeChainCliArgs)
        Add-Case -Cases $cases -Group "plots" -Name "dry-run probe plot probe line grouped params-json" -WorkflowPhase $wfPlots -Args @("invoke", $probeChainTarget, "--dry-run", "--params-json", (ConvertTo-NativeJsonArgument -Payload $probeChainJsonPayload))
    }

    if ($null -ne $readonlyProperty) {
        Add-Case -Cases $cases -Group "app_meta" -Name "describe build property human" -WorkflowPhase $wfAppMeta -Args @("describe", $readonlyTarget)
        Add-Case -Cases $cases -Group "app_meta" -Name "describe build property json" -WorkflowPhase $wfAppMeta -Args @("describe", $readonlyTarget, "--json")
        Add-Case -Cases $cases -Group "app_meta" -Name "dry-run build property" -WorkflowPhase $wfAppMeta -Args @("invoke", $readonlyTarget, "--dry-run")
    }

    if (-not $SkipRealSmoke) {
        Add-Case -Cases $cases -Group "live" -Name "invoke synergy.build json-output" -WorkflowPhase $wfLive -Args @("invoke", "synergy.build", "--json-output")
        Add-Case -Cases $cases -Group "live" -Name "invoke synergy.version json-output" -WorkflowPhase $wfLive -Args @("invoke", "synergy.version", "--json-output")
        Add-Case -Cases $cases -Group "live" -Name "invoke synergy.build trace json" -WorkflowPhase $wfLive -Args @("invoke", "synergy.build", "--trace", "--json") -CaptureTrace
        Add-Case -Cases $cases -Group "live" -Name "invoke synergy.version no-fail-on-false" -WorkflowPhase $wfLive -Args @("invoke", "synergy.version", "--json-output", "--no-fail-on-false")
        Add-Case -Cases $cases -Group "live" -Name "invoke batch-file build and version json-output" -WorkflowPhase $wfLive -Args @("invoke", "--batch-file", $realBatchFile, "--json-output")
        Add-Case -Cases $cases -Group "live" -Name "invoke batch-file build and version json-file-output" -WorkflowPhase $wfLive -Args @("invoke", "--batch-file", $realBatchFile, "--json-file-output", $realBatchJsonOut)

        if (-not $SkipProjectSmoke) {
            $addFileJsonArg = $null
            if ($runSTLWorkflow) {
                $stlDiskPath = Join-Path $artifactDir "cli_demo_block.stl"
                New-DemoAsciiStlBox -Path $stlDiskPath
                $stlCliPath = ConvertTo-CliPath -Path $stlDiskPath
                Write-Output ""
                Write-Output ("Demo STL (100x60x15 mm box) written to: {0}" -f $stlDiskPath)
                $addFilePayload = @{
                    name      = $stlCliPath
                    show_logs = $false
                    opts      = @{
                        __type__  = "ImportOptions"
                        mesh_type = "3D"
                        mdl_mesh  = $true
                        units     = "mm"
                    }
                }
                $addFileJsonArg = ConvertTo-NativeJsonArgument -Payload $addFilePayload
                # Injection NDBC at top-center of demo box (mm); prop_type = 40000.
                # Vector params use signature coercion - xyz triplets, no __type__ (see describe create_ndbc_at_xyz).
                $injNdbcPayload = @{
                    coord     = @{ xyz = @(50.0, 30.0, 15.0) }
                    normal    = @{ xyz = @(0.0, 0.0, -1.0) }
                    prop_type = 40000
                }
                $injNdbcJsonArg = ConvertTo-NativeJsonArgument -Payload $injNdbcPayload
                $probePlotGetPayload = @{
                    find_plot_by_name         = @{
                        plot_name = "Title:Probe XYPlot"
                    }
                    get_probe_plot_probe_line = @{
                        index    = 1
                        start_pt = @{
                            __type__ = "Vector"
                        }
                        end_pt   = @{
                            __type__ = "Vector"
                        }
                    }
                }
                $probePlotGetJsonArg = ConvertTo-NativeJsonArgument -Payload $probePlotGetPayload
            }

            Add-Case -Cases $cases -Group "project_live" -Name "invoke new_project" -WorkflowPhase $wfProjectLive -Args @("invoke", "synergy.new_project", "name=$realProjectName", "path=$artifactDir", "--json-output")
            Add-Case -Cases $cases -Group "project_live" -Name "invoke project new_study" -WorkflowPhase $wfProjectLive -Args @("invoke", "synergy.project.new_study", "study_name=$realStudyName", "--json-output")

            if ($runSTLWorkflow) {
                Add-Case -Cases $cases -Group "project_live" -Name "stl set mesh_type 3D" -WorkflowPhase $wfSTL -Args @("invoke", "synergy.study_doc.mesh_type", "value=3D", "--json-output")
                Add-Case -Cases $cases -Group "project_live" -Name "stl read analysis_sequence" -WorkflowPhase $wfSTL -Args @("invoke", "synergy.study_doc.analysis_sequence", "--json-output")
                # Read molding process only: new_study already targets thermoplastic injection: setting the property
                # often fails on live Synergy (redundant or study-state guard) and is not required for mesh/solve.
                Add-Case -Cases $cases -Group "project_live" -Name "stl read molding_process" -WorkflowPhase $wfSTL -Args @("invoke", "synergy.study_doc.molding_process", "--json-output")
                Add-Case -Cases $cases -Group "project_live" -Name "stl study_doc add_file" -WorkflowPhase $wfSTL -Args @("invoke", "synergy.study_doc.add_file", "--params-json", $addFileJsonArg, "--json-output")
                # 3D flow needs a volume mesh before placing nodal BCs; runner_generator is not used for this solid import path.
                Add-Case -Cases $cases -Group "project_live" -Name "stl study_doc mesh_now" -WorkflowPhase $wfSTL -Args @("invoke", "synergy.study_doc.mesh_now", "show_prompts=false", "--json-output")

                Add-Case -Cases $cases -Group "project_live" -Name "stl boundary_conditions create_ndbc_at_xyz injection" -WorkflowPhase $wfSTL -Args @("invoke", "synergy.boundary_conditions.create_ndbc_at_xyz", "--params-json", $injNdbcJsonArg, "--json-output")
                Add-Case -Cases $cases -Group "project_live" -Name "stl analyze_now solve" -WorkflowPhase $wfSTL -Args @("invoke", "synergy.study_doc.analyze_now", "check=false", "solve=true", "prompts=false", "--json-output", "--no-fail-on-false")
                Add-Case -Cases $cases -Group "project_live" -Name "stl plot_manager add_default_plots" -WorkflowPhase $wfSTL -Args @("invoke", "synergy.plot_manager.add_default_plots", "--json-output", "--no-fail-on-false")
                Add-Case -Cases $cases -Group "project_live" -Name "stl plot_manager get_number_of_results_files" -WorkflowPhase $wfSTL -Args @("invoke", "synergy.plot_manager.get_number_of_results_files", "--json-output")
                Add-Case -Cases $cases -Group "project_live" -Name "stl plot_manager get_results_file_name index 0" -WorkflowPhase $wfSTL -Args @("invoke", "synergy.plot_manager.get_results_file_name", "index=0", "--json-output")
                Add-Case -Cases $cases -Group "project_live" -Name "stl plot_manager get_first_plot" -WorkflowPhase $wfSTL -Args @("invoke", "synergy.plot_manager.get_first_plot", "--json-output")
                Add-Case -Cases $cases -Group "project_live" -Name "stl delete existing probe xy plot" -WorkflowPhase $wfSTL -Args @(
                    "invoke",
                    "synergy.plot_manager.delete_plot_by_name",
                    "plot_name=Title:Probe XYPlot",
                    "--json-output",
                    "--no-fail-on-false"
                )
                Add-Case -Cases $cases -Group "project_live" -Name "stl create probe xy plot add_probe_plot_probe_line" -WorkflowPhase $wfSTL -Args @(
                    "invoke",
                    "synergy.plot_manager.create_plot_by_ds_id.add_probe_plot_probe_line",
                    "create_plot_by_ds_id.ds_id=1",
                    "create_plot_by_ds_id.plot_type=21",
                    "add_probe_plot_probe_line.start_pt.x=0",
                    "add_probe_plot_probe_line.start_pt.y=0",
                    "add_probe_plot_probe_line.start_pt.z=0",
                    "add_probe_plot_probe_line.end_pt.x=10",
                    "add_probe_plot_probe_line.end_pt.y=0",
                    "add_probe_plot_probe_line.end_pt.z=0",
                    "--json-output"
                )
                Add-Case -Cases $cases -Group "project_live" -Name "stl probe xy plot get_probe_plot_probe_line" -WorkflowPhase $wfSTL -Args @(
                    "invoke",
                    "synergy.plot_manager.find_plot_by_name.get_probe_plot_probe_line",
                    "--params-json",
                    $probePlotGetJsonArg,
                    "--json-output"
                )
            }
            else {
                Add-Case -Cases $cases -Group "project_live" -Name "invoke study_doc mesh_type read" -WorkflowPhase $wfProjectLive -Args @("invoke", "synergy.study_doc.mesh_type", "--json-output")
                Add-Case -Cases $cases -Group "project_live" -Name "invoke study_doc mesh_type set args" -WorkflowPhase $wfProjectLive -Args @("invoke", "synergy.study_doc.mesh_type", "value=3D", "--json-output")
                Add-Case -Cases $cases -Group "project_live" -Name "invoke study_doc mesh_type set params-json" -WorkflowPhase $wfProjectLive -Args @("invoke", "synergy.study_doc.mesh_type", "--params-json", (ConvertTo-NativeJsonArgument -Payload $realMeshTypeJson), "--json-output")
            }

            if ($null -ne $zeroArg) {
                # is_analysis_running returns false when idle; CLI exits 1 on boolean false unless --no-fail-on-false (same as poll loop).
                Add-Case -Cases $cases -Group "project_live" -Name "invoke is_analysis_running after mesh change" -WorkflowPhase $wfProjectLive -Args @("invoke", $zeroArgTarget, "--json-output", "--no-fail-on-false")
            }
        }
    }

    if ($null -ne $batchFile) {
        Add-Case -Cases $cases -Group "batch_script" -Name "invoke batch-file dry-run json-output" -WorkflowPhase $wfBatchScript -Args @("invoke", "--batch-file", $batchFile, "--dry-run", "--json-output")
        Add-Case -Cases $cases -Group "batch_script" -Name "invoke batch-file dry-run json-file-output" -WorkflowPhase $wfBatchScript -Args @("invoke", "--batch-file", $batchFile, "--dry-run", "--json-file-output", $batchJsonOut) -CompatibilityStream "stdout" -CompatibilityExpectedText @("Batch results")
        Add-Case -Cases $cases -Group "batch_script" -Name "invoke batch-file misuse with extra target" -WorkflowPhase $wfBatchScript -Args @("invoke", "synergy.build", "--batch-file", $batchFile) -ExpectedOutcome "failure"
        Add-Case -Cases $cases -Group "batch_script" -Name "invoke batch-file misuse with params-json" -WorkflowPhase $wfBatchScript -Args @("invoke", "--batch-file", $batchFile, "--params-json", (ConvertTo-NativeJsonArgument -Payload @{ value = "demo" })) -ExpectedOutcome "failure"
    }

    Add-Case -Cases $cases -Group "regression" -Name "list json yaml conflict" -WorkflowPhase $wfReg -Args @("list", "--json", "--yaml") -ExpectedOutcome "failure"

    if ($null -ne $primitive) {
        Add-Case -Cases $cases -Group "regression" -Name "describe open_project json yaml conflict" -WorkflowPhase $wfReg -Args @("describe", $primitiveTarget, "--json", "--yaml") -ExpectedOutcome "failure"
        Add-Case -Cases $cases -Group "regression" -Name "describe open_project schema json conflict" -WorkflowPhase $wfReg -Args @("describe", $primitiveTarget, "--schema", "--json") -ExpectedOutcome "failure"
        Add-Case -Cases $cases -Group "regression" -Name "invoke open_project dry-run missing path" -WorkflowPhase $wfReg -Args @("invoke", $primitiveTarget, "--dry-run") -ExpectedOutcome "failure"
        Add-Case -Cases $cases -Group "regression" -Name "invoke open_project dry-run bad params-json" -WorkflowPhase $wfReg -Args @("invoke", $primitiveTarget, "--dry-run", "--params-json", "{bad}") -ExpectedOutcome "failure"
        Add-Case -Cases $cases -Group "regression" -Name "invoke open_project params-json and file both" -WorkflowPhase $wfReg -Args @("invoke", $primitiveTarget, "--dry-run", "--params-json", (ConvertTo-NativeJsonArgument -Payload $primitiveJsonPayload), "--params-json-file", $primitiveJsonFile) -ExpectedOutcome "failure"
        Add-Case -Cases $cases -Group "regression" -Name "invoke open_project params-json and positional" -WorkflowPhase $wfReg -Args @("invoke", $primitiveTarget, "--dry-run", "--params-json", (ConvertTo-NativeJsonArgument -Payload $primitiveJsonPayload), $primitiveCliArgs[0]) -ExpectedOutcome "failure"
        Add-Case -Cases $cases -Group "regression" -Name "invoke open_project removed --template" -WorkflowPhase $wfReg -Args @("invoke", $primitiveTarget, "--template") -ExpectedOutcome "failure"
    }

    $hiddenTarget = "boundary_conditions.create_entity_list"
    Add-Case -Cases $cases -Group "regression" -Name "describe hidden transient wrapper" -WorkflowPhase $wfReg -Args @("describe", $hiddenTarget) -ExpectedOutcome "failure" -CompatibilityStream "stderr" -CompatibilityExpectedText @("Error")

    if (-not $SkipRealSmoke -and -not $SkipProjectSmoke) {
        Add-Case -Cases $cases -Group "project_live" -Name "invoke project close cleanup" -WorkflowPhase $wfProjectLive -Args @("invoke", "synergy.project.close", "prompts=false", "--json-output", "--fail-on-false")
    }

    Write-Output ""
    Write-Output ("Planned cases: {0}" -f $cases.Count)

    if (-not $SkipRealSmoke -and $null -ne $realBatchFile) {
        Write-Output ""
        Write-Output "=== Preview: live Synergy batch (build / version) ==="
        Show-JsonArtifactPreview -Path $realBatchFile -Label "Batch JSON: read synergy.build and synergy.version"
    }
    if ($null -ne $batchFile) {
        Write-Output ""
        Write-Output "=== Preview: automation script (multi-step dry-run batch) ==="
        Show-JsonArtifactPreview -Path $batchFile -Label "Batch JSON: open_project + volume loads (+ mesh when live project enabled)"
    }

    $results = @()
    $currentWorkflowPhase = ""
    $currentGroup = ""
    foreach ($case in $cases) {
        $phase = [string]$case.WorkflowPhase
        if (-not [string]::IsNullOrWhiteSpace($phase) -and $phase -ne $currentWorkflowPhase) {
            $currentWorkflowPhase = $phase
            Write-Output ""
            Write-Output ("** {0}" -f $currentWorkflowPhase)
        }
        if ($case.Group -ne $currentGroup) {
            $currentGroup = $case.Group
            Write-Output ""
            Write-Output ("## {0}" -f $currentGroup.ToUpperInvariant())
        }

        $invocationOutput = @(
            Invoke-MoldflowCliCommand -Title $case.Name -Args $case.Args -ExpectedOutcome $case.ExpectedOutcome -CaptureTrace:$case.CaptureTrace
        )
        foreach ($item in $invocationOutput) {
            if (
                $null -eq $item -or
                ($item.PSObject -and $null -ne $item.PSObject.Properties["Passed"])
            ) {
                continue
            }
            Write-Output $item
        }
        $result = @(
            $invocationOutput |
                Where-Object {
                    $_ -ne $null -and
                    $_.PSObject -and
                    $null -ne $_.PSObject.Properties["Passed"] -and
                    $null -ne $_.PSObject.Properties["StdOut"] -and
                    $null -ne $_.PSObject.Properties["StdErr"]
                }
        )[-1]
        if ($null -eq $result) {
            throw "Invoke-MoldflowCliCommand did not return a structured result object for case '$($case.Name)'."
        }

        Add-Member -InputObject $result -NotePropertyName CompatibilityChecked -NotePropertyValue $false
        Add-Member -InputObject $result -NotePropertyName CompatibilityPassed -NotePropertyValue $null
        Add-Member -InputObject $result -NotePropertyName CompatibilityMessage -NotePropertyValue $null
        Add-Member -InputObject $result -NotePropertyName CompatibilityStream -NotePropertyValue $case.CompatibilityStream

        if (-not [string]::IsNullOrWhiteSpace($case.CompatibilityStream)) {
            $compatibility = Test-CapturedOutputCompatibility -Result $result -Stream $case.CompatibilityStream -ExpectedText $case.CompatibilityExpectedText
            $result.CompatibilityChecked = $true
            $result.CompatibilityPassed = $compatibility.Passed
            $result.CompatibilityMessage = $compatibility.Message

            if ($compatibility.Passed) {
                Write-Output ("[compat] {0}" -f $compatibility.Message)
            }
            else {
                Write-Output ("[compat-fail] {0}" -f $compatibility.Message)
                $result.Passed = $false
                if ($FailFast) {
                    throw "Compatibility check failed: $($case.Name)"
                }
            }
        }

        $results += $result

        if ($case.Name -eq "stl analyze_now solve" -and $result.Passed) {
            Wait-MoldflowCliAnalysisIdle -MaxWaitSeconds $AnalysisWaitMaxSeconds -PollSeconds $AnalysisPollSeconds
        }
    }

    $passedCount = @($results | Where-Object { $_.Passed }).Count
    $failedCount = @($results | Where-Object { -not $_.Passed }).Count

    Write-Output ""
    Write-Output "Summary"
    $results |
        Select-Object Title, ExpectedOutcome, ExitCode, Passed, @{Name = "Compat"; Expression = {
            if (-not $_.CompatibilityChecked) {
                ""
            }
            elseif ($_.CompatibilityPassed) {
                "ascii"
            }
            else {
                "failed"
            }
        }} |
        Format-Table -AutoSize |
        Out-String |
        Write-Output

    $compatibilityResults = @($results | Where-Object { $_.CompatibilityChecked })
    if (@($compatibilityResults).Count -gt 0) {
        Write-Output ""
        Write-Output "Redirected output compatibility"
        $compatibilityResults |
            Select-Object Title, CompatibilityStream, @{Name = "Status"; Expression = {
                if ($_.CompatibilityPassed) {
                    "ascii-safe"
                }
                else {
                    "failed"
                }
            }}, @{Name = "Details"; Expression = { $_.CompatibilityMessage }} |
            Format-Table -Wrap -AutoSize |
            Out-String |
            Write-Output
    }

    Write-Output ("Passed: {0}" -f $passedCount)
    if ($failedCount -gt 0) {
        Write-Output ("Failed: {0}" -f $failedCount)
        $results | Where-Object { -not $_.Passed } | ForEach-Object {
            Write-Output ("- {0}" -f $_.Title)
        }
        throw "CLI surface evaluation completed with failures."
    }

    Write-Output ("Failed: {0}" -f $failedCount)
    Write-Output ""
    Write-Output "Evaluation complete."
}
finally {
    Pop-Location
}
