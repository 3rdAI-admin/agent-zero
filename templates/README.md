# Penetration Testing Templates

This directory contains reusable templates for Th3rdAI penetration testing reports and documentation.

## 📁 Available Templates

### 1. Findings Summary Table (Markdown)
**File**: `pentest-findings-table-template.md`

- **Format**: Markdown
- **Best for**: Quick documentation, GitHub/GitLab wikis, text-based reports
- **Features**: Simple table format with emoji severity indicators

**Usage**:
```bash
# Copy to your project
cp templates/pentest-findings-table-template.md ./pentest-findings.md

# Edit with your findings
vim ./pentest-findings.md
```

### 2. Findings Summary Table (HTML)
**File**: `pentest-findings-table-template.html`

- **Format**: HTML with CSS styling
- **Best for**: Professional reports, PDF export, client deliverables
- **Features**:
  - Responsive design
  - Color-coded severity badges
  - Proper text wrapping
  - Print-optimized styling
  - Professional appearance

**Usage**:
```bash
# Open in browser
open templates/pentest-findings-table-template.html

# Or copy to your project
cp templates/pentest-findings-table-template.html ./pentest-report.html
```

**Export to PDF**:
1. Open the HTML file in Chrome/Edge
2. Press `Ctrl+P` (Windows) or `Cmd+P` (Mac)
3. Select "Save as PDF"
4. Adjust margins if needed
5. Save

## 🎨 Customization

### HTML Template Customization

**Change Colors**:
Edit the CSS variables in the `<style>` section:
```css
.severity-critical { background-color: #e74c3c; }  /* Red */
.severity-high     { background-color: #e67e22; }  /* Orange */
.severity-medium   { background-color: #f39c12; }  /* Yellow */
.severity-low      { background-color: #27ae60; }  /* Green */
.severity-info     { background-color: #3498db; }  /* Blue */
```

**Adjust Column Widths**:
```css
.findings-table th:nth-child(3),
.findings-table td:nth-child(3) {
    width: 38%;  /* Title column */
}
```

**Add Company Logo**:
Add to the header section:
```html
<div class="header">
    <img src="path/to/logo.png" alt="Company Logo" style="height: 50px;">
    <h1>🔒 Penetration Test Findings Summary</h1>
</div>
```

## 📊 Severity Levels

| Level | Color | When to Use |
|-------|-------|-------------|
| 🔴 Critical | Red | Immediate action required. Complete system compromise possible |
| 🟠 High | Orange | Remediate ASAP. Significant security risk |
| 🟡 Medium | Yellow | Address in planned updates |
| 🟢 Low | Green | Minor concern. Routine maintenance |
| 🔵 Info | Blue | Informational. Defense-in-depth opportunities |

## 🔗 OWASP Top 10 2021

Quick reference for the most common categories:

- **A01**: Broken Access Control
- **A02**: Cryptographic Failures
- **A03**: Injection
- **A04**: Insecure Design
- **A05**: Security Misconfiguration
- **A06**: Vulnerable and Outdated Components
- **A07**: Identification and Authentication Failures
- **A08**: Software and Data Integrity Failures
- **A09**: Security Logging and Monitoring Failures
- **A10**: Server-Side Request Forgery (SSRF)

## 📝 Best Practices

1. **Clear Titles**: Use descriptive, actionable titles
   - ✅ "Unauthenticated Code Execution via /api/launch"
   - ❌ "Security Issue"

2. **Specific Locations**: Include exact endpoints, files, or services
   - ✅ "POST /api/launch, GET /api/config"
   - ❌ "API"

3. **Accurate Severity**: Base on actual impact and exploitability
   - Consider: Confidentiality, Integrity, Availability impact
   - Factor in: Ease of exploitation, attack surface

4. **OWASP Mapping**: Map to relevant OWASP categories
   - Multiple categories are acceptable (e.g., A02, A05)
   - Use "Info" for non-security findings

## 🚀 Quick Start

```bash
# Create a new pentest report
mkdir my-pentest-2026-03-14
cd my-pentest-2026-03-14

# Copy HTML template
cp ../templates/pentest-findings-table-template.html ./findings.html

# Edit findings
# Open findings.html in your editor and update the table rows

# Preview
open findings.html

# Export to PDF when ready
# Use browser print function (Cmd+P / Ctrl+P)
```

## 📧 Contact

**Organization**: Th3rdAI
**Email**: agentz@th3rdai.com
**Branding**: https://drive.google.com/drive/folders/1T1agtMdgNX0lXUuigGKa7E1fGfvqMgMY

---

**Version**: 1.0
**Last Updated**: 2026-03-14
**Created by**: Agent Zero (Claude Code)
