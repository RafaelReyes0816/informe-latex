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
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
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

[Code]
const
  // Update this URL when MiKTeX publishes a new basic installer version.
  // Check https://miktex.org/download for the latest "Installer" link.
  MiKTeXUrl = 'https://miktex.org/download/ctan/systems/win32/miktex/setup/windows-x64/basic-miktex-25.12-x64.exe';

function LatexmkAvailable(): Boolean;
var
  ResultCode: Integer;
begin
  Result := False;
  if Exec('cmd.exe', '/c latexmk --version >nul 2>&1', '', SW_HIDE,
      ewWaitUntilTerminated, ResultCode) then
  begin
    Result := (ResultCode = 0);
  end;
end;

function DownloadFile(const Url, Dest: string): Boolean;
var
  ResultCode: Integer;
  PS: string;
begin
  Result := False;
  // PowerShell is present on all supported Windows versions and avoids a
  // dependency on urlmon.dll (which may be missing on stripped Windows
  // builds like Tiny11 / Ghost Spectre).
  PS := '-NoProfile -ExecutionPolicy Bypass -Command "' +
        '$ProgressPreference=''SilentlyContinue''; ' +
        'try { Invoke-WebRequest -UseBasicParsing -Uri ''' + Url +
        ''' -OutFile ''' + Dest +
        ''' -TimeoutSec 300; exit 0 } catch { exit 1 }"';
  if Exec('powershell.exe', PS, '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    Result := (ResultCode = 0) and FileExists(Dest);
  end;
end;

function InstallMiKTeX(): Boolean;
var
  InstallResultCode: Integer;
  InstallerPath: string;
begin
  Result := False;
  InstallerPath := ExpandConstant('{tmp}\basic-miktex-x64.exe');

  if not FileExists(InstallerPath) then
  begin
    MsgBox('Downloading MiKTeX Basic (~150 MB). This can take a few minutes...',
           mbInformation, MB_OK);
    if not DownloadFile(MiKTeXUrl, InstallerPath) then
    begin
      MsgBox('Failed to download MiKTeX.' + #13#10 +
             'You can install it later from https://miktex.org/download',
             mbError, MB_OK);
      Exit;
    end;
  end;

  MsgBox('Installing MiKTeX. Please wait...', mbInformation, MB_OK);
  if Exec(InstallerPath, '--unattended --private', '', SW_SHOW,
      ewWaitUntilTerminated, InstallResultCode) then
  begin
    Result := (InstallResultCode = 0) or LatexmkAvailable();
  end;

  if not Result then
  begin
    MsgBox('MiKTeX installation did not complete successfully.' + #13#10 +
           'You can install it manually from https://miktex.org/download',
           mbError, MB_OK);
  end;
end;

function PerlAvailable(): Boolean;
var
  ResultCode: Integer;
begin
  Result := False;
  if Exec('cmd.exe', '/c perl --version >nul 2>&1', '', SW_HIDE,
      ewWaitUntilTerminated, ResultCode) then
  begin
    Result := (ResultCode = 0);
  end;
end;

function InitializeSetup(): Boolean;
begin
  if not LatexmkAvailable() then
  begin
    if MsgBox('md2tex needs a LaTeX distribution (MiKTeX) to compile PDFs, ' +
              'but it was not found on this system.' + #13#10 + #13#10 +
              'Do you want to download and install MiKTeX Basic now? (~150 MB)',
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      InstallMiKTeX();
    end;
  end;
  // latexmk needs a Perl interpreter. If a LaTeX distribution is now
  // present but Perl is missing, alert the user (avoids the cryptic
  // "MiKTeX could not find the script engine 'perl'" at compile time).
  if LatexmkAvailable() and not PerlAvailable() then
  begin
    MsgBox('LaTeX was detected, but md2tex also needs Perl to run latexmk.' + #13#10 +
           'Without it, PDF compilation will fail.' + #13#10 + #13#10 +
           'Install Strawberry Perl: https://strawberryperl.com' + #13#10 + #13#10 +
           'Click OK to open the download page, or install it later.',
           mbConfirmation, MB_OKCANCEL) = IDOK then
    begin
      ShellExec('open', 'https://strawberryperl.com', '', '', SW_SHOW, ewNoWait, ResultCode);
    end;
  end;
  Result := True;
end;
