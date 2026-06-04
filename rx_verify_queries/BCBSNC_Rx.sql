--CLAIM--
SELECT TapeID,
    FORMAT(SUM(CASE WHEN [INSURANCE_PAID_SIGN] = '-'
        THEN [INSURANCE_PAID_AMOUNT] * -1
        ELSE [INSURANCE_PAID_AMOUNT] END), 'C', 'en-US') [Paid],
    Format(count(*), 'N0') [Records]
FROM [BCBSNC_Rx].[dbo].[vwClaimHistory] (nolock)
WHERE TapeID IN ({TAPEIDS})
AND TRG_DupeIndicator = 'N'
GROUP BY TapeID
ORDER BY TapeID

--MINING--
SELECT TapeID, FORMAT(Sum(TotalAmountPaid),'C','en-US') [Paid], Format(count(*),'N0') [Records]
FROM [BCBSNC_Rx].[dbo].[RxClaims] (nolock)
WHERE TapeID IN ({TAPEIDS})
GROUP BY TapeID
ORDER BY TapeID