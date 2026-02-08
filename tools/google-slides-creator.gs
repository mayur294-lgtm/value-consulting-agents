/**
 * Backbase Presentation → Google Slides Creator
 *
 * SETUP INSTRUCTIONS:
 * 1. Go to https://script.google.com
 * 2. Create a new project (give it a name like "Backbase Slides Creator")
 * 3. Delete the default code and paste this entire file
 * 4. IMPORTANT: First run the TEST function to authorize:
 *    - Click the function dropdown (says "myFunction" by default)
 *    - Select "testCreateSlides"
 *    - Click Run (play button)
 *    - Authorize when prompted (Review Permissions → choose your account → Advanced → Go to project → Allow)
 * 5. After authorization works, Deploy:
 *    - Click Deploy → New deployment
 *    - Click the gear icon → Select "Web app"
 *    - Description: "Backbase Slides v1"
 *    - Execute as: "Me"
 *    - Who has access: "Anyone" (or "Anyone with Google account")
 *    - Click Deploy
 * 6. Copy the Web app URL - this is your import endpoint
 *
 * TROUBLESHOOTING:
 * - If nothing happens: Check View → Logs in the script editor after running
 * - If authorization fails: Make sure you're logged into the right Google account
 * - If deployment fails: Try "Manage deployments" and create a new version
 */

// ==========================================
// TEST FUNCTION - RUN THIS FIRST TO AUTHORIZE
// ==========================================

function testCreateSlides() {
  Logger.log("🚀 Starting test...");

  const testJson = JSON.stringify({
    "meta": { "title": "Test Presentation - Delete Me" },
    "scenes": [
      {
        "type": "title",
        "content": {
          "label": "TEST",
          "lines": [{ "text": "Authorization Test", "color": "blue" }],
          "subtitle": "If you see this slide, it worked!"
        }
      },
      {
        "type": "stats",
        "content": {
          "label": "METRICS",
          "heading": "Sample Stats",
          "cards": [
            { "label": "Test", "value": "100%", "context": "Working" }
          ]
        }
      }
    ]
  });

  Logger.log("📝 Test JSON created");

  const result = createPresentation(testJson);

  if (result.success) {
    Logger.log("✅ SUCCESS!");
    Logger.log("📊 Presentation URL: " + result.url);
    Logger.log("📋 Presentation ID: " + result.id);
    Logger.log("You can now deploy as a web app.");
  } else {
    Logger.log("❌ ERROR: " + result.error);
  }

  return result;
}

// Quick test with user's actual JSON structure
function testWithSampleData() {
  Logger.log("🚀 Testing with sample presentation data...");

  const sampleJson = JSON.stringify({
    "version": "2.0",
    "meta": {
      "title": "Sample Test",
      "brandName": "Backbase"
    },
    "scenes": [
      {
        "id": "s1",
        "type": "title",
        "title": "Opening",
        "theme": "dark",
        "content": {
          "label": "DEMO",
          "lines": [
            { "text": "HELLO", "color": "blue" },
            { "text": "WORLD", "color": "white" }
          ],
          "subtitle": "Test slide"
        }
      },
      {
        "id": "s2",
        "type": "stats",
        "title": "Numbers",
        "theme": "dark",
        "content": {
          "label": "PERFORMANCE",
          "heading": "Key Metrics",
          "cards": [
            { "label": "Growth", "value": "+42%", "valueColor": "green", "context": "YoY" },
            { "label": "NPS", "value": "72", "valueColor": "blue", "context": "Industry: 45" }
          ]
        }
      }
    ]
  });

  const result = createPresentation(sampleJson);

  if (result.success) {
    Logger.log("✅ SUCCESS! URL: " + result.url);
  } else {
    Logger.log("❌ ERROR: " + result.error);
  }

  return result;
}

