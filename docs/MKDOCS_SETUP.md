# MkDocs Documentation Setup

This document explains the MkDocs setup for BigQuery ETL Skills documentation.

## What's Been Set Up

### MkDocs Configuration

**File:** `mkdocs.yml`

- Material theme with dark/light mode
- Navigation structure for all skills and examples
- Search functionality
- Code highlighting
- GitHub integration

### GitHub Actions Workflow

**File:** `.github/workflows/deploy-docs.yml`

Automatically deploys documentation to GitHub Pages on push to main.

### Dependencies

**File:** `requirements.txt`

- mkdocs
- mkdocs-material
- pymdown-extensions

## Testing Locally

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Serve Documentation Locally

```bash
mkdocs serve
```

Then visit: http://127.0.0.1:8000

### Build Documentation

```bash
mkdocs build
```

This creates a `site/` directory with static HTML.

## Updating Documentation

### Adding a New Page

1. Create the markdown file in `docs/`
2. Add it to the nav in `mkdocs.yml`
3. Test locally with `mkdocs serve`
4. Commit and push

### Updating Existing Pages

1. Edit the markdown file
2. Test locally
3. Commit and push (auto-deploys)

### Updating Navigation

Edit the `nav:` section in `mkdocs.yml`

## Tips

- Use admonitions for notes, warnings, tips:
  ```markdown
  !!! note "Title"
      Content here
  ```

- Add code blocks with syntax highlighting:
  ````markdown
  ```python
  code here
  ```
  ````

- Link between pages:
  ```markdown
  [Link text](../other-page.md)
  ```

- Add images:
  ```markdown
  ![Alt text](../images/image.png)
  ```

## GitHub Pages URL

Once deployed, documentation will be available at:

**https://mozilla.github.io/bigquery-etl-skills/**

Temp link while private:
**https://friendly-adventure-1e683vz.pages.github.io/**

## Maintenance

- Keep documentation in sync with skill changes
- Update examples when workflows change
- Review and update periodically for accuracy
- Monitor GitHub Actions for build failures
