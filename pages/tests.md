---
title: Tests & Exams
layout: default
permalink: /tests/
description: Test dates, exam info, and archive of past tests.
---

Below are the planned tests and exams for the semester, with links to PDFs as they become available. An automatic archive of old tests appears further down.

## This semester's tests and exams

Date       | Assessment | Coverage / Notes                                         | PDF
---------- | ---------- | -------------------------------------------------------- | ---
Sep 24     | Test 1     | Parts 1 Introduction and Part 2 Generating Samples       | [Test 1 questions + solutions]({{ '/assets/tests/current/MATH565Test1F25Answers.pdf' | relative_url }})
Oct 29       | Test 2   | Part 3 MCMC + Discrepancy and Part 4 Importance Sampling, Control Variates |

---

## Archived tests and exams

This semester's tests and exams may bear some resemblance to the old ones, but topics covered and course emphases change from year to year. There may be typos in these tests, and I will **not** be awarding extra credit if you find them, but I do appreciate it if you point it out.

<!-- The list below is generated automatically from files in `assets/tests/archive/`.
Any PDF you drop there will appear here without editing this page.-->

<details markdown="1">
  <summary><strong>🔎 How to search the Archive (PDFs) for keywords</strong></summary>

*Goal:* find which past exams mention a term (e.g., `Brownian`, `Sobol`, `CLT`) inside PDF files.

### Mac (Homebrew) / Linux

1) Install once:
```bash
# macOS (Homebrew)
brew install pdfgrep

# Ubuntu/Debian Linux
sudo apt-get update && sudo apt-get install pdfgrep
```

2) From `MATH565Fall2025/assets/tests` (the folder that contains `archive`)), run:
```bash
# Case-insensitive, recursive, show filename + page number + context
pdfgrep -rniH -C2 'your term here' archive/
```
- `-r` = search subfolders  
- `-n` = show **page number**  
- `-i` = ignore case  
- `-H` = show **filename**  
- `-C2` = 2 lines of context

**Examples**
```bash
pdfgrep -rniH -C2 'brownian' archive/
pdfgrep -rniH -C2 'sobol' archive/
pdfgrep -rniH -C2 'central limit|CLT' archive/
```

### Windows (quick options)

**A) WSL (recommended):**
```powershell
wsl --install
```
Then in Ubuntu (WSL):
```bash
sudo apt-get update && sudo apt-get install pdfgrep
cd /mnt/c/Users/<you>/path/to/MATH565Fall2025/assets/tests/
pdfgrep -rniH -C2 'your term here' archive/
```

**B) Cross-platform alternative (ripgrep-all):**
```bash
# macOS
brew install ripgrep-all poppler
rga -n -i -C2 'your term here' archive/
```
```powershell
# Windows (Scoop)
scoop install ripgrep-all
rga -n -i -C2 'your term here' archive/
```

**Tips**
- Put phrases in quotes, e.g. `'Monte Carlo'`.
- Try several terms with regex: `'variance|SD|std\. dev'`.
- Narrow to a subfolder/year, e.g. `archive/2019/` or midterms only.
</details>

<!-- End of HOW TO SEARCH section -->


<details open>
<summary><strong>Archive</strong></summary>

{% assign any_found = false %}
<ul>
{% for f in site.static_files %}
  {% if f.path contains '/assets/tests/archive/' and f.extname == '.pdf' %}
    {% assign any_found = true %}
    <li>
      <a href="{{ f.path | relative_url }}">{{ f.name | replace: '_', ' ' }}</a>
    </li>
  {% endif %}
{% endfor %}
</ul>

{% unless any_found %}
<p><em>No archived tests found yet. Add PDFs to <code>assets/tests/archive/</code>.</em></p>
{% endunless %}

</details>
