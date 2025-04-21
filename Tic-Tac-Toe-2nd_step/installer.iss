[Setup]
AppName=Tic Tac Toe 2.0
AppVersion=1.0
DefaultDirName={userappdata}\Tic Tac Toe
DefaultGroupName=Tic Tac Toe
OutputDir=.
OutputBaseFilename=TicTacToeInstaller
Compression=lzma
SolidCompression=yes
SetupIconFile=Tic Tac Toe 2.0.ico
VersionInfoVersion=1.0.0.0
VersionInfoCompany=Stoshka
VersionInfoDescription=Made by Stoshka
VersionInfoProductName=Tic Tac Toe 2.0

[Files]
Source: "Tic Tac Toe 2.0.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "background.mp3"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Tic Tac Toe 2.0"; Filename: "{app}\Tic Tac Toe 2.0.exe"; IconFilename: "{app}\Tic Tac Toe 2.0.exe"
Name: "{userdesktop}\Tic Tac Toe 2.0"; Filename: "{app}\Tic Tac Toe 2.0.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"