SELECT TOP 200 [TapeID], [VolSerNum], [FileName], t.[FileTypeID], f.[FileType], [FileSize], [FileCreateDate], [FileDate], [ProcessStatusID], [DataDescription]
FROM [TuftsMedPref].[dbo].[tblTape] T (nolock)
JOIN [TuftsMedPref].[dbo].[tblFileType] F (nolock)
ON t.FileTypeID = f.FileTypeID
ORDER BY TapeID desc

--------------------------------------------------------
--RESEARCH--

--Select FORMAT(Sum(payamount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
--from TuftsMedPref.dbo.vwMiningcache_full (nolock)
--where TapeId in (1737,1738)
--and ProviderName is Null