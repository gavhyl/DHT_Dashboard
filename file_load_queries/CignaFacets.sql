SELECT TOP 200 [TapeID], [VolSerNum], [FileName], t.[FileTypeID], f.[FileType], [FileSize], [FileCreateDate], [FileDate], [ProcessStatusID], [DataDescription]
FROM [CignaFacets].[dbo].[tblTape] T (nolock)
JOIN [CignaFacets].[dbo].[tblFileType] F (nolock)
ON t.FileTypeID = f.FileTypeID
ORDER BY TapeID desc

--Expected Weekly Files (2): Claims, CAQH
--TRGETL1