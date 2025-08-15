---
title: Assignments
layout: default
permalink: /assignments/
---
# Assignments
<table>
  <thead><tr><th>Assignment</th><th>Due</th></tr></thead>
  <tbody>
  {% assign items = site.assignments %}
  {% for a in items %}
    <tr>
      <td><a href="{{ a.url | relative_url }}">{{ a.title }}</a></td>
      <td>{% if a.due %}{{ a.due }}{% else %}&mdash;{% endif %}</td>
    </tr>
  {% endfor %}
  </tbody>
</table>