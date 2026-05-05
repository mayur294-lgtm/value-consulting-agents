# Frontline 2026 — HTML Component Library

Components for the HTML preview builder. All use the design tokens from `design-tokens.json`.

---

## Base Styling

```css
@import url('https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@300;400;500;600;700;800&display=swap');

:root {
  --primary-navy: #001C3D;
  --action-blue: #1A5AFF;
  --surface-white: #FFFFFF;
  --bg-gray: #F5F7F9;
  --text-main: #001C3D;
  --text-muted: #5C6E84;
  --success-green: #2ECC71;
  --radius: 16px;
  --radius-pill: 30px;
}

body {
  font-family: 'Libre Franklin', Helvetica, Arial, sans-serif;
  margin: 0;
  padding: 0;
  background: var(--primary-navy);
  color: var(--text-main);
}

.slide {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 3% 4%;
  box-sizing: border-box;
}
```

---

## Component 1: Cover Slide

Navy background, large white title, subtitle, date.

```html
<section class="slide slide--cover">
  <span class="label">INTRODUCTION</span>
  <h1>AI-Native<br>Banking OS</h1>
  <p class="date">March 2026</p>
</section>
```

---

## Component 2: Section Divider

Navy background, section label + large title + tagline.

```html
<section class="slide slide--divider">
  <span class="label">INTRODUCTION TO BACKBASE</span>
  <h1>Unified Frontline</h1>
  <p class="tagline">What problem are we trying to solve?</p>
</section>
```

---

## Component 3: Split Comparison (From / To)

Two-column layout. Left gray, right white.

```html
<section class="slide slide--split">
  <h2 class="slide-title">Title Goes Here</h2>
  <div class="split">
    <div class="split__from">
      <h3>FRAGMENTED FRONTLINE</h3>
      <ul>
        <li>20-40 disconnected apps</li>
        <li>Manual steps everywhere</li>
      </ul>
    </div>
    <div class="split__to">
      <h3>UNIFIED FRONTLINE</h3>
      <ul>
        <li>Consistent modern experiences</li>
        <li>3x faster change velocity</li>
      </ul>
    </div>
  </div>
</section>
```

---

## Component 4: Content Slide (Full Width)

Title + subtitle + flexible content area.

```html
<section class="slide slide--content">
  <h2 class="slide-title">Challenge &bull; 50% of banking work lives between systems</h2>
  <p class="slide-subtitle">The expensive whitespace between systems.</p>
  <div class="content-area">
    <!-- Flexible: cards, diagrams, text blocks -->
  </div>
</section>
```

---

## Component 5: Product Showcase

Left text, right image.

```html
<section class="slide slide--showcase">
  <div class="showcase__text">
    <span class="label">CUSTOMER FACING</span>
    <h2>Customer Apps</h2>
    <p>Composable apps and tailored customer experiences.</p>
  </div>
  <div class="showcase__image">
    <img src="screenshot.png" alt="Product screenshot" />
  </div>
</section>
```

---

## Component 6: AI Assistant Widget ("Just Ask")

Gradient container with pill-shaped input.

```html
<div class="ai-widget">
  <div class="ai-widget__input">
    <input type="text" placeholder="Just ask" disabled />
    <span class="ai-icon">✦</span>
  </div>
</div>
```

```css
.ai-widget {
  background: linear-gradient(180deg, #EBF2FF 0%, #FFFFFF 100%);
  border-radius: var(--radius);
  padding: 24px;
}
.ai-widget__input input {
  border: 1px solid #D0D5DD;
  border-radius: var(--radius-pill);
  padding: 12px 20px;
  width: 100%;
  font-size: 14px;
}
```

---

## Component 7: Stat Card

Large number with label and optional trend indicator.

```html
<div class="stat-card">
  <span class="stat-card__number">3×</span>
  <span class="stat-card__label">Faster change velocity</span>
  <span class="stat-card__trend trend--up">↑ 12%</span>
</div>
```

---

## Component 8: Architecture Stack

Layered horizontal bars representing platform layers.

```html
<div class="arch-stack">
  <div class="arch-row arch-row--segments">
    <div class="arch-box">Online</div>
    <div class="arch-box">Mobile</div>
    <div class="arch-box">Conversational</div>
  </div>
  <div class="arch-row arch-row--workspaces">
    <div class="arch-box">Teller</div>
    <div class="arch-box">CSR</div>
    <div class="arch-box">RM</div>
    <div class="arch-box">Operations</div>
  </div>
  <div class="arch-bar arch-bar--platform">AI-native Banking OS</div>
  <div class="arch-row arch-row--systems">
    <div class="arch-box arch-box--muted">CRM</div>
    <div class="arch-box arch-box--muted">KYC</div>
    <div class="arch-box arch-box--muted">Payments</div>
  </div>
</div>
```

---

## Navigation (Keyboard)

Arrow keys (← →), Space, Home, End. Dot nav on right edge.

```javascript
document.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowRight' || e.key === ' ') nextSlide();
  if (e.key === 'ArrowLeft') prevSlide();
  if (e.key === 'Home') goToSlide(0);
  if (e.key === 'End') goToSlide(slides.length - 1);
});
```
