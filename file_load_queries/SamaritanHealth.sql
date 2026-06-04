SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [SamaritanHealth].[etl].[tape] T (nolock)
JOIN [SamaritanHealth].[config].[Table] F (nolock)
ON t.TableID = f.TableID
--WHERE [FileName] like '%Claim\shp_history_professional%'
ORDER BY TapeID desc

---------------------------------------------
--RESEARCH--

--Select TapeID, PayDate, Datename(Weekday, PayDate) [Day], '$' + FORMAT(SUM(PayAmount), 'N0', 'en-US') [Paid], Format(count(*),'N0') [Records]
--from [SamaritanHealth].[cache].[Mining] (nolock)
--where TapeID in (244,253,360,370)
--Group by TapeID, PayDate
--Order by TapeID, PayDate