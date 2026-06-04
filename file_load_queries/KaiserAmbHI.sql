SELECT TOP 200 *
FROM KaiserAmbHI.etl.tape (nolock)
ORDER BY TapeID desc

--Expected Monthly Files (4): Claims, Eligibility (3)
--TRGETL1