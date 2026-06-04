SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription] 
FROM [KaiserNCPareo].[etl].[tape] T (nolock)
JOIN [KaiserNCPareo].[config].[Table] F (nolock)
ON t.TableID = f.TableID
ORDER BY TapeID desc

--Expected Daily Files (66): Claims (50), Eligibility (13), Group (3)
--**Passfile
--TableID: Claims = 1000's, Elig = 2000's, Group = 4000's, Passfile = 6000