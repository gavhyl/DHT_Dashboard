--CLAIM--
SELECT TapeID, FORMAT(Sum(TOTALAMOUNTPAID),'C','en-US') [Paid], Format(count(*),'N0') [Records]
FROM [ElixirRx].[claim].[TRGClaim] (nolock)
WHERE TapeID IN ({TAPEIDS})
GROUP BY TapeID
ORDER BY TapeID

--MINING--
SELECT TapeID, FORMAT(Sum(TotalAmountPaid),'C','en-US') [Paid], Format(count(*),'N0') [Records]
FROM [ElixirRx].[mining].[RxClaim] (nolock)
WHERE TapeID IN ({TAPEIDS})
GROUP BY TapeID
ORDER BY TapeID