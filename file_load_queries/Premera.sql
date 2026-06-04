SELECT TOP 200 [TapeID], [VolSerNum], [FileName], t.[FileTypeID], f.[FileType], [FileSize], [FileCreateDate], [FileDate], [ProcessStatusID], [DataDescription]
FROM [Premera].[dbo].[tblTape] T (nolock)
JOIN [Premera].[dbo].[tblFileType] F (nolock)
ON t.FileTypeID = f.FileTypeID
--WHERE t.FileTypeID = '38'
ORDER BY TapeID desc

--Expected Monthly Files (2): Claims, Members
--TRGETL3