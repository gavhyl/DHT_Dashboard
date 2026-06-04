--CLAIM--
SELECT TapeID, FORMAT(Sum(SubrogationPaidAmount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
FROM [EverNorthRx].[claim].[TRGClaim] (nolock)
WHERE TapeID IN ({TAPEIDS})
GROUP BY TapeID
ORDER BY TapeID

--MINING--
SELECT TapeID, FORMAT(Sum(TotalAmountPaid),'C','en-US') [Paid], Format(count(*),'N0') [Records]
FROM [EverNorthRx].[mining].[RxClaim] (nolock)
WHERE TapeID IN ({TAPEIDS})
GROUP BY TapeID
ORDER BY TapeID