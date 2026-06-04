SELECT TOP 200 *
FROM Kaiser_HealthConnect.dbo.tbltape (nolock)
ORDER BY TapeID desc

------------------

--Select FORMAT(Sum(payamount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
--from Kaiser_HealthConnect.dbo.vwMiningcache_Full (nolock)
--where TapeId = 866443
--and ICD9_1 is Null