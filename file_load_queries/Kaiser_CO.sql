SELECT TOP 200 [TapeID], [VolSerNum], [FileName], t.[FileTypeID], f.[Name], [FileSize], [FileCreateDate], [FileDate], [ProcessStatusId] 
FROM [Kaiser_CO].[etl].[tape] T (nolock)
JOIN [Kaiser_CO].[config].[FileType] F (nolock)
ON t.filetypeId = f.filetypeid
--Where FileName like '%20260113%'
ORDER BY TapeID desc

--Expected Daily Files (63): Claims (49), Membership (14)
--Pareo Passfile (FileType 34)