--MINING--
SELECT TapeID, FORMAT(Sum(TotalAmountPaid),'C','en-US') [Paid], Format(count(*),'N0') [Records]
FROM [ElevanceMMMRx].[mining].[RxClaim] (nolock)
WHERE TapeID IN ({TAPEIDS})
GROUP BY TapeID
ORDER BY TapeID