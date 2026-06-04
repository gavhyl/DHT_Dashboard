SELECT TOP 200 [TapeID], [VolSerNum], [FileName], t.[FileTypeID], f.[Name], [FileSize], [FileCreateDate], [FileDate], [ProcessStatusId] 
FROM [Kaiser_NW].[etl].[tape] T (nolock)
JOIN [Kaiser_NW].[config].[FileType] F (nolock)
ON t.filetypeId = f.filetypeid
--Where FileName like '%20260113%'
ORDER BY TapeID desc

------------------

--SELECT *
--  FROM [Kaiser_CO].[config].[FileType]
  --WHERE FileTypeId = 6