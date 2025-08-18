---
title: Notebooks
layout: default
permalink: /notebooks/
---

# Notebooks

> ⚙️ **First time here?** Please follow the [Conda environment setup instructions]({{ site.baseurl }}/conda-setup/) before running the notebooks in JupyterLab.
<br>
You can run notebooks in [Google Colab](https://colab.research.google.com/), view them on GitHub, or download and open them locally (e.g., JupyterLab, VS Code).

{% assign owner  = site.repo_owner  | default: 'QMCSoftware' %}
{% assign name   = site.repo_name   | default: 'MATH565Fall2025' %}
{% assign branch = site.repo_branch | default: 'main' %}

{%- assign files = site.static_files | sort: 'name' -%}
<ul>
{% for nb in files %}
  {% if nb.path contains '/notebooks/' and nb.extname == '.ipynb' %}
    {% assign rel = nb.path | replace: site.baseurl, '' | remove_first: '/' %}
    {% assign pretty = nb.name | replace: '.ipynb','' | replace: '_',' ' %}

    {% assign colab = 'https://colab.research.google.com/github/' | append: owner | append: '/' | append: name | append: '/blob/' | append: branch | append: '/' | append: rel %}
    {% assign gh    = 'https://github.com/' | append: owner | append: '/' | append: name | append: '/blob/' | append: branch | append: '/' | append: rel %}

    <li>
      <strong>{{ pretty }}</strong>
      <div style="margin-left:0.5rem;">
        <a href="{{ nb.path | relative_url }}" download>Download</a> ·
        <a href="{{ colab }}" target="_blank" rel="noopener">Colab</a> ·
        <a href="{{ gh }}"    target="_blank" rel="noopener">GitHub</a>
      </div>
    </li>
  {% endif %}
{% endfor %}
</ul>