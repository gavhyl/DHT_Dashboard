SELECT [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [JohnsHopkins].[etl].[tape] T (nolock)
JOIN [JohnsHopkins].[config].[Table] F (nolock)
ON t.TableID = f.TableID
ORDER BY TapeID desc

---------------------------------------------
--RESEARCH--

--Select top 15 ClaimNumber,SubscriberID,SubscriberFirstName,SubscriberLastName,SubscriberAddress1,SubscriberCity,SubscriberState,PatientID,PatientFirstName,PatientLastName,ICD9_1 [ICD10_1]
--from JohnsHopkins.cache.Mining (nolock)
--where TapeId = 2035 and ICD9_1 is NULL

--Select TapeID, Year(PatientEffectiveDate), month(PatientEffectiveDate), --SubroClientCode, Market, LineofBusiness, PlanType, 
--FORMAT(Sum(payamount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
--from JohnsHopkins.cache.Mining (nolock)
--where TapeId >= 2033
--and ICD9_1 is Null
--Group by TapeID, Year(PatientEffectiveDate), month(PatientEffectiveDate)--, SubroClientCode, Market, LineofBusiness, PlanType
--Order by TapeID, Year(PatientEffectiveDate), month(PatientEffectiveDate)--, SubroClientCode, Market, LineofBusiness, PlanType

--Select FORMAT(Sum(payamount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
--from JohnsHopkins.cache.Mining (nolock)
--where TapeId = 2033
--and ICD9_1 is Null

--Select TapeID, PayDate, Datename(Weekday, PayDate) [Day], '$' + FORMAT(SUM(PayAmount), 'N0', 'en-US') [Paid], Format(count(*),'N0') [Records]
--from [JohnsHopkins].[cache].[Mining] (nolock)
--where TapeID >= 2000
--Group by TapeID, PayDate
--Order by TapeID, PayDate