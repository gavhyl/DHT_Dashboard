SELECT [TapeID], [VolSerNum], [FileName], t.[FileTypeID], f.[FileType], [FileSize], [FileCreateDate], [FileDate], [ProcessStatusID], [DataDescription]
FROM [BCBSNC].[dbo].[tblTape] T (nolock)
JOIN [BCBSNC].[dbo].[tblFileType] F (nolock)
ON t.FileTypeID = f.FileTypeID
--WHERE FILENAME LIKE '%20260215%'
--WHERE f.[FileTypeID] = 8 --[Elig Check]
--WHERE f.[FileTypeID] = 9 --[Provider Check] - Good through 3/9
--WHERE f.[FileTypeID] = 3 --[PassFile Check] - Good through 3/10
--WHERE f.[FileTypeID] = 10 --[CAQH Check] - Good through 3/9 & 3/10
ORDER BY TapeID desc

-------------------------------------------
--RESEARCH--

--Select TapeID, ClientCode, SeniorMarketInd, '$' + FORMAT(SUM(PayAmount), 'N0', 'en-US') [Paid], Format(count(*),'N0') [Records]
--From BCBSNC.dbo.vwMiningCache_Full
--Where TapeID >= 41482
--Group by TapeID, ClientCode, SeniorMarketInd
--Order by TapeID, ClientCode, SeniorMarketInd

--Select Top 100 *
--From BCBSNC.dbo.vwMiningCache_Full
--Where TapeID = 40416 --and SeniorMarketInd = 'Y'

--Select Top 100 *
--From BCBSNC.dbo.vwMiningCache_Full
--Where TapeID = 42896

--SELECT Year(PayDate) [Yr], Month(PayDate) [Mth], '$' + FORMAT(SUM(PayAmount), 'N0', 'en-US') [Paid], Format(count(*),'N0') [Records]
--FROM [BCBSNC].[DBO].[vwMiningcache_full] (nolock)
--where TapeId >= 29986 and Year(PayDate) in (2025,2026) and ClientCode not in ('BCBSNC_SR')
--group by Year(PayDate), Month(PayDate)
--order by Year(PayDate), Month(PayDate)

--SELECT PayDate, '$' + FORMAT(SUM(PayAmount), 'N0', 'en-US') [Paid], Format(count(*),'N0') [Records]
--FROM [BCBSNC].[DBO].[vwMiningcache_full] (nolock)
--where TapeId = 42896 and Year(PayDate) in (2026)
--group by PayDate
--order by PayDate