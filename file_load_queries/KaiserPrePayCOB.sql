SELECT TOP 200 *
FROM [KaiserPrePayCOB].[etl].[Tape] (nolock)
WHERE FileLoadDate >= DATEADD(Month, DATEDIFF(Month, 0, GETDATE()),0)
AND FileLoadDate < DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()) + 1, 0)
AND TableID = 1000
ORDER BY TapeID

-------------------------------------------------------
--RESEARCH--

--SELECT MC.TapeID, FileName, FileSize, MIN(PayDate) [Min], MAX(PayDate) [Max], FORMAT(Sum(payamount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
--FROM KaiserPrePayCOB.cache.Mining MC (nolock)
--Join KaiserPrePayCOB.etl.tape T (nolock)
--on mc.TapeID = t.TapeID
--Where MC.TapeID >= 342
--Group by MC.TapeID, FileName, FileSize
--ORDER BY MC.TapeID