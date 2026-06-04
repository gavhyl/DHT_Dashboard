SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription] 
FROM [KaiserSCPareo].[etl].[tape] T (nolock)
JOIN [KaiserSCPareo].[config].[Table] F (nolock)
ON t.TableID = f.TableID
ORDER BY TapeID desc

-------------------------------------------------------
--PayDate Review