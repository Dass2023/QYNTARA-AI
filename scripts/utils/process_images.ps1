Add-Type -AssemblyName System.Drawing

function Remove-Background {
    param ($inputPath, $outputPath)
    
    if (-not (Test-Path $inputPath)) {
        Write-Host "Error: Input file not found: $inputPath"
        return
    }

    try {
        $bmp = [System.Drawing.Bitmap]::FromFile($inputPath)
        # Create a copy to edit
        $newBmp = New-Object System.Drawing.Bitmap($bmp.Width, $bmp.Height)
        $g = [System.Drawing.Graphics]::FromImage($newBmp)
        $g.DrawImage($bmp, 0, 0, $bmp.Width, $bmp.Height)
        $g.Dispose()
        
        Write-Host "Processing $inputPath ($($bmp.Width)x$($bmp.Height))..."
        
        # Simple thresholding
        for ($x=0; $x -lt $newBmp.Width; $x++) {
            for ($y=0; $y -lt $newBmp.Height; $y++) {
                $c = $newBmp.GetPixel($x, $y)
                # Check for dark gray/black (< 40)
                if ($c.R -lt 40 -and $c.G -lt 40 -and $c.B -lt 40) {
                    $newBmp.SetPixel($x, $y, [System.Drawing.Color]::Transparent)
                }
            }
        }
        
        $newBmp.Save($outputPath, [System.Drawing.Imaging.ImageFormat]::Png)
        Write-Host "Saved to $outputPath"
        
        $bmp.Dispose()
        $newBmp.Dispose()
    }
    catch {
        Write-Host "Error processing image: $_"
    }
}

$iconSrc = "C:\Users\ArockiadassD_2j5cw54\.gemini\antigravity\brain\2f5a697b-41f7-4358-97c1-aa7390e017d4\qyntara_icon_3d_1765523450588.png"
$typeSrc = "C:\Users\ArockiadassD_2j5cw54\.gemini\antigravity\brain\2f5a697b-41f7-4358-97c1-aa7390e017d4\qyntara_type_only_1765523113574.png"

$iconDst = "e:\QYNTARA AI\qyntara_ai\ui\resources\icon_brand.png"
$typeDst = "e:\QYNTARA AI\qyntara_ai\ui\resources\type_brand.png"

Remove-Background $iconSrc $iconDst
Remove-Background $typeSrc $typeDst
