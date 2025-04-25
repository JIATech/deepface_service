param (
    [Parameter(Mandatory=$true)]
    [string]$referencePath,
    
    [Parameter(Mandatory=$true)]
    [string]$comparePath,
    
    [string]$serverUrl = "http://localhost:7424"
)

Write-Host "Verificando servicio facial con curl" -ForegroundColor Cyan
Write-Host "Imagen de referencia: $referencePath"
Write-Host "Imagen a comparar: $comparePath"
Write-Host "URL del servidor: $serverUrl"

# Verificar si los archivos existen
if (-not (Test-Path $referencePath)) {
    Write-Host "Error: El archivo de referencia $referencePath no existe" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $comparePath)) {
    Write-Host "Error: El archivo a comparar $comparePath no existe" -ForegroundColor Red
    exit 1
}

# Comprobar si el servicio está disponible
Write-Host "`nVerificando disponibilidad del servicio..." -ForegroundColor Yellow
$maxRetries = 10
$retryCount = 0
$retryInterval = 3

while ($retryCount -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "$serverUrl/health" -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "Servicio disponible y funcionando correctamente." -ForegroundColor Green
            break
        }
    }
    catch {
        $intentoActual = $retryCount + 1
        Write-Host "Intento $intentoActual de $maxRetries`: Servicio no disponible" -ForegroundColor Yellow
    }
    
    $retryCount++
    if ($retryCount -eq $maxRetries) {
        Write-Host "El servicio no está disponible después de $maxRetries intentos." -ForegroundColor Red
        exit 1
    }
    
    Start-Sleep -Seconds $retryInterval
}

# Codificar imágenes en base64
Write-Host "`nCodificando imágenes..." -ForegroundColor Yellow
$referenceBytes = [System.IO.File]::ReadAllBytes($referencePath)
$referenceBase64 = [System.Convert]::ToBase64String($referenceBytes)

$compareBytes = [System.IO.File]::ReadAllBytes($comparePath)
$compareBase64 = [System.Convert]::ToBase64String($compareBytes)

# Crear el payload JSON
$payload = @{
    reference_image = $referenceBase64
    compare_image = $compareBase64
} | ConvertTo-Json

# Guardar el payload en un archivo temporal
$tempFile = [System.IO.Path]::GetTempFileName()
Set-Content -Path $tempFile -Value $payload -Encoding UTF8

# Realizar la solicitud con Invoke-WebRequest
Write-Host "`nEnviando solicitud al servicio..." -ForegroundColor Yellow

try {
    $headers = @{"Content-Type" = "application/json"}
    $response = Invoke-WebRequest -Uri "$serverUrl/verify" -Method POST -Headers $headers -Body $payload -TimeoutSec 120
    $result = $response.Content
    
    # Eliminar el archivo temporal
    Remove-Item -Path $tempFile -Force
    
    # Mostrar el resultado
    Write-Host "`nResultado de la verificación:" -ForegroundColor Green
    $jsonResult = $result | ConvertFrom-Json
}
catch {
    Write-Host "`nError al enviar la solicitud: $_" -ForegroundColor Red
    # Eliminar el archivo temporal
    Remove-Item -Path $tempFile -Force
    exit 1
}

Write-Host "Verificado: $($jsonResult.verified)"
Write-Host "Similitud: $($jsonResult.similarity)"

# Mostrar tiempo de procesamiento si está disponible
if ($jsonResult.process_time_seconds) {
    Write-Host "Tiempo de procesamiento: $($jsonResult.process_time_seconds) segundos" -ForegroundColor Cyan
}

# Devolver el resultado
return $jsonResult