// Web app entry point - serves the HTML interface
function doGet() {
  return HtmlService.createHtmlOutput(getWebInterface())
    .setTitle('Backbase → Google Slides')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

// Main function to create slides from JSON
function createPresentation(jsonString) {
  Logger.log("📥 createPresentation called");
  Logger.log("📝 Input type: " + typeof jsonString);
  Logger.log("📝 Input length: " + (jsonString ? jsonString.length : 'null/undefined'));

  // Guard against undefined/null input
  if (!jsonString || jsonString === 'undefined' || jsonString === 'null') {
    Logger.log("❌ ERROR: No JSON provided or invalid input");
    return {
      success: false,
      error: "No JSON data received. Make sure you pasted the JSON in the text area."
    };
  }

  try {
    Logger.log("📝 Parsing JSON...");
    const data = JSON.parse(jsonString);
    Logger.log("✅ JSON parsed successfully");

    const meta = data.meta || {};
    const scenes = data.scenes || [];
    Logger.log("📊 Found " + scenes.length + " scenes");

    // Create new presentation
    Logger.log("🎨 Creating presentation: " + (meta.title || 'Backbase Presentation'));
    const presentation = SlidesApp.create(meta.title || 'Backbase Presentation');
    Logger.log("✅ Presentation created with ID: " + presentation.getId());

    const slides = presentation.getSlides();

    // Remove default blank slide
    if (slides.length > 0) {
      slides[0].remove();
      Logger.log("🗑️ Removed default blank slide");
    }

    // Brand colors
    const COLORS = {
      blue: '#1A56FF',
      navy: '#1A1F36',
      white: '#FFFFFF',
      gray: '#6B7280',
      lightGray: '#F3F4F6',
      red: '#EF4444',
      green: '#10B981',
      orange: '#F59E0B',
      purple: '#8B5CF6',
      teal: '#14B8A6',
      pink: '#EC4899'
    };

    // Process each scene
    scenes.forEach((scene, index) => {
      Logger.log("🎬 Processing scene " + (index + 1) + "/" + scenes.length + ": " + scene.type);

      const slide = presentation.appendSlide(SlidesApp.PredefinedLayout.BLANK);
      slide.getBackground().setSolidFill(COLORS.white);

      const c = scene.content || {};

      switch (scene.type) {
        case 'title':
          renderTitle(slide, c, COLORS);
          break;
        case 'quote':
          renderQuote(slide, c, COLORS);
          break;
        case 'stats':
          renderStats(slide, c, COLORS);
          break;
        case 'cardGrid':
          renderCardGrid(slide, c, COLORS);
          break;
        case 'comparison':
          renderComparison(slide, c, COLORS);
          break;
        case 'caseStudy':
          renderCaseStudy(slide, c, COLORS);
          break;
        case 'timeline':
          renderTimeline(slide, c, COLORS);
          break;
        case 'iconGrid':
          renderIconGrid(slide, c, COLORS);
          break;
        case 'pyramid':
          renderPyramid(slide, c, COLORS);
          break;
        case 'flywheel':
          renderFlywheel(slide, c, COLORS);
          break;
        case 'table':
          renderTable(slide, c, COLORS);
          break;
        case 'journeyMap':
          renderJourneyMap(slide, c, COLORS);
          break;
        case 'capabilityMap':
          renderCapabilityMap(slide, c, COLORS);
          break;
        case 'barChart':
        case 'lineChart':
        case 'donutChart':
        case 'waterfallChart':
          renderChart(slide, scene.type, c, COLORS);
          break;
        default:
          renderDefault(slide, scene, COLORS);
      }
    });

    // Return the URL
    const url = presentation.getUrl();
    Logger.log("✅ All scenes processed successfully!");
    Logger.log("🔗 Presentation URL: " + url);

    return {
      success: true,
      url: url,
      id: presentation.getId(),
      title: meta.title || 'Backbase Presentation'
    };

  } catch (error) {
    Logger.log("❌ ERROR in createPresentation: " + error.toString());
    Logger.log("📍 Stack trace: " + error.stack);
    return {
      success: false,
      error: error.toString()
    };
  }
}

// ==========================================
// SCENE RENDERERS
// ==========================================

function renderTitle(slide, c, COLORS) {
  const pageWidth = 720;
  const pageHeight = 405;

  // Label
  if (c.label) {
    const label = slide.insertTextBox(c.label);
    label.setTop(60).setLeft(50).setWidth(620).setHeight(25);
    const labelText = label.getText();
    labelText.getTextStyle()
      .setFontSize(10)
      .setForegroundColor(COLORS.blue)
      .setBold(true);
    labelText.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);
  }

  // Main title lines
  const lines = c.lines || [];
  let yPos = 120;
  lines.forEach((line, i) => {
    const textBox = slide.insertTextBox(line.text || '');
    textBox.setTop(yPos).setLeft(50).setWidth(620).setHeight(50);
    const text = textBox.getText();
    text.getTextStyle()
      .setFontSize(36)
      .setForegroundColor(getColor(line.color, COLORS))
      .setBold(true);
    text.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);
    yPos += 55;
  });

  // Subtitle
  if (c.subtitle) {
    const subtitle = slide.insertTextBox(c.subtitle);
    subtitle.setTop(300).setLeft(50).setWidth(620).setHeight(30);
    const subText = subtitle.getText();
    subText.getTextStyle()
      .setFontSize(14)
      .setForegroundColor(COLORS.gray);
    subText.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);
  }
}

function renderQuote(slide, c, COLORS) {
  // Main quote text
  const quoteBox = slide.insertTextBox((c.text || '') + '\n' + (c.highlight || ''));
  quoteBox.setTop(120).setLeft(50).setWidth(620).setHeight(180);

  const text = quoteBox.getText();
  // Style the main text
  if (c.text) {
    const mainRange = text.getRange(0, c.text.length);
    mainRange.getTextStyle()
      .setFontSize(24)
      .setForegroundColor(COLORS.navy)
      .setBold(true);
  }
  // Style the highlight
  if (c.highlight && c.text) {
    const highlightStart = c.text.length + 1;
    const highlightRange = text.getRange(highlightStart, highlightStart + c.highlight.length);
    highlightRange.getTextStyle()
      .setFontSize(28)
      .setForegroundColor(COLORS.blue)
      .setBold(true);
  }
  text.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);
}

