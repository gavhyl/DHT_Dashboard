SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [PremeraMedAdvVIS].[etl].[tape] T (nolock)
JOIN [PremeraMedAdvVIS].[config].[Table] F (nolock)
ON t.TableID = f.TableID
ORDER BY TapeID desc

----------------------------------------------------
--RESEARCH--

--Select TapeID, Year(StartDate) [Year], '$' + FORMAT(SUM(PayAmount), 'N0', 'en-US') [Paid], Format(count(*),'N0') [Records]
--From Premera.dbo.vwMiningCache_Full
--where tapeid in (42001,42012,42021)
--and PatientAddress1 is Null and Year(StartDate) in (2025,2026)
--Group by TapeID, Year(StartDate)
--Order by TapeID, Year(StartDate)