SELECT TOP 200 *
FROM BCBSKSMedAdv.etl.tape (nolock)
ORDER BY TapeID desc

-----------------------------------------------------
--RESEARCH--

--Select year(PayDate) [Year], month(PayDate) [Month], FORMAT(Sum(payamount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
--from BCBSKSMedAdv.cache.mining (nolock)
--where year(PayDate) in (2024, 2025)
--group by year(PayDate), month(PayDate)
--order by year(PayDate), month(PayDate)

--Select year(PayDate) [Year], month(PayDate) [Month], FORMAT(Sum(payamount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
--from BCBSKSMedAdv.cache.mining (nolock)
--where TapeID >= 900 and year(PayDate) in (2025)
--group by year(PayDate), month(PayDate)
--order by year(PayDate), month(PayDate)

--SELECT T.ProdCtrlNo, T.TableID, C.TapeID, MIN(PayDate) [Min], MAX(PayDate) [Max], FORMAT(Sum(payamount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
--  FROM [BCBSKSMedAdv].[cache].[Mining] C (NOLOCK)
--  JOIN BCBSKSMedAdv.etl.tape T (NOLOCK)
--  ON t.TapeID = c.TapeID
--  WHERE C.TapeID >= 949
--  Group by T.ProdCtrlNo, T.TableID, C.TapeID
--  Order by T.ProdCtrlNo, T.TableID, C.TapeID

--Select FORMAT(Sum(payamount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
--from BCBSKSMedAdv.cache.mining (nolock)
--where TapeID = 961 and SubscriberAddress1 is Null

--Select *
--from BCBSKSMedAdv.history.eligibility (nolock)
--where TapeID = 986