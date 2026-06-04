SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [AetnaRx].[etl].[tape] T (nolock)
JOIN [AetnaRx].[config].[Table] F (nolock)
ON t.TableID = f.TableID
--WHERE t.TableID in (100,200,910,920)  --[Claims, Elig, OI Member, OI Medicare Member]
--WHERE t.TableID in (100) --and [FileName] like '%260410%'
--WHERE t.TableID in (200) and [FileName] like '%EIE-CVSCMK.MBRMDCR%' --(Copy/Paste Elig names to verify daily/weekly loads)
--WHERE f.[TableName] in ('DTL','PRM','SUP') and [FileName] like '%260423%'
--WHERE f.[TableName] in ('TRR') and [FileName] like '%260423%'
ORDER BY TapeID desc