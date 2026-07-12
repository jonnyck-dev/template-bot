---
name: github-manager
description: Gestiona repositorios de GitHub: crear nuevos repos y pushear cambios. Usa GITHUB_TOKEN para autenticacion. Compatible con Windows/opencode.
---

# GitHub Manager (Windows)

Gestiona repositorios de GitHub usando la API de GitHub y comandos git desde PowerShell.

## Prerrequisitos

- **GITHUB_TOKEN**: Variable de entorno con un Personal Access Token.
- **GitHub Username**: `jonnyck-dev`

## Flujos de trabajo

### 1. Actualizar un proyecto existente

1. Verificar cambios: `git status`
2. Agregar cambios: `git add -A`
3. Commit: `git commit -m "mensaje"`
4. Push usando el token (sin guardarlo en el remote):
   ```powershell
   git push https://jonnyck-dev:$env:GITHUB_TOKEN@github.com/jonnyck-dev/<repo>.git
   ```

### 2. Crear un nuevo repositorio

1. Inicializar git local: `git init`
2. Crear el remote en GitHub con el script:
   ```powershell
   .\scripts\create_repo.ps1 <repo_name> "<description>" <$true|$false>
   ```
3. Vincular y pushear:
   ```powershell
   git remote add origin <clone_url>
   git branch -M main
   git push -u https://jonnyck-dev:$env:GITHUB_TOKEN@github.com/jonnyck-dev/<repo>.git main
   ```

## Notas de seguridad

- Nunca imprimir el `GITHUB_TOKEN` en la terminal.
- Preferir usar el token solo en el comando `git push` en lugar de guardarlo en `.git/config`.
- Si es necesario agregar un remote con token, advertir al usuario.