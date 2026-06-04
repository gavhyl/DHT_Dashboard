--CLAIM--
SELECT TapeID, FORMAT(Sum(TotalAmountPaid),'C','en-US') [Paid], Format(count(*),'N0') [Records]
FROM [HAPRx].[claim].[TRGRxClaim] (nolock)
WHERE TapeID IN ({TAPEIDS})
GROUP BY TapeID
ORDER BY TapeID

--MINING--
SELECT TapeID, FORMAT(Sum(TotalAmountPaid),'C','en-US') [Paid], Format(count(*),'N0') [Records]
FROM [HAPRx].[mining].[RxClaim] (nolock)
WHERE TapeID IN ({TAPEIDS})
GROUP BY TapeID
ORDER BY TapeID