SELECT [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [WellCare].[etl].[tape] T (nolock)
JOIN [WellCare].[config].[Table] F (nolock)
ON t.TableID = f.TableID
ORDER BY TapeID desc

----------------------------------------------------------------------
--Research--

--Select top 1000*
--from Centene.dbo.vwMiningcache_full 
--where TapeID = 82079 and LineOfBusiness = 'CC'

--Select c.TapeID, [FileName], ClientCode, SubroClientCode, '$' + FORMAT(SUM(PayAmount), 'N0', 'en-US') [Paid], Format(count(*),'N0') [Records]
----,sum(CASE when [Patientaddress1] is NULL THEN 1 ELSE 0 END) [Null PT_Add]
--from Centene.dbo.vwMiningcache_full C
--Join Centene.dbo.tbltape T
--On c.TapeID = t.TapeID
--where C.tapeID >= 82640 and SubroClientCode = 'NCM'
--group by c.TapeID, [FileName], ClientCode, SubroClientCode
--order by c.TapeID, [FileName], ClientCode, SubroClientCode

--Select TapeID, ClientCode, LineOfBusiness, CARRIER_DESC, REGION_DESC, BUS_LINE_DESC, FORMAT(Sum(PayAmount),'C','en-US') [Paid], Format(count(*),'N0') [Records], 
--sum(CASE when [Patientaddress1] is NULL THEN 1 ELSE 0 END) [Null PT_Add]
--from  Centene.dbo.vwMiningcache_full
--where TapeId in (82078,82079)
--group by TapeID, ClientCode, LineOfBusiness, Carrier_DESC, REGION_DESC, BUS_LINE_DESC
--order by TapeID, ClientCode, LineOfBusiness, Carrier_DESC, REGION_DESC, BUS_LINE_DESC