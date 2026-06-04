SELECT TOP 200 [TapeID], [VolSerNum], [FileName], t.[FileTypeID], f.[FileType], [FileSize], [FileCreateDate], [FileDate], [ProcessStatusID], [DataDescription]
FROM [BCBSNC_Rx].[dbo].[tblTape] T (nolock)
JOIN [BCBSNC_Rx].[dbo].[tblFileType] F (nolock)
ON t.FileTypeID = f.FileTypeID
--WHERE t.FileTypeID in (5,6,7,8) and [FileName] like '%260315%'
ORDER BY TapeID desc