SELECT TOP 200 *
FROM BCBSKS.dbo.tbltape (nolock)
ORDER BY TapeID desc

--Expected Weekly Files (3): Claim, CodeSet, Eligibility
--TRGETL1