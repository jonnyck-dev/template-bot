param(
    [Parameter(Mandatory=$true)][string]$RepoName,
    [string]$Description = "Repository created via opencode",
    [bool]$Private = $false
)

$token = $env:GITHUB_TOKEN
if (-not $token) {
    Write-Error "Error: GITHUB_TOKEN no esta definido en las variables de entorno."
    exit 1
}

$body = @{
    name        = $RepoName
    description = $Description
    private     = $Private
} | ConvertTo-Json

$headers = @{
    Authorization = "Bearer $token"
    Accept        = "application/vnd.github+json"
}

try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $headers -Body $body -ContentType "application/json"
    Write-Host "Success: Repositorio '$RepoName' creado en GitHub."
    Write-Host $response.clone_url
} catch {
    Write-Error "Error: No se pudo crear el repositorio."
    Write-Error $_.Exception.Message
    exit 1
}