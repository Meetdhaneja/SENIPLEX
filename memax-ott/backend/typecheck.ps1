Param(
  [switch]$Watch
)

$ErrorActionPreference = "Stop"

$root = (Resolve-Path (Join-Path $PSScriptRoot "..\\..")).Path
$config = Join-Path $root "pyrightconfig.json"
$py = Join-Path $PSScriptRoot "venv\\Scripts\\python.exe"

if (!(Test-Path -LiteralPath $py)) {
  throw "Virtualenv python not found at: $py"
}
if (!(Test-Path -LiteralPath $config)) {
  throw "pyrightconfig.json not found at: $config"
}

if ($Watch) {
  & $py -m basedpyright --project $config --watch
} else {
  & $py -m basedpyright --project $config
}

