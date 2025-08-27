# Viewing This Jekyll Site Locally on macOS

This guide explains how to view this GitHub Pages site locally using Jekyll on a Mac.

---

## ✅ Prerequisites

Ensure you have the following installed:

- [Homebrew](https://brew.sh)
- Ruby (via Homebrew)
- Jekyll (via Homebrew)
- Bundler (Ruby gem)

You can install them with:

```bash
brew install chruby ruby-install
ruby-install ruby 3.4.1
echo "source $(brew --prefix)/opt/chruby/share/chruby/chruby.sh" >> ~/.zshrc
echo "source $(brew --prefix)/opt/chruby/share/chruby/auto.sh" >> ~/.zshrc
echo "chruby ruby-3.4.1" >> ~/.zshrc # run 'chruby' to see actual version
ruby -v
gem install jekyll
gem install bundler
```

---

## 📦 Set Up Your Local Environment

### 1. Clone or navigate to the repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

### 2. Create a `Gemfile` (if not already present)

In the root of your site directory, create a file named `Gemfile` with this content:

```ruby
source "https://rubygems.org"

gem "github-pages", group: :jekyll_plugins
```

### 3. Install dependencies

```bash
bundle install
```

This installs the `github-pages` gem and ensures your local build matches what GitHub Pages will publish.

---

## ▶️ Serve the Site Locally

Run the following command from the project root:

```bash
bundle exec jekyll serve
```

Visit the site in your browser:

```
http://localhost:4000
```

The site will automatically rebuild if you make changes to the source files.

---

## 🛠 Optional: Enable LiveReload

To automatically refresh the browser on file changes (Jekyll 4+ only):

```bash
bundle exec jekyll serve --livereload
```

Then visit:

```
http://localhost:4000
```

---

## 📄 Notes

- Always check out the correct branch (e.g., `draft`) before serving:

```bash
git checkout draft
```

- If your site uses additional plugins or configuration files (e.g., `_config_dev.yml`), update the serve command accordingly.

---

Happy local previewing!
