SELECT TOP 200 [TapeID], [VolSerNum], [FileName], t.[FileTypeID], f.[FileType], [FileSize], [FileCreateDate], [FileDate], [ProcessStatusID], [DataDescription]
FROM [Chickering].[dbo].[tblTape] T (nolock)
JOIN [Chickering].[dbo].[tblFileType] F (nolock)
ON t.FileTypeID = f.FileTypeID
ORDER BY TapeID desc

---------------------------------------------------------------

--Expected Daily Files (2): Claims, Eligibility 
--TRGETL4