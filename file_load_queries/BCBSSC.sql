SELECT TOP 200 [TapeID], [VolSerNum], [FileName], t.[FileTypeID], f.[FileType], [FileSize], [FileCreateDate], [FileDate], [ProcessStatusID], [DataDescription]
FROM [BCBSSC].[dbo].[tblTape] T (nolock)
JOIN [BCBSSC].[dbo].[tblFileType] F (nolock)
ON t.FileTypeID = f.FileTypeID
ORDER BY TapeID desc

--MONTHLY TOTAL