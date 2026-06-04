SELECT [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [BCBSFL].[etl].[tape] T (nolock)
JOIN [BCBSFL].[config].[Table] F (nolock)
ON t.TableID = f.TableID
ORDER BY TapeID desc

------------------------------------------------------------
--RESEARCH--

--SELECT MC.TapeID, FileName, FileSize, MIN(PayDate) [Min], MAX(PayDate) [Max], '$' + FORMAT(SUM(PayAmount), 'N0', 'en-US') [Paid], Format(count(*),'N0') [Records]
--FROM BCBSFL.cache.Mining MC (nolock)
--Join BCBSFL.etl.tape T (nolock)
--on mc.TapeID = t.TapeID
--Where MC.TapeID >= 12963
--Group by MC.TapeID, FileName, FileSize
--ORDER BY MC.TapeID

--select GroupPlanFundType, PlanType, MedicarePrimaryIndicator, '$' + FORMAT(SUM(PayAmount), 'N0', 'en-US') [Paid], Format(count(*),'N0') [Records]
--FROM BCBSFL.cache.Mining MC (nolock)
--where tapeid = 13082
--and groupname is Null
--Group by GroupPlanFundType, PlanType, MedicarePrimaryIndicator
--order by PlanType

--select top 1000 *
--FROM BCBSFL.cache.Mining MC (nolock)
--where tapeid = 13082




--GROUPNAME NULL