SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [CareSourceRx].[etl].[tape] T (nolock)
JOIN [CareSourceRx].[config].[Table] F (nolock)
ON t.TableID = f.TableID
--WHERE t.[FileName] like '%SUP8451%'
ORDER BY TapeID desc