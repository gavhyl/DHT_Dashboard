SELECT TOP 200 [TapeID], [VolSerNum], [FileName], t.[FileTypeID], f.[Name], [FileSize], [FileCreateDate], [FileDate], [ProcessStatusId] 
FROM [Kaiser_GA].[etl].[tape] T (nolock)
JOIN [Kaiser_GA].[config].[FileType] F (nolock)
ON t.filetypeId = f.filetypeid
--Where FileName like '%20260113%'
ORDER BY TapeID desc

--Expected Daily Files (49): Claims (49)
--Pareo Passfile (FileType 28)