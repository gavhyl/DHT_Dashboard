--CLAIM--
SELECT TapeID, FORMAT(Sum(payamount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
FROM [CenteneFidelisRx].[cache].[TRGCache] (nolock)
WHERE TapeID IN ({TAPEIDS})
GROUP BY TapeID
ORDER BY TapeID

--MINING--
SELECT TapeID, FORMAT(Sum(TotalAmountPaid),'C','en-US') [Paid], Format(count(*),'N0') [Records]
FROM [CenteneFidelisRx].[mining].[RxClaim] (nolock)
WHERE TapeID IN ({TAPEIDS})
GROUP BY TapeID
ORDER BY TapeID