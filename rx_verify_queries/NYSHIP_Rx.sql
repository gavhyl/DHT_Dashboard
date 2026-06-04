--MINING--
SELECT TapeID, FORMAT(Sum(PatientPayAmount),'C','en-US') [Paid], Format(count(*),'N0') [Records]
FROM [NYSHIP_Rx].[dbo].[RxClaims] (nolock)
WHERE TapeID IN ({TAPEIDS})
GROUP BY TapeID
ORDER BY TapeID