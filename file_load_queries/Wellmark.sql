SELECT [TapeID], [VolSerNum], [FileName], t.[FileTypeID], f.[FileType], [FileSize], [FileCreateDate], [FileDate], [ProcessStatusID], [DataDescription]
FROM [Wellmark].[dbo].[tblTape] T (nolock)
JOIN [Wellmark].[dbo].[tblFileType] F (nolock)
ON t.FileTypeID = f.FileTypeID
ORDER BY TapeID desc

--------------------------------------------------------------
--RESEARCH--

--select top 1000*
--from WellMark.dbo.vwMiningCache_Full
--where tapeid = 4231

--SELECT year(PayDate) [Year],month(PayDate) [Month], ITSType, Format(count(*),'N0') [Records], '$' + FORMAT(SUM(PayAmount), 'N0', 'en-US') [Paid], count(distinct PayDate) [Days]
--  FROM [WellMark].[dbo].[vwMiningcache_full] (nolock)
--  Where year(PayDate) in (2024, 2025, 2026) And TapeID > 4196
--  Group by year(PayDate), month(PayDate), ITSType
--  Order by year(PayDate), month(PayDate), ITSType