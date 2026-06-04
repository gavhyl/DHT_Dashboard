SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [CenteneQualChoice].[etl].[tape] T (nolock)
JOIN [CenteneQualChoice].[config].[Table] F (nolock)
ON t.TableID = f.TableID
ORDER BY TapeID desc

----------------------------------------------
--Research

--Select TapeID, FORMAT(Sum(PayAmount),'C','en-US') [Paid], Format(count(*),'N0') [Records] 
--from CenteneQualChoice.cache.Mining
--where TapeID in (271,286,292) and PayAmount <= '0.00'
--group by TapeID
--order by TapeID

--Select TapeID, FORMAT(Sum(PayAmount),'C','en-US') [Paid], Format(count(*),'N0') [Records] 
--from CenteneQualChoice.cache.Mining
--where TapeID in (271,286,292) and PayAmount > '0.00'
--group by TapeID
--order by TapeID

--Select TapeID, [PayDate], Datename(Weekday, PayDate) [Day], FORMAT(Sum(PayAmount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
--From CenteneQualChoice.cache.mining (nolock)
--Where tapeid >= 414
--Group by TapeID, PayDate
--Order by TapeID, PayDate

--Select TapeID, LineOfBusiness, FORMAT(Sum(PayAmount),'C','en-US') [Paid], Format(count(*),'N0') [Records] 
--from CenteneQualChoice.cache.Mining
--where TapeID >= 430
--group by TapeID, LineOfBusiness
--order by TapeID, LineOfBusiness