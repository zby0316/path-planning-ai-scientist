param(
    [Parameter(Mandatory=$true)][string]$DocxPath,
    [Parameter(Mandatory=$true)][string]$PdfPath
)

$ErrorActionPreference = 'Stop'
$docx = [System.IO.Path]::GetFullPath($DocxPath)
$pdf = [System.IO.Path]::GetFullPath($PdfPath)
$pdfDir = [System.IO.Path]::GetDirectoryName($pdf)
[System.IO.Directory]::CreateDirectory($pdfDir) | Out-Null

$word = $null
$doc = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $doc = $word.Documents.Open($docx, $false, $false)

    foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
    $doc.Fields.Update() | Out-Null
    foreach ($section in $doc.Sections) {
        foreach ($header in $section.Headers) { $header.Range.Fields.Update() | Out-Null }
        foreach ($footer in $section.Footers) { $footer.Range.Fields.Update() | Out-Null }
    }

    $doc.Save()
    # wdExportFormatPDF = 17; wdExportOptimizeForPrint = 0
    $doc.ExportAsFixedFormat($pdf, 17, $false, 0)
    $pages = $doc.ComputeStatistics(2)
    [pscustomobject]@{
        docx = $docx
        pdf = $pdf
        pages = $pages
        toc_count = $doc.TablesOfContents.Count
    } | ConvertTo-Json -Compress
}
finally {
    if ($doc -ne $null) { $doc.Close($false) }
    if ($word -ne $null) { $word.Quit() }
    if ($doc -ne $null) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc) }
    if ($word -ne $null) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
