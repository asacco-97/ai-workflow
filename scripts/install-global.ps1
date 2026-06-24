# Install skills, agents, and rules into $HOME\.claude
# Usage: pwsh scripts/install-global.ps1 [-Mode copy|junction]
# Default: copy
#
# junction mode creates directory junctions (Windows equivalent of symlinks
# for folders). Requires no special permissions on most Windows setups.
# File-level junctions are not created — agent .md files are always copied.

param(
    [ValidateSet("copy", "junction")]
    [string]$Mode = "copy"
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path "$PSScriptRoot\..").Path
$ClaudeDir = "$HOME\.claude"

$InstalledSkills = @()
$InstalledAgents = @()
$InstalledRules  = @()

# --- helpers -----------------------------------------------------------------

function Install-Dir($Src, $DestParent, [string]$Name) {
    $dest = Join-Path $DestParent $Name
    if ($Mode -eq "junction") {
        if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
        New-Item -ItemType Junction -Path $dest -Target $Src | Out-Null
    } else {
        if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
        Copy-Item -Path $Src -Destination $dest -Recurse
    }
}

function Install-File($Src, $DestDir) {
    $name = Split-Path $Src -Leaf
    $dest = Join-Path $DestDir $name
    Copy-Item -Path $Src -Destination $dest -Force
}

# --- skills ------------------------------------------------------------------

$SkillsSrc  = Join-Path $RepoRoot "skills"
$SkillsDest = Join-Path $ClaudeDir "skills"

if (Test-Path $SkillsSrc) {
    New-Item -ItemType Directory -Force -Path $SkillsDest | Out-Null
    foreach ($skillDir in (Get-ChildItem $SkillsSrc -Directory)) {
        Install-Dir $skillDir.FullName $SkillsDest $skillDir.Name
        $InstalledSkills += $skillDir.Name
    }
} else {
    Write-Warning "skills/ not found in repo root, skipping."
}

# --- agents ------------------------------------------------------------------

$AgentsSrc  = Join-Path $RepoRoot "agents"
$AgentsDest = Join-Path $ClaudeDir "agents"

if (Test-Path $AgentsSrc) {
    New-Item -ItemType Directory -Force -Path $AgentsDest | Out-Null
    foreach ($agentFile in (Get-ChildItem $AgentsSrc -Filter "*.md")) {
        Install-File $agentFile.FullName $AgentsDest
        $InstalledAgents += $agentFile.Name
    }
} else {
    Write-Warning "agents/ not found in repo root, skipping."
}

# --- rules (recursive, preserves subdirectory structure) ---------------------

$RulesSrc  = Join-Path $RepoRoot "rules"
$RulesDest = Join-Path $ClaudeDir "rules"

if (Test-Path $RulesSrc) {
    $ruleFiles = Get-ChildItem $RulesSrc -Filter "*.md" -Recurse
    if ($ruleFiles.Count -gt 0) {
        New-Item -ItemType Directory -Force -Path $RulesDest | Out-Null
        foreach ($ruleFile in $ruleFiles) {
            $rel = $ruleFile.FullName.Substring($RulesSrc.Length + 1)
            $dest = Join-Path $RulesDest $rel
            $destDir = Split-Path $dest -Parent
            New-Item -ItemType Directory -Force -Path $destDir | Out-Null
            Copy-Item -Path $ruleFile.FullName -Destination $dest -Force
            $InstalledRules += $rel
        }
    }
} else {
    Write-Warning "rules/ not found in repo root, skipping."
}

# --- summary -----------------------------------------------------------------

Write-Host ""
Write-Host "Install complete (mode: $Mode)"
Write-Host ""
Write-Host "Skills  -> $SkillsDest ($($InstalledSkills.Count))"
foreach ($s in $InstalledSkills) { Write-Host "  $s" }

Write-Host ""
Write-Host "Agents  -> $AgentsDest ($($InstalledAgents.Count))"
foreach ($a in $InstalledAgents) { Write-Host "  $a" }

if ($InstalledRules.Count -gt 0) {
    Write-Host ""
    Write-Host "Rules   -> $RulesDest ($($InstalledRules.Count))"
    foreach ($r in $InstalledRules) { Write-Host "  $r" }
}

Write-Host ""
Write-Host "Run 'bash scripts/verify-install.sh' to confirm (or manually check $ClaudeDir)."
