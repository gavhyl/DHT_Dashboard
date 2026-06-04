SELECT TOP 200 [TapeID], [VolSerNum], [FileName], t.[FileTypeID], f.[FileType], t.[ProcessStatusID], [FileSize], [FileCreateDate], [FileDate], [DataDescription]
FROM [AetnaRCE].[etl].[tape] T (nolock)
JOIN [AetnaRCE].[etl].[FileType] F (nolock)
ON t.FileTypeID = f.FileTypeID
ORDER BY TapeID desc

--Expected Monthly Files (4): Members (2), Groups, Providers
--Expected Daily Files (1): Block Files
--TRGETL2