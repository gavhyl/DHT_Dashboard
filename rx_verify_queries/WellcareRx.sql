--CLAIM--
SELECT TapeID, FORMAT(Sum(AmountPaid),'C','en-US') [Paid], Format(count(*),'N0') [Records]
FROM [WellcareRx].[claim].[TRGClaim] (nolock)
WHERE TapeID IN ({TAPEIDS})
GROUP BY TapeID
ORDER BY TapeID

--MINING--
SELECT TapeID, FORMAT(Sum(TotalAmountPaid),'C','en-US') [Paid], Format(count(*),'N0') [Records]
FROM [WellcareRx].[mining].[RxClaim] (nolock)
WHERE TapeID IN ({TAPEIDS})
GROUP BY TapeID
ORDER BY TapeID