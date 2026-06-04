SELECT TOP 200 *
FROM CVSPBMRx.etl.Tape (nolock)
WHERE FileLoadDate >= DATEADD(Month, DATEDIFF(Month, 0, GETDATE()),0)
AND FileLoadDate < DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()) + 1, 0)
ORDER BY TapeID

--Expected Monthly Files (15): Eligibility (CA, FL, GA, IA, IL, IN, LA, MI, NH, NM, NV, NY, SC, TX, WA)
--TRGETL3