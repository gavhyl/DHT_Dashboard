SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [Oscar].[etl].[tape] T (nolock)
JOIN [Oscar].[config].[Table] F (nolock)
ON t.TableID = f.TableID
ORDER BY TapeID desc

-----------------------------------------------------------------
--RESEARCH--

--Select TapeID, ClientCode,LineOfBusiness,PlanType,FORMAT(Sum(payamount),'C','en-US') [Paid], Format(count(*),'N0') [Records], 
--sum(CASE when [PatientAddress1] is NULL THEN 1 ELSE 0 END) [NULL_PTAdd]
--from [Oscar].[cache].[mining] (nolock)
--where TapeId = 1055
--group by TapeID, ClientCode,LineOfBusiness,PlanType
--order by TapeID, ClientCode,LineOfBusiness,PlanType

--Select FORMAT(Sum(payamount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
--from oscar.cache.Mining (nolock)
--where TapeId = 1055
--and PatientAddress1 is Null

--Select PatientRelationship, FORMAT(Sum(payamount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
--from [Oscar].[cache].[mining] (nolock)
--where TapeId = 1055
--and PatientAddress1 is Null
--Group by PatientRelationship
--Order by PatientRelationship