function renderStats(slide, c, COLORS) {
  // Label and heading
  addLabelAndHeading(slide, c, COLORS);

  // Stats cards
  const cards = c.cards || [];
  const cardWidth = 160;
  const cardHeight = 100;
  const gap = 20;
  const totalWidth = cards.length * cardWidth + (cards.length - 1) * gap;
  let startX = (720 - totalWidth) / 2;

  cards.forEach((card, i) => {
    const x = startX + i * (cardWidth + gap);
    const y = 150;

    // Card background
    const rect = slide.insertShape(SlidesApp.ShapeType.ROUND_RECTANGLE);
    rect.setTop(y).setLeft(x).setWidth(cardWidth).setHeight(cardHeight);
    rect.getFill().setSolidFill(COLORS.lightGray);
    rect.getBorder().setWeight(1).getLineFill().setSolidFill('#E5E7EB');

    // Label
    const labelBox = slide.insertTextBox(card.label || '');
    labelBox.setTop(y + 10).setLeft(x + 10).setWidth(cardWidth - 20).setHeight(20);
    labelBox.getText().getTextStyle().setFontSize(9).setForegroundColor(COLORS.blue).setBold(true);

    // Value
    const valueBox = slide.insertTextBox(card.value || '');
    valueBox.setTop(y + 35).setLeft(x + 10).setWidth(cardWidth - 20).setHeight(35);
    const valueText = valueBox.getText();
    valueText.getTextStyle()
      .setFontSize(24)
      .setForegroundColor(getColor(card.valueColor, COLORS) || COLORS.navy)
      .setBold(true);

    // Context
    if (card.context) {
      const contextBox = slide.insertTextBox(card.context);
      contextBox.setTop(y + 75).setLeft(x + 10).setWidth(cardWidth - 20).setHeight(20);
      contextBox.getText().getTextStyle().setFontSize(8).setForegroundColor(COLORS.gray);
    }
  });
}

function renderCardGrid(slide, c, COLORS) {
  addLabelAndHeading(slide, c, COLORS);

  const cards = c.cards || [];
  const cardWidth = 200;
  const cardHeight = 180;
  const gap = 20;
  const totalWidth = cards.length * cardWidth + (cards.length - 1) * gap;
  let startX = (720 - totalWidth) / 2;

  cards.forEach((card, i) => {
    const x = startX + i * (cardWidth + gap);
    const y = 120;

    // Card background
    const rect = slide.insertShape(SlidesApp.ShapeType.ROUND_RECTANGLE);
    rect.setTop(y).setLeft(x).setWidth(cardWidth).setHeight(cardHeight);
    rect.getFill().setSolidFill(COLORS.lightGray);
    rect.getBorder().setWeight(card.spotlight ? 2 : 1)
      .getLineFill().setSolidFill(card.spotlight ? COLORS.blue : '#E5E7EB');

    // Icon
    if (card.icon) {
      const iconBox = slide.insertTextBox(card.icon);
      iconBox.setTop(y + 10).setLeft(x + 10).setWidth(40).setHeight(35);
      iconBox.getText().getTextStyle().setFontSize(24);
    }

    // Title
    const titleBox = slide.insertTextBox(card.title || '');
    titleBox.setTop(y + 50).setLeft(x + 10).setWidth(cardWidth - 20).setHeight(25);
    titleBox.getText().getTextStyle().setFontSize(14).setForegroundColor(COLORS.navy).setBold(true);

    // Description
    if (card.description) {
      const descBox = slide.insertTextBox(card.description);
      descBox.setTop(y + 80).setLeft(x + 10).setWidth(cardWidth - 20).setHeight(30);
      descBox.getText().getTextStyle().setFontSize(9).setForegroundColor(COLORS.gray);
    }

    // Features
    const features = card.features || [];
    features.slice(0, 3).forEach((f, fi) => {
      const fBox = slide.insertTextBox('• ' + f);
      fBox.setTop(y + 115 + fi * 18).setLeft(x + 10).setWidth(cardWidth - 20).setHeight(18);
      fBox.getText().getTextStyle().setFontSize(9).setForegroundColor(COLORS.navy);
    });
  });
}

function renderComparison(slide, c, COLORS) {
  addLabelAndHeading(slide, c, COLORS);

  const sides = [c.left, c.right];
  const cardWidth = 280;
  const cardHeight = 150;

  sides.forEach((s, i) => {
    if (!s) return;
    const x = i === 0 ? 60 : 380;
    const y = 140;
    const borderColor = getColor(s.color, COLORS) || COLORS.gray;

    // Card background
    const rect = slide.insertShape(SlidesApp.ShapeType.ROUND_RECTANGLE);
    rect.setTop(y).setLeft(x).setWidth(cardWidth).setHeight(cardHeight);
    rect.getFill().setSolidFill(COLORS.lightGray);
    rect.getBorder().setWeight(2).getLineFill().setSolidFill(borderColor);

    // Title
    const titleBox = slide.insertTextBox(s.title || '');
    titleBox.setTop(y + 15).setLeft(x + 10).setWidth(cardWidth - 20).setHeight(25);
    const titleText = titleBox.getText();
    titleText.getTextStyle().setFontSize(11).setForegroundColor(borderColor).setBold(true);
    titleText.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);

    // Value
    const valueBox = slide.insertTextBox(s.value || '');
    valueBox.setTop(y + 45).setLeft(x + 10).setWidth(cardWidth - 20).setHeight(50);
    const valueText = valueBox.getText();
    valueText.getTextStyle().setFontSize(32).setForegroundColor(COLORS.navy).setBold(true);
    valueText.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);

    // Detail
    if (s.detail) {
      const detailBox = slide.insertTextBox(s.detail);
      detailBox.setTop(y + 105).setLeft(x + 10).setWidth(cardWidth - 20).setHeight(30);
      const detailText = detailBox.getText();
      detailText.getTextStyle().setFontSize(10).setForegroundColor(COLORS.gray);
      detailText.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);
    }
  });
}

