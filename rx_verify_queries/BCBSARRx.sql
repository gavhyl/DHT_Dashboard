--CLAIM--
SELECT TapeID, FORMAT(Sum(DRUGPYALLOWEDPAID),'C','en-US') [Paid], Format(count(*),'N0') [Records]
FROM [BCBSARRx].[claim].[TRGClaim] (nolock)
WHERE TapeID IN ({TAPEIDS})
GROUP BY TapeID
ORDER BY TapeID

--MINING--
SELECT TapeID, FORMAT(Sum(TotalAmountPaid),'C','en-US') [Paid], Format(count(*),'N0') [Records]
FROM [BCBSARRx].[mining].[RxClaim] (nolock)
WHERE TapeID IN ({TAPEIDS})
GROUP BY TapeID
ORDER BY TapeID