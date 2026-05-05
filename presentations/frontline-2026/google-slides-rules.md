# Google Slides Compatibility Rules

These rules MUST be followed by all PPTX generation code to ensure formatting survives Google Slides import.

## CRITICAL RULES

### 1. Text Box Width Buffer
Set all text box widths to **Actual Text Width + 15%**.
Google Slides renders fonts slightly wider than PPTX. Without buffer, text wraps or gets cut off.

```python
# Example: If text needs 5 inches, set box to 5.75 inches
text_box_width = calculated_width * 1.15
```

### 2. No Autofit
Explicitly disable "Autofit Text to Shape" on every text frame.
```python
from pptx.enum.text import MSO_AUTO_SIZE
text_frame.auto_size = MSO_AUTO_SIZE.NONE
```

### 3. Group Complex Shapes
When building multi-part diagrams (radial diagrams, architecture layers, connected shapes):
- Group all related lines, circles, and shapes into a single group object
- This prevents individual elements from shifting during import
```python
# Use add_group_shape() to create a group, then add shapes to it
```

### 4. Margin Protection
Keep ALL content at least **0.75 inches** from slide edges.
Google Slides' UI chrome can clip content near edges.

### 5. Font Safety
- Primary: `Libre Franklin` (Backbase corporate font, available on Google Fonts)
- Fallback: `Helvetica`, `Arial`
- NEVER use fonts that aren't available on Google Slides

### 6. No Gradient Fills in Shapes
Google Slides handles gradient fills inconsistently from PPTX.
- Use solid fills only for shape backgrounds
- Gradients are acceptable in HTML output only

### 7. No Shadow Effects
PowerPoint shadow effects render differently in Google Slides.
- Skip `shadow` properties on shapes
- Use color contrast for visual depth instead

### 8. EMU Precision
Use EMU (English Metric Units) for all positioning to avoid rounding errors.
```python
from pptx.util import Inches, Pt, Emu
# 1 inch = 914400 EMU
# Always calculate from Inches() for consistency
```

### 9. No Rotated Text
Text rotation renders unpredictably in Google Slides.
- Keep all text horizontal
- Use layout changes instead of rotation for visual variety

### 10. Image Handling
- Embed images directly (no external links)
- Use PNG for diagrams/icons, JPEG for photos
- Size images explicitly — do not rely on auto-scaling
