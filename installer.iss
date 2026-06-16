; Script Inno Setup para FirmaDigitalONPECAP
; Descargar Inno Setup: https://jrsoftware.org/isinfo.php
; Compilar: Click derecho > Compile Script

#define MyAppName "Firma Digital ONPE"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Demo"
#define MyAppExeName "FirmaDigitalONPECAP.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\FirmaDigitalONPECAP
DefaultGroupName={#MyAppName}
OutputDir=installer
OutputBaseFilename=FirmaDigitalONPECAP_Installer
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
LicenseFile=
SetupIconFile=assets\images\Icon11.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Archivos principales
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Assets
Source: "assets\images\Icon11.ico"; DestDir: "{app}\assets\images"; Flags: ignoreversion
Source: "assets\images\1.png"; DestDir: "{app}\assets\images"; Flags: ignoreversion
Source: "assets\images\sello_small.png"; DestDir: "{app}\assets\images"; Flags: ignoreversion
Source: "assets\images\sello_base.png"; DestDir: "{app}\assets\images"; Flags: ignoreversion
Source: "assets\icons\*"; DestDir: "{app}\assets\icons"; Flags: ignoreversion
Source: "assets\fonts\fa-solid-900.ttf"; DestDir: "{app}\assets\fonts"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Ejecutar {#MyAppName}"; Flags: nowait postinstall skipifsilent
