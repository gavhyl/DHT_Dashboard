SELECT TOP 200 [TapeID], [VolSerNum], [FileName], t.[FileTypeID], f.[FileType], [FileSize], [FileCreateDate], [FileDate], [ProcessStatusID], [DataDescription]
FROM [HMSA_Rx].[dbo].[tblTape] T (nolock)
JOIN [HMSA_Rx].[dbo].[tblFileType] F (nolock)
ON t.FileTypeID = f.FileTypeID
ORDER BY TapeID desc