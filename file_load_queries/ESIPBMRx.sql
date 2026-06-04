SELECT TOP 200 *
FROM ESIPBMRx.etl.Tape (nolock)
WHERE FileLoadDate >= DATEADD(Month, DATEDIFF(Month, 0, GETDATE()),0)
AND FileLoadDate < DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()) + 1, 0)
ORDER BY TapeID

--Expected Monthly Files (102): Eligibility
--TRGETL3