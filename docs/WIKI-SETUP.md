# Wiki Setup Complete

This document describes the wiki setup and synchronization process.

## What Was Done

### 1. Documentation Organization
All documentation files have been moved to the `docs/` folder:

- **Home.md** - Main wiki home page (project overview)
- **User-Guide.md** - Complete user guide (renamed from index.md)
- **Architecture.md** - System architecture
- **Contributing.md** - Development guidelines
- **Index.md** - Documentation index
- **Build-Complete.md** - Build completion report
- **Phase1-Complete.md** - Phase 1 deliverables
- **Verification-Checklist.md** - QA checklist
- **File-Manifest.md** - File listing
- **Summary.md** - Project summary
- **Evaluation-Report.md** - Application evaluation

### 2. GitHub Workflow
Created `.github/workflows/sync-wiki.yml` that:

- Automatically syncs `docs/` folder to GitHub Wiki
- Triggers on pushes to `main` branch when `docs/` files change
- Can be manually triggered via `workflow_dispatch`
- Converts internal links to wiki format (removes `.md` extensions)
- Handles wiki repository initialization if it doesn't exist

### 3. Updated References
- Updated `README.md` to reference `docs/` instead of root-level files
- Updated `docs/Index.md` to use wiki-style links
- All internal documentation links now use wiki format

## How It Works

### Automatic Sync
When you push changes to `docs/` on the `main` branch:

1. GitHub Actions workflow triggers
2. Clones the wiki repository
3. Copies all `.md` files from `docs/` (except README.md)
4. Fixes internal links to wiki format
5. Commits and pushes to wiki

### Manual Sync
You can manually trigger the sync:

1. Go to Actions tab in GitHub
2. Select "Sync Documentation to Wiki"
3. Click "Run workflow"

### Wiki Link Format
In wiki pages, use page names without `.md`:

```markdown
[User Guide](User-Guide)
[Architecture](Architecture)
[Contributing](Contributing)
```

The workflow automatically converts:
- `](file.md)` → `](file)`
- `](docs/file.md)` → `](file)`

## Adding New Documentation

1. Create a new `.md` file in `docs/`
2. Use descriptive names (spaces become hyphens in URLs)
3. Update `docs/Index.md` to include the new page
4. Commit and push - workflow will sync automatically

## Viewing Documentation

- **Local**: View files in `docs/` folder
- **GitHub Wiki**: https://github.com/azcoigreach/nagatha_core/wiki
- **GitHub Repository**: Files in `docs/` folder

## Notes

- The wiki repository is separate from the main repository
- Wiki pages are stored in a git repository at `https://github.com/azcoigreach/nagatha_core.wiki.git`
- The workflow uses `GITHUB_TOKEN` which is automatically available
- First sync may fail if wiki doesn't exist - it will be created on first push

## Troubleshooting

### Workflow Fails
- Check that wiki is enabled in repository settings
- Verify `GITHUB_TOKEN` has write permissions
- Check workflow logs for specific errors

### Links Not Working
- Ensure links use wiki format (no `.md` extension)
- Check that page names match exactly (case-sensitive)
- Verify the page exists in the wiki

### Changes Not Syncing
- Verify files are in `docs/` folder
- Check that workflow is enabled
- Ensure you're pushing to `main` branch
- Check workflow logs for errors
