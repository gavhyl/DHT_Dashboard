SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [MedStar].[etl].[tape] T (nolock)
JOIN [MedStar].[config].[Table] F (nolock)
ON t.TableID = f.TableID
--WHERE t.TableID in (1000,2000)
ORDER BY TapeID desc

-----------------------------------------------------

--Select TapeID, PayDate, Datename(Weekday, PayDate) [Day], '$' + FORMAT(SUM(PayAmount), 'N0', 'en-US') [Paid], Format(count(*),'N0') [Records]
--From [MedStar].[cache].[Mining]
--Where Year(PayDate) in (2025,2026)
--Group by TapeID, PayDate
--Order by TapeID, PayDate