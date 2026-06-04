SELECT TOP 200 [TapeID], [VolSerNum], [FileName], t.[FileTypeID], f.[FileType], [FileSize], [FileCreateDate], [FileDate], [ProcessStatusID], [DataDescription]
FROM [BCBSNorthCarolinaFEP].[dbo].[tblTape] T (nolock)
JOIN [BCBSNorthCarolinaFEP].[dbo].[tblFileType] F (nolock)
ON t.FileTypeID = f.FileTypeID
ORDER BY TapeID desc


-------------------------------------------------------
--RESEARCH--

--SELECT *
--  FROM [BCBSNorthCarolinaFEP].[dbo].[vwMiningcache_full] (nolock)
--  WHERE TapeID = 

--SELECT year(PayDate) [Year],month(PayDate) [Month], Format(count(*),'N0') [Records], FORMAT(Sum(payamount),'C','en-US') [Paid], count(distinct PayDate) [Days]
--  FROM [BCBSNorthCarolinaFEP].[dbo].[vwMiningcache_full] (nolock)
--  Where year(PayDate) in (2025)
--  and TapeID >= 9488
--  Group by year(PayDate),month(PayDate)
--  Order by year(PayDate),month(PayDate)