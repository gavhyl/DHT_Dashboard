SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [EmblemFacets].[etl].[tape] T (nolock)
JOIN [EmblemFacets].[config].[Table] F (nolock)
ON t.TableID = f.TableID
--where t.TableID in (4000,5000,6000,7000)
--WHERE [FileName] like '%provider%'
ORDER BY TapeID desc

---------------------------------------------------------------
--RESEARCH--