SELECT TOP 200 [TapeID], [VolSerNum], [FileName], t.[FileTypeID], f.[FileType], [FileSize], [FileCreateDate], [FileDate], [ProcessStatusID], [DataDescription]
FROM [AetnaSubro].[dbo].[tblTape] T (nolock)
JOIN [AetnaSubro].[dbo].[tblFileType] F (nolock)
ON t.FileTypeID = f.FileTypeID
ORDER BY TapeID desc

---------------------------------------------------------------
--RESEARCH--

--Select PayDate, FORMAT(Sum(payamount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
--From AetnaHRP.cache.mining (nolock)
--where TapeID > 11633 and PayDate >= '2025-07-01'
--Group by PayDate
--Order by PayDate

---------------------------------------------------------------
--RESEARCH--

--Select TapeID, PatientRelationship, '$' + FORMAT(SUM(PayAmount), 'N0', 'en-US') [Paid], Format(count(*),'N0') [Records]
--From [AetnaRCE].[Claims].[Standard] (nolock)
--where TapeID >= 15102
--and PatientAddress1 is NULL
--Group by TapeID, PatientRelationship
--Order by TapeID, PatientRelationship