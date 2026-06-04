SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [Kaiser_WA].[etl].[tape] T (nolock)
JOIN [Kaiser_WA].[config].[Table] F (nolock)
ON t.TableID = f.TableID
ORDER BY TapeID desc

------------------------------------------------------------

--SELECT DISTINCT [c].[TapeID], [FileName], [c].[isDuplicate], Format(count(*),'N0') [Records]
--FROM [Kaiser_WA].[history].[Claim] [c] (NOLOCK)
--JOIN [Kaiser_WA].[etl].[tape] [T]
--ON c.TapeID = t.TapeID
--WHERE [c].[TapeID] >= 1932 --and isDuplicate = '1'
--GROUP BY [c].[TapeID], [FileName], [c].[isDuplicate]
--ORDER BY [c].[TapeID]

--SELECT [c].[TapeID], [FileName], '$' + FORMAT(SUM(PayAmount), 'N0', 'en-US') [Paid], Format(count(*),'N0') [Records]
--FROM [Kaiser_WA].[history].[Claim] [c] (NOLOCK)
--JOIN [Kaiser_WA].[etl].[tape] [T]
--ON c.TapeID = t.TapeID
--WHERE [c].[TapeID] >= 1932
--GROUP BY [c].[TapeID], [FileName]
--ORDER BY [c].[TapeID]

--Select TapeID, '$' + FORMAT(SUM(PayAmount), 'N0', 'en-US') [Paid], Format(count(*),'N0') [Records]
--From Kaiser_WA.cache.mining
--where TapeID in (1940) --and ICD9_1 is Null
--Group By TapeID

--Select Format(count(*),'N0') [Records]
--FROM [Kaiser_WA].[history].[Claim] 
--WHERE TapeID = 1940 and Diag1 is Null

--Select TapeID, Finalst,FORMAT(Sum(payamount),'C','en-US') [Paid], Format(count(*),'N0') [Records], 
--sum(CASE when [Diag1] is NULL THEN 1 ELSE 0 END) [NULL_Diag1]
--from [Kaiser_WA].[history].[Claim] 
--where TapeId = 1940
--group by TapeID, Finalst
--order by TapeID, Finalst