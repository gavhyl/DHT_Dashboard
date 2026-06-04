SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [WebTPA].[etl].[tape] T (nolock)
JOIN [WebTPA].[config].[Table] F (nolock)
ON t.TableID = f.TableID
ORDER BY TapeID desc

------------------------------------------------------------

--select member_id,*
--from [WEBTPA].[history].[Eligibility]
--where member_id in (13707816, 13709964, 13708160, 13707812, 13708144)
----where tapeid = 1930 and member_id in (13707816, 13709964, 13708160, 13707812, 13708144)--and Employergroup_ud = 'L2860'

--select *
--from [WEBTPA].[cache].[Mining]
--where tapeid = 1923 and GroupNumber = 'L2860' and SubscriberAddress1 is Null

--Select c.TapeID, [FileName], GroupNumber, GroupName, FORMAT(Sum(payamount),'C','en-US') [Paid], Format(count(*),'N0') [Records], 
--sum(CASE when [SubscriberAddress1] is NULL THEN 1 ELSE 0 END) [NULL_SubAdd]
--from [WEBTPA].[cache].[Mining] C
--join [WEBTPA].[etl].[Tape] T
--on C.TapeID = T.TapeID
--where GroupNumber = 'L2860'
--group by c.TapeID, [FileName], GroupNumber, GroupName
--order by c.TapeID, [FileName], GroupNumber, GroupName

--Select GroupNumber, GroupName, FORMAT(Sum(payamount),'C','en-US') [Paid], Format(count(*),'N0') [Records], 
--sum(CASE when [PatientEffectiveDate] is NULL THEN 1 ELSE 0 END) [NULL_EffDate]
--from [WEBTPA].[cache].[Mining]
--group by GroupNumber, GroupName
--order by GroupNumber, GroupName

--Select PayDate, Datename(Weekday, PayDate) [Day], FORMAT(Sum(PayAmount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
--from [WEBTPA].[cache].[Mining] (nolock)
--where TapeID in (1752, 1754)
--Group by PayDate
--Order by PayDate

--Select PayDate, Datename(Weekday, PayDate) [Day], FORMAT(Sum(PayAmount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
--from [WEBTPA].[cache].[Mining] (nolock)
--where TapeID in (1769, 1771)
--Group by PayDate
--Order by PayDate

--Select PayDate, Datename(Weekday, PayDate) [Day], FORMAT(Sum(PayAmount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
--from [WEBTPA].[cache].[Mining] (nolock)
--where TapeID in (1786, 1788)
--Group by PayDate
--Order by PayDate