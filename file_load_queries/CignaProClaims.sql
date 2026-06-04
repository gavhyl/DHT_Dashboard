SELECT [TapeID], [VolSerNum], [FileName], t.[FileTypeID], f.[FileType], [FileSize], [FileCreateDate], [FileDate], [ProcessStatusID], [DataDescription]
FROM [CignaProClaims].[dbo].[tblTape] T (nolock)
JOIN [CignaProClaims].[dbo].[tblFileType] F (nolock)
ON t.FileTypeID = f.FileTypeID
ORDER BY TapeID desc

------------------------------------------------------------------------
--RESEARCH--

--Select top 1000*
--from CignaFacets.dbo.vwMiningCache_Full
--where TapeId >= 3517

--Select TapeID, PayDate, Datename(Weekday, PayDate) [Day], '$' + FORMAT(SUM(PayAmount), 'N0', 'en-US') [Paid], Format(count(*),'N0') [Records]
--from CignaFacets.dbo.vwMiningCache_Full
--where TapeId >= 3517
--Group by TapeID, PayDate, Datename(Weekday, PayDate)
--Order by TapeID, PayDate, Datename(Weekday, PayDate)

--Select Year(PayDate) [Year], Month(PayDate) [Month], '$' + FORMAT(SUM(PayAmount), 'N0', 'en-US') [Paid], Format(count(*),'N0') [Records]
--from CignaFacets.dbo.vwMiningCache_Full
--where TapeId >= 3462
--Group by Year(PayDate), Month(PayDate)
--Order by Year(PayDate), Month(PayDate)