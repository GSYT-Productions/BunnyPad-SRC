; Script for BunnyPad v11-FPL1 Installer
#define MyAppName "BunnyPad"
#define MyAppVersion "11.1"
#define MyAppPublisher "GSYT Productions"
#define MyAppURL "https://teknixstuff.com/Network/Donate/"
#define MyAppExeName "BunnyPad.exe"

[Setup]
AppId={{GENERATE-YOUR-OWN-GUID}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=C:\BunnyPad\InstallerOutput
OutputBaseFilename=BunnyPad-PyQt5-v11FPL1
SolidCompression=yes
WizardStyle=modern
LicenseFile="C:\BunnyPad\v11-FPL1\Qt5\License.txt"
InfoBeforeFile="C:\BunnyPad\v11-FPL1\Qt5\InfoBefore.txt"
Compression=lzma
DisableDirPage=auto
DisableProgramGroupPage=auto
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Main executable
Source: "C:\BunnyPad\v11-FPL1\Qt5\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Assets folder
Source: "C:\BunnyPad\v11-FPL1\Qt5\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\BunnyPad\v11-FPL1\Qt5\NOTICE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\BunnyPad\v11-FPL1\Qt5\License.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\BunnyPad\v11-FPL1\Qt5\InfoBefore.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "{#MyAppURL}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Display post-install message
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox(
      'Thank you for installing BunnyPad v11-FPL1!' + #13#10#13#10 +
      'BunnyPad now supports per-user customization of themes.' + #13#10 +
      'You can edit your theme by modifying:' + #13#10 +
      '   %USERPROFILE%\.bunnypad\assets\qss\stylesheet.qss' + #13#10#13#10 +
      'To reset to the default theme, delete or rename the ".bunnypad" folder in your user directory.' + #13#10#13#10 +
      'Support Tech Stuff, a recurring contributor to BunnyPad who makes awesome projects:' + #13#10 +
      'https://teknixstuff.com/Network/Donate/',
      mbInformation, MB_OK
    );
  end;
end;

