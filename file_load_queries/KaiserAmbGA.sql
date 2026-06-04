SELECT TOP 200 *
FROM KaiserAmbGA.etl.tape (nolock)
ORDER BY TapeID desc

--Expected Monthly Files (2): Claims, Eligibility
--TRGETL1