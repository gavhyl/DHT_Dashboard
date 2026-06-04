SELECT [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [HarvardPilgrim].[etl].[tape] T (nolock)
JOIN [HarvardPilgrim].[config].[Table] F (nolock)
ON t.TableID = f.TableID
ORDER BY TapeID desc

-----------------------------------------------------
--RESEARCH--

--Select [TapeID], [PayDate], Datename(Weekday, PayDate) [Day], FORMAT(Sum(PayAmount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
--From [HarvardPilgrim].[cache].[Mining] (nolock)
--Where tapeid >= 463
--Group by [TapeID], [PayDate]
--Order by [TapeID], [PayDate]

--Select top 1000 *
--From [HarvardPilgrim].[cache].[Mining] (nolock)
--Where tapeid = 496

--Select [TapeID], [ClientCode], [SubroClientCode], FORMAT(Sum(PayAmount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
--From [HarvardPilgrim].[cache].[Mining] (nolock)
--Where tapeid >= 463
--Group by [TapeID], [ClientCode], [SubroClientCode]
--Order by [TapeID], [ClientCode], [SubroClientCode]

--Select *
--From HarvardPilgrim.history.Eligibility
--Where TapeID = 508

--Select [TapeID], FORMAT(Sum(PayAmount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
--From HarvardPilgrim.cache.Mining
--Where TapeID in (507,506,505,504)
--Group by [TapeID]
--Order by [TapeID]