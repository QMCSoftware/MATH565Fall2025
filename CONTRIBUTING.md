# Contributing to MATH565Fall2025

Thank you for helping with this course repository!  
This guide explains how to **preview the Jekyll site locally** and how to **set up nbstripout** so that Jupyter notebooks don’t pollute commits with execution metadata.

---

## 🖥 Viewing This Jekyll Site Locally on macOS

### ✅ Prerequisites

Install the following:

- [Homebrew](https://brew.sh)
- Ruby (via Homebrew)
- Jekyll (via Homebrew)
- Bundler (Ruby gem)

```bash
brew install chruby ruby-install
ruby-install ruby 3.4.1
echo "source $(brew --prefix)/opt/chruby/share/chruby/chruby.sh" >> ~/.zshrc
echo "source $(brew --prefix)/opt/chruby/share/chruby/auto.sh" >> ~/.zshrc
echo "chruby ruby-3.4.1" >> ~/.zshrc   # run 'chruby' to confirm version
ruby -v
gem install jekyll
gem install bundler
```

### 📦 Set Up Your Local Environment

1. Clone or navigate to the repository:

   ```bash
   git clone https://github.com/QMCSoftware/MATH565Fall2025.git
   cd MATH565Fall2025
   ```

2. Create a `Gemfile` (if not already present):

   ```ruby
   source "https://rubygems.org"

   gem "github-pages", group: :jekyll_plugins
   ```

3. Install dependencies:

   ```bash
   bundle install
   ```

### ▶️ Serve the Site Locally

```bash
bundle exec jekyll serve
```

Visit the site in your browser:

```
http://localhost:4000
```

For automatic reload on file changes (Jekyll 4+ only):

```bash
bundle exec jekyll serve --livereload
```

---

## 📓 Notebook Contribution Guidelines

This repository uses [`nbstripout`](https://github.com/kynan/nbstripout) to strip Jupyter execution metadata and outputs from notebooks before commit.

### Setup (one time, after cloning)

Run the script below in the repo root:

```bash
pip install --upgrade nbstripout

git config --local filter.nbstripout.clean   'python -m nbstripout --extra-keys metadata.kernelspec metadata.language_info metadata.vscode metadata.colab metadata.widgets'

git config --local diff.ipynb.textconv   'python -m nbstripout -t --extra-keys metadata.kernelspec metadata.language_info metadata.vscode metadata.colab metadata.widgets'
```

This ensures:
- Notebook outputs and noisy metadata don’t show up in diffs or commits.
- Only *source cells* are versioned.

You can normalize notebooks at any time:

```bash
git ls-files '*.ipynb' -z | xargs -0 python -m nbstripout --force   --extra-keys metadata.kernelspec metadata.language_info metadata.vscode metadata.colab metadata.widgets
```

### Ignoring Checkpoints

Ensure `.gitignore` contains:

```
.ipynb_checkpoints/
```

---

## 📄 Notes

- Always check out the correct branch (e.g., `draft`) before serving the site:

  ```bash
  git checkout draft
  ```

- If your site uses additional plugins or configuration files (e.g., `_config_dev.yml`), update the `jekyll serve` command accordingly.

---

Happy contributing!
