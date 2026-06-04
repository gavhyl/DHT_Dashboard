SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [GEHA].[etl].[tape] T (nolock)
JOIN [GEHA].[config].[Table] F (nolock)
ON t.TableID = f.TableID
ORDER BY TapeID desc

-----------------------------------------------------
--RESEARCH--

--Select TapeID, ClientCode, LineOfBusiness, PlanType, ClientSystem, FORMAT(Sum(payamount),'C','en-US') [Paid], Format(count(*),'N0') [Records], 
--sum(CASE when [ICD9_1] is NULL THEN 1 ELSE 0 END) [NULL_ICD]
--from [GEHA].[cache].[Mining] (nolock)
--where TapeId = 
--group by TapeID, ClientCode,LineOfBusiness,PlanType,ClientSystem
--order by TapeID, ClientCode,LineOfBusiness,PlanType,ClientSystem

--Select TapeID, GroupNumber, GroupName, FORMAT(Sum(payamount),'C','en-US') [Paid], Format(count(*),'N0') [Records], 
--sum(CASE when [PatientAddress1] is NULL THEN 1 ELSE 0 END) [NULL_PTAdd1]
--from [GEHA].[cache].[Mining] (nolock)
--where TapeId >= 4873 and PatientAddress1 is Null 
--group by TapeID, GroupNumber, GroupName
--order by TapeID, GroupNumber, GroupName