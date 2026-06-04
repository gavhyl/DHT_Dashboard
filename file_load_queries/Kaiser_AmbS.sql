SELECT TOP 200 *
FROM Kaiser_AmbS.etl.tape (nolock)
ORDER BY TapeID desc

--Expected Monthly Files (2): Claims, Eligibility
--TRGETL1