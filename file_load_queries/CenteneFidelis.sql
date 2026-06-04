SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [CenteneFidelis].[etl].[tape] T (nolock)
JOIN [CenteneFidelis].[config].[Table] F (nolock)
ON t.TableID = f.TableID
ORDER BY TapeID desc

--Expected Weekly Files (5): Claim Load, Provider, Claim Detail, Eligibility, Claim Header
--TRGETL4