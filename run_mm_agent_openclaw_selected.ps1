param(
    [string]$Model = "deepseek/deepseek-v4-flash",
    [ValidateSet("off", "minimal", "low", "medium", "high")]
    [string]$Thinking = "high",
    [ValidateRange(1, 86400)]
    [int]$Timeout = 7200,
    [string]$OutputRoot = (Join-Path $PSScriptRoot "output_workspace_mm_agent_openclaw"),
    [string]$OpenClawCommand = "",
    [switch]$SkipJudge,
    [switch]$PrepareOnly
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$problemIds = @(
    "2025_Managing_Sustainable_Tourism"
    "2003_Aviation_Baggage_Screening"
)

$runnerArguments = @(
    "-m"
    "src.OpenClaw.run_mm_agent_baseline"
) + $problemIds + @(
    "--model"
    $Model
    "--thinking"
    $Thinking
    "--timeout"
    $Timeout.ToString()
    "--concurrency"
    $problemIds.Count.ToString()
    "--output-root"
    $OutputRoot
)

if ($OpenClawCommand) {
    $runnerArguments += @("--openclaw-command", $OpenClawCommand)
}
if ($SkipJudge) {
    $runnerArguments += "--skip-judge"
}
if ($PrepareOnly) {
    $runnerArguments += "--prepare-only"
}

Push-Location -LiteralPath $PSScriptRoot
try {
    & python @runnerArguments
    if ($LASTEXITCODE -ne 0) {
        throw "MM-Agent + OpenClaw baseline failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}
