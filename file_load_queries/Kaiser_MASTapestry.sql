SELECT TOP 200 [TapeID], [VolSerNum], [FileName], t.[FileTypeID], f.[Name], [FileSize], [FileCreateDate], [FileDate], [ProcessStatusId] 
FROM [Kaiser_MASTapestry].[etl].[tape] T (nolock)
JOIN [Kaiser_MASTapestry].[config].[FileType] F (nolock)
ON t.filetypeId = f.filetypeid
--Where FileName like '%20260113%'
ORDER BY TapeID desc

---------------------------------------------------------------
--RESEARCH--

--Select FORMAT(Sum(payamount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
--from Kaiser_MASTapestry.cache.vwMining (nolock)
--where TapeId = 909731
--and SubscriberAddress1 is Null

--Select FORMAT(Sum(payamount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
--from Kaiser_MASTapestry.cache.vwMining (nolock)
--where TapeId = 811054
--and ICD9_1 is Null

---------------------------------------------------------------

----Expected Daily Files (13-14): Claims CCA/TPMG (11-12 per PCN), Claim Reason CCA & TPMG
----TRGETL1
--SELECT *
--FROM Kaiser_NCTapestry.etl.tape (nolock)
--ORDER BY TapeID desc

----Expected Daily Files (13): Claims (11 per PCN), Claim Reason (2 per date - HDR & DTL)
----TRGETL1
--SELECT *
--FROM Kaiser_SCTapestry.etl.tape (nolock)
--ORDER BY TapeID desc