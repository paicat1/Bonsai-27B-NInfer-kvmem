$ErrorActionPreference = "Continue"
$vc = "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
if (Test-Path $vc) {
  cmd /c "`"$vc`" >nul 2>&1 && set" | ForEach-Object { if ($_ -match '^([^=]+)=(.*)$') { Set-Item -Path ("env:" + $matches[1]) -Value $matches[2] } }
}
$cmake = "C:\Program Files\CMake\bin\cmake.exe"
$b = "J:\Bonsai\landing\repos\ninfer-4090-windows\_build_5080"
Write-Output ("=== BUILD START " + (Get-Date -Format o) + " ===")
& $cmake --build $b --target ninfer_qwen3_6_frontend_test 2>&1
$be = $LASTEXITCODE
Write-Output ("BUILD_EXIT=" + $be)
if ($be -eq 0) {
  $exe = Join-Path $b "tests\ninfer_qwen3_6_frontend_test.exe"
  Write-Output ("=== RUN TEST " + $exe + " ===")
  if (Test-Path $exe) { & $exe 2>&1; Write-Output ("TEST_EXIT=" + $LASTEXITCODE) }
  else { Write-Output "TEST_EXE_NOT_FOUND" }
}
Write-Output ("=== DONE " + (Get-Date -Format o) + " ===")