function renderCaseStudy(slide, c, COLORS) {
  // Badge
  if (c.badge) {
    const badgeBox = slide.insertTextBox(c.badge);
    badgeBox.setTop(60).setLeft(50).setWidth(100).setHeight(20);
    badgeBox.getText().getTextStyle().setFontSize(9).setForegroundColor(COLORS.blue).setBold(true);
  }

  // Name
  const nameBox = slide.insertTextBox(c.name || '');
  nameBox.setTop(90).setLeft(50).setWidth(350).setHeight(40);
  nameBox.getText().getTextStyle().setFontSize(24).setForegroundColor(COLORS.navy).setBold(true);

  // Description
  if (c.description) {
    const descBox = slide.insertTextBox(c.description);
    descBox.setTop(140).setLeft(50).setWidth(350).setHeight(80);
    descBox.getText().getTextStyle().setFontSize(11).setForegroundColor(COLORS.gray);
  }

  // Result card
  const r = c.result || {};
  const resultRect = slide.insertShape(SlidesApp.ShapeType.ROUND_RECTANGLE);
  resultRect.setTop(70).setLeft(450).setWidth(220).setHeight(180);
  resultRect.getFill().setSolidFill(COLORS.lightGray);
  resultRect.getBorder().setWeight(2).getLineFill().setSolidFill(COLORS.blue);

  if (r.label) {
    const rLabelBox = slide.insertTextBox(r.label);
    rLabelBox.setTop(100).setLeft(460).setWidth(200).setHeight(25);
    const rLabelText = rLabelBox.getText();
    rLabelText.getTextStyle().setFontSize(9).setForegroundColor(COLORS.gray);
    rLabelText.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);
  }

  const rValueBox = slide.insertTextBox(r.value || '');
  rValueBox.setTop(130).setLeft(460).setWidth(200).setHeight(50);
  const rValueText = rValueBox.getText();
  rValueText.getTextStyle().setFontSize(36).setForegroundColor(COLORS.blue).setBold(true);
  rValueText.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);

  if (r.sublabel) {
    const rSubBox = slide.insertTextBox(r.sublabel);
    rSubBox.setTop(190).setLeft(460).setWidth(200).setHeight(25);
    const rSubText = rSubBox.getText();
    rSubText.getTextStyle().setFontSize(9).setForegroundColor(COLORS.gray);
    rSubText.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);
  }
}

function renderTimeline(slide, c, COLORS) {
  addLabelAndHeading(slide, c, COLORS);

  const phases = c.phases || [];
  const phaseWidth = 160;
  const phaseHeight = 150;
  const gap = 15;
  const totalWidth = phases.length * phaseWidth + (phases.length - 1) * gap;
  let startX = (720 - totalWidth) / 2;

  phases.forEach((p, i) => {
    const x = startX + i * (phaseWidth + gap);
    const y = 120;
    const isPrimary = p.variant === 'primary';

    // Phase card
    const rect = slide.insertShape(SlidesApp.ShapeType.ROUND_RECTANGLE);
    rect.setTop(y).setLeft(x).setWidth(phaseWidth).setHeight(phaseHeight);
    rect.getFill().setSolidFill(isPrimary ? '#E8F0FE' : COLORS.lightGray);
    rect.getBorder().setWeight(1).getLineFill().setSolidFill(isPrimary ? COLORS.blue : '#E5E7EB');

    // Label
    const labelBox = slide.insertTextBox(p.label || '');
    labelBox.setTop(y + 10).setLeft(x + 10).setWidth(phaseWidth - 20).setHeight(20);
    labelBox.getText().getTextStyle().setFontSize(9).setForegroundColor(COLORS.blue).setBold(true);

    // Title
    const titleBox = slide.insertTextBox(p.title || '');
    titleBox.setTop(y + 35).setLeft(x + 10).setWidth(phaseWidth - 20).setHeight(30);
    titleBox.getText().getTextStyle().setFontSize(14).setForegroundColor(COLORS.navy).setBold(true);

    // Tags
    const tags = p.tags || [];
    tags.slice(0, 4).forEach((t, ti) => {
      const tagBox = slide.insertTextBox('• ' + t);
      tagBox.setTop(y + 70 + ti * 18).setLeft(x + 10).setWidth(phaseWidth - 20).setHeight(18);
      tagBox.getText().getTextStyle().setFontSize(8).setForegroundColor(COLORS.gray);
    });
  });
}

function renderIconGrid(slide, c, COLORS) {
  addLabelAndHeading(slide, c, COLORS);

  const items = c.items || [];
  const itemWidth = 140;
  const itemHeight = 90;
  const gap = 20;
  const maxPerRow = 4;

  items.forEach((item, i) => {
    const row = Math.floor(i / maxPerRow);
    const col = i % maxPerRow;
    const itemsInRow = Math.min(maxPerRow, items.length - row * maxPerRow);
    const rowWidth = itemsInRow * itemWidth + (itemsInRow - 1) * gap;
    const startX = (720 - rowWidth) / 2;

    const x = startX + col * (itemWidth + gap);
    const y = 110 + row * (itemHeight + 15);

    // Card
    const rect = slide.insertShape(SlidesApp.ShapeType.ROUND_RECTANGLE);
    rect.setTop(y).setLeft(x).setWidth(itemWidth).setHeight(itemHeight);
    rect.getFill().setSolidFill(COLORS.lightGray);
    rect.getBorder().setWeight(1).getLineFill().setSolidFill('#E5E7EB');

    // Icon
    const iconBox = slide.insertTextBox(item.icon || '📌');
    iconBox.setTop(y + 8).setLeft(x).setWidth(itemWidth).setHeight(30);
    const iconText = iconBox.getText();
    iconText.getTextStyle().setFontSize(22);
    iconText.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);

    // Name
    const nameBox = slide.insertTextBox(item.name || '');
    nameBox.setTop(y + 42).setLeft(x + 5).setWidth(itemWidth - 10).setHeight(20);
    const nameText = nameBox.getText();
    nameText.getTextStyle().setFontSize(10).setForegroundColor(COLORS.navy).setBold(true);
    nameText.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);

    // Tagline
    if (item.tagline) {
      const tagBox = slide.insertTextBox(item.tagline);
      tagBox.setTop(y + 65).setLeft(x + 5).setWidth(itemWidth - 10).setHeight(18);
      const tagText = tagBox.getText();
      tagText.getTextStyle().setFontSize(8).setForegroundColor(COLORS.gray);
      tagText.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);
    }
  });
}

