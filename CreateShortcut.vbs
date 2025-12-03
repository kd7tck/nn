Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = oWS.SpecialFolders("Desktop") & "\\${PROJECT_NAME}.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
    oLink.TargetPath = WScript.Arguments.Item(0)
    oLink.Save

' Create a subfolder in the Start Menu
Set fso = CreateObject("Scripting.FileSystemObject")
sProgramsFolder = oWS.SpecialFolders("Programs")
sAppFolder = sProgramsFolder & "\\${PROJECT_NAME}"

If Not fso.FolderExists(sAppFolder) Then
    fso.CreateFolder sAppFolder
End If

sLinkFile = sAppFolder & "\\${PROJECT_NAME}.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
    oLink.TargetPath = WScript.Arguments.Item(0)
    oLink.Save
