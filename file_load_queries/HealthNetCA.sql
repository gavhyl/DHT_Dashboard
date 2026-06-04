SELECT TOP 200 [TapeID], [VolSerNum], [FileName], t.[FileTypeID], f.[FileType], [FileSize], [FileCreateDate], [FileDate], [ProcessStatusID], [DataDescription]
FROM [HealthNetCA].[dbo].[tblTape] T (nolock)
JOIN [HealthNetCA].[dbo].[tblFileType] F (nolock)
ON t.FileTypeID = f.FileTypeID
ORDER BY TapeID desc

---------------------------------------------------------
----Cert Stats for DMG
--SELECT T.VolSerNum, [FileName], [FileSize], T.FileTypeID, C.TapeID, MIN(PayDate) [Min], MAX(PayDate) [Max], '$' + FORMAT(SUM(PayAmount), 'N0', 'en-US') [Paid], Format(count(*),'N0') [Records]
--  FROM [HealthNetCA].[dbo].[vwMiningCache_Full] C (NOLOCK)
--  JOIN [HealthNetCA].[dbo].[tblTape] T (NOLOCK)
--  ON t.TapeID = c.TapeID
--  WHERE C.TapeID >= 15926
--  Group by T.VolserNum, [FileName], [FileSize], T.FileTypeID, C.TapeID
--  Order by T.VolserNum, [FileName], [FileSize], T.FileTypeID, C.TapeID

---------------------------------------------------------
--RESEARCH--

--Select t.[VolSerNum], '$' + FORMAT(SUM(PayAmount), 'N0', 'en-US') [Paid], Format(count(*),'N0') [Records]  
--from HealthNetCA.dbo.vwMiningCache_Full c
--JOIN [HealthNetCA].[dbo].[tblTape] T (NOLOCK)
--ON t.TapeID = c.TapeID
--where c.tapeID >= 15712
--group by t.[VolSerNum]
--order by t.[VolSerNum]

--Select t.[VolSerNum], c.TapeID, [FileName], '$' + FORMAT(SUM(PayAmount), 'N0', 'en-US') [Paid], Format(count(*),'N0') [Records]  
--from HealthNetCA.dbo.vwMiningCache_Full c
--JOIN [HealthNetCA].[dbo].[tblTape] T (NOLOCK)
--ON t.TapeID = c.TapeID
--where c.tapeID >= 15993
--group by t.[VolSerNum], c.TapeID, [FileName]
--order by t.[VolSerNum], c.TapeID, [FileName]

--Select ClientCode, '$' + FORMAT(SUM(PayAmount), 'N0', 'en-US') [Paid], Format(count(*),'N0') [Records]    
--from HealthNetCA.dbo.vwMiningCache_Full
--where tapeid >= 15937
--group by ClientCode
--order by ClientCode