function renderPyramid(slide, c, COLORS) {
  addLabelAndHeading(slide, c, COLORS);

  const tiers = c.tiers || [];
  const maxWidth = 500;
  const tierHeight = 45;
  const gap = 8;
  const centerX = 360;

  tiers.forEach((tier, i) => {
    const widthFactor = 0.4 + (i / Math.max(tiers.length - 1, 1)) * 0.6;
    const w = maxWidth * widthFactor;
    const x = centerX - w / 2;
    const y = 110 + i * (tierHeight + gap);
    const isPrimary = tier.variant === 'primary';

    // Tier bar
    const rect = slide.insertShape(SlidesApp.ShapeType.ROUND_RECTANGLE);
    rect.setTop(y).setLeft(x).setWidth(w).setHeight(tierHeight);
    rect.getFill().setSolidFill(isPrimary ? '#E8F0FE' : COLORS.lightGray);
    rect.getBorder().setWeight(1).getLineFill().setSolidFill(isPrimary ? COLORS.blue : '#E5E7EB');

    // Label
    const labelBox = slide.insertTextBox(tier.label || '');
    labelBox.setTop(y + 5).setLeft(x + 10).setWidth(80).setHeight(18);
    labelBox.getText().getTextStyle().setFontSize(8).setForegroundColor(COLORS.blue).setBold(true);

    // Bar text
    const barBox = slide.insertTextBox(tier.bar || '');
    barBox.setTop(y + 12).setLeft(x + 95).setWidth(w - 110).setHeight(25);
    barBox.getText().getTextStyle().setFontSize(10).setForegroundColor(COLORS.navy);
  });
}

function renderFlywheel(slide, c, COLORS) {
  addLabelAndHeading(slide, c, COLORS);

  const centerX = 250;
  const centerY = 220;
  const radius = 100;

  // Center circle
  const centerCircle = slide.insertShape(SlidesApp.ShapeType.ELLIPSE);
  centerCircle.setTop(centerY - 40).setLeft(centerX - 40).setWidth(80).setHeight(80);
  centerCircle.getFill().setSolidFill('#E8F0FE');
  centerCircle.getBorder().setWeight(2).getLineFill().setSolidFill(COLORS.blue);

  const centerBox = slide.insertTextBox(c.center || 'Core');
  centerBox.setTop(centerY - 15).setLeft(centerX - 35).setWidth(70).setHeight(30);
  const centerText = centerBox.getText();
  centerText.getTextStyle().setFontSize(11).setForegroundColor(COLORS.blue).setBold(true);
  centerText.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);

  // Nodes
  const nodes = c.nodes || [];
  nodes.forEach((node, i) => {
    const angle = (i / nodes.length) * 2 * Math.PI - Math.PI / 2;
    const nx = centerX + radius * Math.cos(angle) - 40;
    const ny = centerY + radius * Math.sin(angle) - 18;

    const nodeRect = slide.insertShape(SlidesApp.ShapeType.ROUND_RECTANGLE);
    nodeRect.setTop(ny).setLeft(nx).setWidth(80).setHeight(36);
    nodeRect.getFill().setSolidFill(COLORS.lightGray);
    nodeRect.getBorder().setWeight(1).getLineFill().setSolidFill(COLORS.blue);

    const nodeBox = slide.insertTextBox(node.text || '');
    nodeBox.setTop(ny + 8).setLeft(nx + 5).setWidth(70).setHeight(20);
    const nodeText = nodeBox.getText();
    nodeText.getTextStyle().setFontSize(9).setForegroundColor(COLORS.navy);
    nodeText.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);
  });

  // Info section
  if (c.info) {
    const infoTitle = slide.insertTextBox('How it works');
    infoTitle.setTop(130).setLeft(420).setWidth(250).setHeight(25);
    infoTitle.getText().getTextStyle().setFontSize(12).setForegroundColor(COLORS.navy).setBold(true);

    const bullets = Array.isArray(c.info) ? c.info : [c.info];
    bullets.slice(0, 5).forEach((b, bi) => {
      const bBox = slide.insertTextBox('• ' + b);
      bBox.setTop(160 + bi * 25).setLeft(420).setWidth(250).setHeight(22);
      bBox.getText().getTextStyle().setFontSize(9).setForegroundColor(COLORS.gray);
    });
  }
}

