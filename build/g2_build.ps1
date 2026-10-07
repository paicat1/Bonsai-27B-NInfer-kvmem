$ErrorActionPreference = "Continue"
$vc = "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
if (Test-Path $vc) {
  cmd /c "`"$vc`" >nul 2>&1 && set" | ForEach-Object { if ($_ -match '^([^=]+)=(.*)$') { Set-Item -Path ("env:" + $matches[1]) -Value $matches[2] } }
}
$cmake = "C:\Program Files\CMake\bin\cmake.exe"
$b = "J:\Bonsai\landing\repos\ninfer-4090-windows\_build_5080"
$env:PATH = $b + ";J:\Bonsai\landing\cuda-13.3\bin;" + $env:PATH
Write-Output ("=== G2 BUILD START " + (Get-Date -Format o) + " ===")
& $cmake --build $b --target ninfer_qwen3_6_frontend_test 2>&1
Write-Output ("BUILD_EXIT=" + $LASTEXITCODE)
if ($LASTEXITCODE -eq 0) {
  $exe = Join-Path $b "tests\ninfer_qwen3_6_frontend_test.exe"
  Write-Output "=== G2 RUN TEST ==="
  & $exe 2>&1
  Write-Output ("TEST_EXIT=" + $LASTEXITCODE)
}
Write-Output "=== G2 DONE ==="
