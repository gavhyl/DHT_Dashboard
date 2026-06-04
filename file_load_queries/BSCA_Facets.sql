SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [BSCA_Facets].[etl].[tape] T (nolock)
JOIN [BSCA_Facets].[config].[Table] F (nolock)
ON t.TableID = f.TableID
--WHERE [FileName] like '%Surrogacy%'
ORDER BY TapeID desc