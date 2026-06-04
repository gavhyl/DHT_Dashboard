SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [Medica].[etl].[tape] T (nolock)
JOIN [Medica].[config].[Table] F (nolock)
ON t.TableID = f.TableID
ORDER BY TapeID desc


--Expected Weekly Files (2): Claims, Eligibility
--TRGETL4