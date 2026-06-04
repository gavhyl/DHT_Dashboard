SELECT [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [Tufts_PublicPlan].[etl].[tape] T (nolock)
JOIN [Tufts_PublicPlan].[config].[Table] F (nolock)
ON t.TableID = f.TableID
ORDER BY TapeID desc

-----------------------------------------------------
--RESEARCH--

--Select SubroClientCode, LineOfBusiness, FORMAT(Sum(payamount),'C','en-US') [Paid], Format(count(*),'N0') [Records], 
--sum(CASE when [ProviderName] is NULL THEN 1 ELSE 0 END) [NULL_ProvName]
--from [Tufts_PublicPlan].[cache].[Mining] (nolock)
--where TapeId = 499
--group by SubroClientCode, LineOfBusiness
--order by [NULL_ProvName] desc

--Select top 5000 *
--from [Tufts_PublicPlan].[cache].[Mining] (nolock)
--where TapeId = 499