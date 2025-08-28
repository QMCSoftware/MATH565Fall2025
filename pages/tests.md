---
title: Tests & Exams
layout: default
permalink: /tests/
description: Test dates, exam info, and archive of past tests.
---

Below are the planned tests and exams for the semester, with links to PDFs as they become available. An automatic archive of old tests appears further down.

Tip: Put the current semester PDFs in `assets/tests/current/` (or edit the paths below). Put old tests in `assets/tests/archive/` to populate the archive list automatically.

## This semester's tests and exams

Date       | Assessment | Coverage / Notes                     | PDF                                                                 | Solutions
---------- | ---------- | ------------------------------------- | ------------------------------------------------------------------- | ---------
2025-010-?? | Test 1     | TBD                | <!-- Example reference:[PDF]({{ '/assets/tests/current/MATH565_Fa2025_Test1.pdf' | relative_url }}) -->


---

## Old tests (automatic archive)

This semester's tests may bear some resemblance to the old ones, but topics covered and course emphases change from year to year.

<!-- The list below is generated automatically from files in `assets/tests/archive/`.  
Any PDF you drop there will appear here without editing this page.-->

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

