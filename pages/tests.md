---
title: Tests & Exams
layout: default
permalink: /tests/
description: Test dates, exam info, and archive of past tests.
---

Below are the planned tests and exams for the semester, with links to PDFs as they become available. An automatic archive of old tests appears further down.


## This semester's tests and exams

Date       | Assessment | Coverage / Notes                     | PDF                                                                 
---------- | ---------- | ------------------------------------- | -------------------------------------------------------------------
Sep 24 | Test 1     | Parts 1 Introduction and Part 2 Generating Samples                | <!-- Example reference:[PDF]({{ '/assets/tests/current/MATH565_Fa2025_Test1.pdf' | relative_url }}) -->
TBD | Test 2 


---

## Archived tests and exams

This semester's tests and exams may bear some resemblance to the old ones, but topics covered and course emphases change from year to year.  There may be typos in these tests, and I will **not** be awarding extra credit if you find them, but I do appreciate it if you point it out.

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

