SELECT TOP 200 [TapeID], [VolSerNum], [FileName], t.[FileTypeID], f.[FileType], [FileSize], [FileCreateDate], [FileDate], [ProcessStatusID], [DataDescription]
FROM [Centene].[dbo].[tblTape] T (nolock)
JOIN [Centene].[dbo].[tblFileType] F (nolock)
ON t.FileTypeID = f.FileTypeID
--WHERE t.FileTypeID IN (1,3,9)
--WHERE FileName like '%code%'
ORDER BY TapeID desc

--Expected Weekly Files (20): Claims, COB (5), Eligibility (5), AltCarrier (4), Division (4), Provider
--TRGETL4