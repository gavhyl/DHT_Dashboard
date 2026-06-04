SELECT TOP 200 [TapeID], [VolSerNum], [FileName], t.[FileTypeID], f.[FileType], [FileSize], [FileCreateDate], [FileDate], [ProcessStatusID], [DataDescription]
FROM [HMSA].[dbo].[tblTape] T (nolock)
JOIN [HMSA].[dbo].[tblFileType] F (nolock)
ON t.FileTypeID = f.FileTypeID
ORDER BY TapeID desc


---------------------------------------------------------
--RESEARCH--

--rawlcomp.outbound_hmsa_rawlings_memberfep_extract_20260406 (Yearly FEP Elig sent to DMG)