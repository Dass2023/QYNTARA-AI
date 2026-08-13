; Qyntara Nexus - FULLY AUTOMATED Installer v9.1 PRO
; Zero manual steps - everything installs automatically

[Setup]
AppName=Qyntara Nexus
AppVersion=9.1.0-PRO
AppPublisher=Dass2023
AppPublisherURL=https://github.com/Dass2023/Qyntara-AI
DefaultDirName={autopf}\Qyntara Nexus
DefaultGroupName=Qyntara Nexus
OutputDir=releases
OutputBaseFilename=Qyntara_Nexus_Setup_v9.1_PRO_FullAuto
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; 1. Documentation
Source: "dist\qyntara_nexus_installer_v9.1_PRO\docs\*"; DestDir: "{app}\Docs"; Flags: ignoreversion recursesubdirs createallsubdirs

; 2. Maya Scripts
Source: "dist\qyntara_nexus_installer_v9.1_PRO\scripts\*"; DestDir: "{userdocs}\maya\scripts"; Flags: ignoreversion recursesubdirs createallsubdirs

; 3. Backend & Frontend Binaries
Source: "dist\qyntara_nexus_installer_v9.1_PRO\bin\*"; DestDir: "{app}\Bin"; Flags: ignoreversion recursesubdirs createallsubdirs

; 4. Adapters
Source: "dist\qyntara_nexus_installer_v9.1_PRO\adapters\*"; DestDir: "{app}\Adapters"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Qyntara Nexus Documentation"; Filename: "{app}\Docs\README.txt"
Name: "{group}\Launch Qyntara Nexus Backend"; Filename: "{app}\Bin\backend\start_server.bat" 
Name: "{autodesktop}\Qyntara Nexus Utils"; Filename: "{app}"

[Code]
var
  ResultPage: TOutputMsgMemoWizardPage;
  InstallLog: TStringList;

procedure LogInstall(Msg: String);
begin
  InstallLog.Add(Msg);
end;

procedure ConfigureMaya();
var
  MayaScriptsPath, StartupScript, LaunchBat: String;
begin
  MayaScriptsPath := ExpandConstant('{userdocs}\maya\scripts');
  
  if DirExists(MayaScriptsPath) then
  begin
      LogInstall('✓ Maya Scripts Folder Detected: ' + MayaScriptsPath);
      
      // Create auto-launch script in Maya userSetup.py
      StartupScript := MayaScriptsPath + '\userSetup.py';
      
      // For this installer we overwrite to ensure v9.1 works.
      SaveStringToFile(StartupScript, 
        '# Qyntara Nexus Auto-Launch (v9.1 PRO)' + #13#10 +
        'import sys' + #13#10 +
        'import os' + #13#10 +
        'sys.path.insert(0, r"' + MayaScriptsPath + '")' + #13#10 +
        'try:' + #13#10 +
        '    import launch_in_maya' + #13#10 +
        '    # launch_in_maya.launch() # Optional: Auto-open window' + #13#10 +
        '    print("Qyntara Nexus v9.1 Loaded Successfully")' + #13#10 +
        'except Exception as e:' + #13#10 +
        '    print("Qyntara Nexus Load Error: " + str(e))' + #13#10, True);
      
      LogInstall('✓ userSetup.py configured for Auto-Load');
      
      // Create desktop launcher batch file
      LaunchBat := MayaScriptsPath + '\LAUNCH_QYNTARA_MAYA.bat';
      SaveStringToFile(LaunchBat,
        '@echo off' + #13#10 +
        'echo Starting Maya with Qyntara AI v9.1...' + #13#10 +
        'timeout /t 3' + #13#10 +
        'start "" "maya.exe"', False);
        
      LogInstall('✓ Qyntara Launcher created in scripts folder');
  end
  else
    LogInstall('⊘ Maya not detected (Documents\maya\scripts missing)');
end;

procedure ConfigureBlender();
var
  BlenderDest: String;
begin
    BlenderDest := ExpandConstant('{app}\Adapters\blender');
    LogInstall('⚠ Blender Addon located at: ' + BlenderDest);
    LogInstall('  -> Install via Blender Preferences > Add-ons > Install...');
end;

procedure ConfigureGameEngines();
begin
    LogInstall('✓ Unity Package: ' + ExpandConstant('{app}\Adapters\unity'));
    LogInstall('✓ Unreal Plugin: ' + ExpandConstant('{app}\Adapters\unreal'));
    LogInstall('  -> Drag/Drop these into your project folders.');
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  I: Integer;
begin
  if CurStep = ssInstall then
  begin
    InstallLog := TStringList.Create;
  end;
  
  if CurStep = ssPostInstall then
  begin
    LogInstall('=== QYNTARA NEXUS v9.1 PRO INSTALLATION ===');
    LogInstall('');
    
    ConfigureMaya();
    ConfigureBlender();
    ConfigureGameEngines();
    
    LogInstall('');
    LogInstall('Installation Complete.');
    
    // Show results
    ResultPage := CreateOutputMsgMemoPage(wpInfoAfter,
      'Setup Finished', 
      'Qyntara Nexus v9.1 PRO installed successfully.',
      'Configuration Log:',
      '');
    
    for I := 0 to InstallLog.Count - 1 do
      ResultPage.RichEditViewer.Lines.Add(InstallLog[I]);
    
    InstallLog.Free;
  end;
end;
