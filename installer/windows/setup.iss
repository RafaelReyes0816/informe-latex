; Inno Setup script for md2tex
; Run with: iscc installer\windows\setup.iss

#define MyAppName "md2tex"
#define MyAppVersion GetEnv('MD2TEX_VERSION')
#ifndef MyAppVersion
  #define MyAppVersion "0.1.0"
#endif
#define MyAppPublisher "Rafael Reyes"
#define MyAppURL "https://github.com/RafaelReyes0816/informe-latex"
#define MyAppExeName "md2tex-windows.exe"
#define MyAppCliExeName "md2tex-windows-cli.exe"

[Setup]
AppId={{B8F4A3E1-2C5D-4A7F-9E6B-1D3C5F8A2E4B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=..\..\dist
OutputBaseFilename=md2tex-setup-v{#MyAppVersion}
SetupIconFile=..\..\installer\icons\md2tex.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
Source: "..\..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\dist\{#MyAppCliExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\installer\icons\md2tex.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\md2tex"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\md2tex.ico"
Name: "{group}\md2tex (CLI)"; Filename: "{app}\{#MyAppCliExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\md2tex.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\md2tex"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\md2tex.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
