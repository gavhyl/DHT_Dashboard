SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [UPMC].[etl].[tape] T (nolock)
JOIN [UPMC].[config].[Table] F (nolock)
ON t.TableID = f.TableID
ORDER BY TapeID desc

-----------------------------------
--RESEARCH--

--Select [TapeID], [PayDate] = isnull(convert(varchar(10),PayDate,120),''), Datename(Weekday, PayDate) [Day], FORMAT(Sum(PayAmount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
--From [UPMC].[cache].[Mining] (nolock)
--Where tapeid in (446, 448, 460)
--Group by [TapeID], [PayDate]
--Order by [TapeID], [PayDate]