function renderTable(slide, c, COLORS) {
  addLabelAndHeading(slide, c, COLORS);

  const rows = c.rows || [];
  if (rows.length === 0) return;

  const colCount = Math.max(...rows.map(r => (r.cells || []).length));
  if (colCount === 0) return;

  const tableWidth = 620;
  const tableHeight = Math.min(250, rows.length * 30);
  const colWidth = tableWidth / colCount;
  const rowHeight = tableHeight / rows.length;

  const table = slide.insertTable(rows.length, colCount);
  table.setTop(110).setLeft(50);

  rows.forEach((row, ri) => {
    const cells = row.cells || [];
    cells.forEach((cell, ci) => {
      const tableCell = table.getCell(ri, ci);
      tableCell.getText().setText(cell || '');
      tableCell.getText().getTextStyle()
        .setFontSize(9)
        .setForegroundColor(ri === 0 ? COLORS.navy : COLORS.gray)
        .setBold(ri === 0);
      tableCell.getFill().setSolidFill(ri === 0 ? COLORS.lightGray : COLORS.white);
    });
  });
}

function renderJourneyMap(slide, c, COLORS) {
  addLabelAndHeading(slide, c, COLORS, true);

  const phases = c.phases || [];
  const phaseWidth = Math.min(150, (620 / phases.length) - 10);
  const gap = 10;
  const totalWidth = phases.length * phaseWidth + (phases.length - 1) * gap;
  let startX = (720 - totalWidth) / 2;

  phases.forEach((phase, i) => {
    const x = startX + i * (phaseWidth + gap);

    // Phase header
    const headerRect = slide.insertShape(SlidesApp.ShapeType.ROUND_RECTANGLE);
    headerRect.setTop(80).setLeft(x).setWidth(phaseWidth).setHeight(28);
    headerRect.getFill().setSolidFill(COLORS.blue);
    headerRect.getBorder().setWeight(0);

    const headerBox = slide.insertTextBox(phase.name || '');
    headerBox.setTop(84).setLeft(x).setWidth(phaseWidth).setHeight(20);
    const headerText = headerBox.getText();
    headerText.getTextStyle().setFontSize(9).setForegroundColor(COLORS.white).setBold(true);
    headerText.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);

    // Sections
    const sections = [
      { title: 'Touchpoints', items: phase.touchpoints || [], color: COLORS.blue },
      { title: 'Pain Points', items: phase.painPoints || [], color: COLORS.red },
      { title: 'Opportunities', items: phase.opportunities || [], color: COLORS.green }
    ];

    let yPos = 115;
    sections.forEach(section => {
      const sectionTitle = slide.insertTextBox(section.title);
      sectionTitle.setTop(yPos).setLeft(x + 5).setWidth(phaseWidth - 10).setHeight(15);
      sectionTitle.getText().getTextStyle().setFontSize(7).setForegroundColor(section.color).setBold(true);
      yPos += 15;

      section.items.slice(0, 2).forEach(item => {
        const itemBox = slide.insertTextBox('• ' + item);
        itemBox.setTop(yPos).setLeft(x + 5).setWidth(phaseWidth - 10).setHeight(14);
        itemBox.getText().getTextStyle().setFontSize(7).setForegroundColor(COLORS.gray);
        yPos += 14;
      });
      yPos += 8;
    });
  });
}

function renderCapabilityMap(slide, c, COLORS) {
  // Heading
  if (c.heading) {
    const headingBox = slide.insertTextBox(c.heading);
    headingBox.setTop(20).setLeft(50).setWidth(620).setHeight(30);
    const headingText = headingBox.getText();
    headingText.getTextStyle().setFontSize(16).setForegroundColor(COLORS.navy).setBold(true);
    headingText.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);
  }

  // Problems summary
  const problems = c.problems || [];
  if (problems.length) {
    const probText = 'Problems: ' + problems.map(p => p.label).join(' | ');
    const probBox = slide.insertTextBox(probText);
    probBox.setTop(52).setLeft(50).setWidth(620).setHeight(18);
    const pText = probBox.getText();
    pText.getTextStyle().setFontSize(8).setForegroundColor(COLORS.gray);
    pText.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);
  }

  // Domains
  const domains = c.domains || [];
  let yPos = 75;

  domains.forEach(domain => {
    // Domain name
    const domainBox = slide.insertTextBox(domain.name || '');
    domainBox.setTop(yPos).setLeft(30).setWidth(150).setHeight(20);
    domainBox.getText().getTextStyle().setFontSize(10).setForegroundColor(COLORS.blue).setBold(true);

    // Capabilities
    const caps = domain.capabilities || [];
    const capWidth = 110;
    const capHeight = 24;
    const capsPerRow = 4;

    caps.forEach((cap, ci) => {
      const row = Math.floor(ci / capsPerRow);
      const col = ci % capsPerRow;
      const cx = 185 + col * (capWidth + 8);
      const cy = yPos + row * (capHeight + 5);

      const matColor = cap.maturity === 'high' ? COLORS.green :
                       cap.maturity === 'medium' ? COLORS.orange :
                       cap.maturity === 'low' ? COLORS.red : COLORS.gray;

      const capRect = slide.insertShape(SlidesApp.ShapeType.ROUND_RECTANGLE);
      capRect.setTop(cy).setLeft(cx).setWidth(capWidth).setHeight(capHeight);
      capRect.getFill().setSolidFill(COLORS.lightGray);
      capRect.getBorder().setWeight(2).getLineFill().setSolidFill(matColor);

      const capBox = slide.insertTextBox(cap.name || '');
      capBox.setTop(cy + 4).setLeft(cx + 5).setWidth(capWidth - 10).setHeight(16);
      capBox.getText().getTextStyle().setFontSize(8).setForegroundColor(COLORS.navy);
    });

    yPos += Math.ceil(caps.length / capsPerRow) * (capHeight + 5) + 25;
  });
}

