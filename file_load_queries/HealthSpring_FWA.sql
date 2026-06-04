SELECT TOP 200 [TapeID], [VolSerNum], [FileName], t.[FileTypeID], f.[FileType], [FileSize], [FileCreateDate], [FileDate], [ProcessStatusID], [DataDescription]
FROM [HealthSpring_FWA].[dbo].[tblTape] T (nolock)
JOIN [HealthSpring_FWA].[dbo].[tblFileType] F (nolock)
ON t.FileTypeID = f.FileTypeID
ORDER BY TapeID desc

-----------------------------------------------------------------------------
--RESEARCH--

--Select TapeID, Year(StartDate) [YR Start], '$' + FORMAT(SUM(PayAmount), 'N0', 'en-US') [Paid], Format(count(*),'N0') [Records]
--From [HealthSpring_FWA].[dbo].[vwMiningCache_Full]
--Where TapeID >= 2182
--Group By TapeID, Year(StartDate)
--Order By TapeID, Year(StartDate)