SELECT TOP 200 *
FROM MedImpactPBMRx.etl.Tape (nolock)
WHERE FileLoadDate >= DATEADD(Month, DATEDIFF(Month, 0, GETDATE()),0)
AND FileLoadDate < DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()) + 1, 0)
ORDER BY TapeID

--Expected Monthly Files (5): Raw1, Raw2, Raw3 (SOM), Raw5, Raw6 (EOM)
--TRGETL3