function renderChart(slide, chartType, c, COLORS) {
  addLabelAndHeading(slide, c, COLORS);

  const chart = c.chart || {};

  // For charts, we'll render a simplified version with shapes and text
  // Google Slides API doesn't easily support creating editable charts like Sheets

  if (chartType === 'barChart') {
    const bars = chart.bars || [];
    const barWidth = 60;
    const maxHeight = 150;
    const gap = 20;
    const totalWidth = bars.length * barWidth + (bars.length - 1) * gap;
    let startX = (720 - totalWidth) / 2;
    const baseY = 320;

    // Find max value
    const maxVal = Math.max(...bars.map(b => parseFloat(b.value) || 0), 1);

    bars.forEach((bar, i) => {
      const x = startX + i * (barWidth + gap);
      const val = parseFloat(bar.value) || 0;
      const h = (val / maxVal) * maxHeight;
      const y = baseY - h;

      // Bar
      const rect = slide.insertShape(SlidesApp.ShapeType.RECTANGLE);
      rect.setTop(y).setLeft(x).setWidth(barWidth).setHeight(h);
      rect.getFill().setSolidFill(getColor(bar.color, COLORS) || COLORS.blue);
      rect.getBorder().setWeight(0);

      // Value
      const valBox = slide.insertTextBox(String(bar.value));
      valBox.setTop(y - 20).setLeft(x).setWidth(barWidth).setHeight(20);
      const valText = valBox.getText();
      valText.getTextStyle().setFontSize(10).setForegroundColor(COLORS.navy).setBold(true);
      valText.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);

      // Label
      const labelBox = slide.insertTextBox(bar.label || '');
      labelBox.setTop(baseY + 5).setLeft(x).setWidth(barWidth).setHeight(25);
      const labelText = labelBox.getText();
      labelText.getTextStyle().setFontSize(9).setForegroundColor(COLORS.gray);
      labelText.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);
    });

  } else if (chartType === 'donutChart') {
    // Simplified donut as segments list
    const segments = chart.segments || [];
    let yPos = 130;

    segments.forEach((seg, i) => {
      const color = getColor(seg.color, COLORS) || COLORS.blue;

      // Color indicator
      const colorRect = slide.insertShape(SlidesApp.ShapeType.RECTANGLE);
      colorRect.setTop(yPos).setLeft(250).setWidth(20).setHeight(20);
      colorRect.getFill().setSolidFill(color);
      colorRect.getBorder().setWeight(0);

      // Label and value
      const textBox = slide.insertTextBox(seg.label + ': ' + seg.value);
      textBox.setTop(yPos).setLeft(280).setWidth(200).setHeight(22);
      textBox.getText().getTextStyle().setFontSize(12).setForegroundColor(COLORS.navy);

      yPos += 30;
    });

  } else {
    // Fallback for other chart types
    const infoBox = slide.insertTextBox(chartType + ' - See HTML presentation for full chart visualization');
    infoBox.setTop(180).setLeft(100).setWidth(520).setHeight(40);
    const infoText = infoBox.getText();
    infoText.getTextStyle().setFontSize(12).setForegroundColor(COLORS.gray);
    infoText.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);
  }
}

function renderDefault(slide, scene, COLORS) {
  const titleBox = slide.insertTextBox(scene.title || 'Slide');
  titleBox.setTop(170).setLeft(50).setWidth(620).setHeight(60);
  const titleText = titleBox.getText();
  titleText.getTextStyle().setFontSize(28).setForegroundColor(COLORS.navy).setBold(true);
  titleText.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);
}

// ==========================================
// HELPER FUNCTIONS
// ==========================================

function addLabelAndHeading(slide, c, COLORS, compact) {
  const labelY = compact ? 25 : 35;
  const headingY = compact ? 45 : 60;

  if (c.label) {
    const labelBox = slide.insertTextBox(c.label);
    labelBox.setTop(labelY).setLeft(50).setWidth(620).setHeight(20);
    const labelText = labelBox.getText();
    labelText.getTextStyle().setFontSize(9).setForegroundColor(COLORS.blue).setBold(true);
    labelText.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);
  }

  if (c.heading) {
    const headingBox = slide.insertTextBox(c.heading);
    headingBox.setTop(headingY).setLeft(50).setWidth(620).setHeight(35);
    const headingText = headingBox.getText();
    headingText.getTextStyle().setFontSize(compact ? 16 : 20).setForegroundColor(COLORS.navy).setBold(true);
    headingText.getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);
  }
}

function getColor(colorName, COLORS) {
  if (!colorName) return null;
  const colorMap = {
    'blue': COLORS.blue,
    'navy': COLORS.navy,
    'white': COLORS.white,
    'gray': COLORS.gray,
    'red': COLORS.red,
    'green': COLORS.green,
    'orange': COLORS.orange,
    'purple': COLORS.purple,
    'teal': COLORS.teal,
    'pink': COLORS.pink
  };
  return colorMap[colorName] || colorName;
}

// ==========================================
// WEB INTERFACE
// ==========================================

