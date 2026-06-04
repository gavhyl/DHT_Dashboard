SELECT TOP 200 [TapeID], [VolSerNum], [FileName], t.[FileTypeID], f.[FileType], [FileSize], [FileCreateDate], [FileDate], [ProcessStatusID], [DataDescription]
FROM [Tufts_Audit_CIT].[dbo].[tblTape] T (nolock)
JOIN [Tufts_Audit_CIT].[dbo].[tblFileType] F (nolock)
ON t.FileTypeID = f.FileTypeID
ORDER BY TapeID desc

-----------------------------------------------------------
--RESEARCH--