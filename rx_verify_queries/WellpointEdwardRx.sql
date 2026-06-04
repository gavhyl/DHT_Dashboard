--CLAIM--
SELECT [C].[TapeID],
    FORMAT(SUM(CASE WHEN [cSplitClaimIndicator] = 'Y'
        THEN [cSplitAmountPaid_sum]
        ELSE [AmountPaid] END), 'C', 'en-US') [Paid],
    Format(count(*), 'N0') [Records]
FROM [WellpointEdwardRx].[dbo].[vwClaimHistory] [C] (nolock)
WHERE [C].[TapeID] IN ({TAPEIDS})
AND [C].[TRG_DupeIndicator] = 'N'
GROUP BY [C].[TapeID]
ORDER BY [C].[TapeID]

--MINING--
SELECT R.TAPEID AS TapeID, FORMAT(Sum(TotalAmountPaid), 'C', 'en-US') [Paid],
    Format(count(*), 'N0') [Records]
FROM [WellpointEdwardRx].[dbo].[RXCLAIMS] R (nolock)
WHERE R.TAPEID IN ({TAPEIDS})
GROUP BY R.TAPEID
ORDER BY R.TAPEID