function getWebInterface() {
  return `
<!DOCTYPE html>
<html>
<head>
  <base target="_top">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: linear-gradient(135deg, #1A1F36 0%, #2D3748 100%);
      min-height: 100vh;
      padding: 40px 20px;
    }
    .container {
      max-width: 800px;
      margin: 0 auto;
    }
    .header {
      text-align: center;
      margin-bottom: 30px;
    }
    .logo {
      font-size: 28px;
      font-weight: 800;
      color: #1A56FF;
      margin-bottom: 8px;
    }
    .subtitle {
      color: #9CA3AF;
      font-size: 14px;
    }
    .card {
      background: white;
      border-radius: 16px;
      padding: 30px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    label {
      display: block;
      font-weight: 600;
      color: #374151;
      margin-bottom: 8px;
    }
    textarea {
      width: 100%;
      height: 300px;
      border: 2px solid #E5E7EB;
      border-radius: 8px;
      padding: 15px;
      font-family: monospace;
      font-size: 12px;
      resize: vertical;
      transition: border-color 0.2s;
    }
    textarea:focus {
      outline: none;
      border-color: #1A56FF;
    }
    .btn {
      display: block;
      width: 100%;
      padding: 16px;
      background: #1A56FF;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      margin-top: 20px;
      transition: background 0.2s;
    }
    .btn:hover { background: #1544CC; }
    .btn:disabled { background: #9CA3AF; cursor: not-allowed; }
    .status {
      margin-top: 20px;
      padding: 15px;
      border-radius: 8px;
      text-align: center;
      display: none;
    }
    .status.success {
      background: #D1FAE5;
      color: #065F46;
      display: block;
    }
    .status.error {
      background: #FEE2E2;
      color: #991B1B;
      display: block;
    }
    .status a {
      color: #1A56FF;
      font-weight: 600;
    }
    .instructions {
      margin-top: 30px;
      padding: 20px;
      background: #F3F4F6;
      border-radius: 8px;
      font-size: 13px;
      color: #6B7280;
    }
    .instructions h4 {
      color: #374151;
      margin-bottom: 10px;
    }
    .instructions ol {
      margin-left: 20px;
    }
    .instructions li {
      margin-bottom: 5px;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="logo">Backbase → Google Slides</div>
      <div class="subtitle">Create editable Google Slides from your presentation JSON</div>
      <div style="color:#6B7280;font-size:11px;margin-top:5px;">v1.1</div>
    </div>

    <div class="card">
      <label for="jsonInput">Paste your presentation JSON:</label>
      <textarea id="jsonInput" placeholder='{"meta": {"title": "..."}, "scenes": [...]}'></textarea>

      <button class="btn" id="createBtn" onclick="createSlides()">
        🚀 Create Google Slides
      </button>

      <div id="status" class="status"></div>

      <div class="instructions">
        <h4>How to use:</h4>
        <ol>
          <li>In your HTML presentation, click <strong>Share → Export for Google Slides</strong></li>
          <li>Copy the JSON that appears</li>
          <li>Paste it in the text area above</li>
          <li>Click "Create Google Slides"</li>
          <li>Your new presentation will open in a new tab</li>
        </ol>
      </div>
    </div>
  </div>

  <script>
    function createSlides() {
      var btn = document.getElementById('createBtn');
      var status = document.getElementById('status');
      var textarea = document.getElementById('jsonInput');
      var jsonValue = textarea.value;

      console.log('Textarea value length:', jsonValue ? jsonValue.length : 0);

      if (!jsonValue || jsonValue.trim() === '') {
        status.className = 'status error';
        status.textContent = 'Please paste your JSON first';
        return;
      }

      var jsonString = jsonValue.trim();

      // Validate JSON
      try {
        var parsed = JSON.parse(jsonString);
        console.log('JSON valid, scenes:', parsed.scenes ? parsed.scenes.length : 0);
      } catch (e) {
        status.className = 'status error';
        status.textContent = 'Invalid JSON: ' + e.message;
        return;
      }

      btn.disabled = true;
      btn.textContent = '⏳ Creating slides...';
      status.className = 'status';
      status.style.display = 'none';

      console.log('Calling createPresentation with ' + jsonString.length + ' chars...');

      // Pass as explicit string to avoid undefined issues
      google.script.run
        .withSuccessHandler(function(result) {
          console.log('Success:', result);
          btn.disabled = false;
          btn.textContent = '🚀 Create Google Slides';

          if (result && result.success) {
            status.className = 'status success';
            var url = result.url;
            status.innerHTML = '✅ Created: <a href="' + url + '" target="_blank">' + result.title + '</a><br><br><a href="' + url + '" target="_blank" style="display:inline-block;padding:10px 20px;background:#1A56FF;color:white;text-decoration:none;border-radius:6px;font-weight:600;">📊 Open Presentation</a>';
          } else {
            status.className = 'status error';
            status.textContent = '❌ Error: ' + (result ? result.error : 'Unknown error');
          }
        })
        .withFailureHandler(function(error) {
          console.log('Failure:', error);
          btn.disabled = false;
          btn.textContent = '🚀 Create Google Slides';
          status.className = 'status error';
          status.innerHTML = '❌ Error: ' + (error.message || error) + '<br><br>💡 Make sure you ran testCreateSlides first to authorize.';
        })
        .createPresentation(jsonString);
    }
  </script>
</body>
</html>
  `;
}
