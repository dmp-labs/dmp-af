# dmp-af Documentation

This directory contains the source for the dmp-af documentation website, built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

## Quick Start

### Prerequisites

- [Dagger CLI](https://docs.dagger.io/install) installed
- Docker running locally

All documentation dependencies are managed automatically by Dagger containers.

### Local Development Server

Run the docs locally with live reload:

```bash
make docs-serve
# or
make serve
```

Then open http://127.0.0.1:8000 in your browser.

Changes to markdown files will automatically reload in the browser.

### Build Static Site

Generate the static HTML site:

```bash
make docs-build
# or
make build
```

Output will be in the `site/` directory.

### Makefile Commands

The `Makefile` provides convenient commands:

```bash
make help             # Show all available commands
make docs-serve       # Start dev server
make docs-build       # Build production site
make docs-test        # Test build (validates links)
make docs-clean       # Remove site/ directory
```

## Documentation Structure

```
docs/
├── index.md                  # Landing page
├── getting-started/          # Installation and setup
├── tutorials/                # Step-by-step guides
├── features/                 # Feature overviews
├── configuration/            # Configuration reference
├── reference/                # API and technical reference
├── development/              # Contributing and development
└── static/                   # Images and assets
```

## Writing Documentation

### Markdown Features

MkDocs Material supports many extensions. Some useful ones:

#### Admonitions

```markdown
!!! note "Optional Title"
    This is a note.

!!! tip
    This is a tip.

!!! warning
    This is a warning.
```

#### Code Blocks

````markdown
```python
def hello():
    print("Hello, world!")
```
````

With line highlighting:

````markdown
```python hl_lines="2"
def hello():
    print("Hello, world!")  # This line is highlighted
```
````

#### Tabs

```markdown
=== "Tab 1"
    Content for tab 1

=== "Tab 2"
    Content for tab 2
```

#### Links

```markdown
[Link text](../other-page.md)
[External link](https://example.com)
```

### Style Guide

- Use sentence case for headings ("Getting started" not "Getting Started")
- Keep paragraphs short (2-3 sentences)
- Use code blocks for all code examples
- Include examples for every feature
- Link to related pages at the end of each page

### Adding Images

Place images in `docs/static/` and reference them:

```markdown
![Alt text](../static/image.png)
```

## Configuration

Documentation configuration is in `mkdocs.yml` at the repository root.

### Navigation

Update the `nav:` section to add or reorganize pages:

```yaml
nav:
  - Home: index.md
  - Getting Started:
    - getting-started/index.md
    - Installation: getting-started/installation.md
```

### Theme Customization

The theme is configured in `mkdocs.yml`:

```yaml
theme:
  name: material
  palette:
    primary: indigo
    accent: indigo
  features:
    - navigation.tabs
    - search.suggest
```

## Contributing

When contributing documentation:

1. Create a new branch
2. Make your changes
3. Test locally with `make docs-serve`
4. Validate with `make docs-test` to check for errors
5. Submit a pull request

## Troubleshooting

### Port Already in Use

If port 8000 is taken, modify the port in the Dagger call:

```bash
dagger -m .ci call docs serve --port=8001 up --ports=8001:8001
```

### Broken Links

Validate documentation build and check for broken links:

```bash
make docs-test
```

This will fail on any broken internal links or warnings.

### Build Issues

If you encounter build issues, try:

```bash
# Clean previous builds
make docs-clean

# Rebuild from scratch
make docs-build
```

All dependencies are managed in containers, so local environment issues are minimized.

## Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [Markdown Guide](https://www.markdownguide.org/)
