SELECT TOP 200 *
FROM KaiserAmbNW.etl.tape (nolock)
ORDER BY TapeID desc

-------------------------------------------------------

--Select TapeID,FORMAT(Sum(payamount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
--from KaiserAmbGA.cache.Mining (nolock)
--where TapeId >= 190
--and SubscriberAddress1 is Null
--Group by TapeID
--Order by TapeID