# ARK Portal Publications Management

## GH Actions Workflows

### Monthly Queries Cron Workflow

`.github/workflows/monthly-queries-cron.yml`

This repository includes a GitHub Actions workflow (`monthly-queries-cron`) 
that automates the generation and publication of updated query results.

**What it does**
- Runs a Python script (`main.py`) to generate or update query outputs (`publication_updates.csv`, `new_publications.csv`)
- Detects whether the script produced any changes
- If changes are found:  
  - Commits updates to the `query-results` branch  
  - Automatically opens a pull request into `main` for review

**When it runs**
- cron Schedule: First day of every month at midnight PDT  
- Manual trigger: Can be run from the GitHub Actions UI with a custom commit message

**Workflow Steps**
1. Checkout repository (using service account credentials)
2. Set up Python and install dependencies
3. Run `main.py` to generate updated results
4. Check for changes in repo
5. If changed detected, push updates to new branch `query-results` and create PR with @jmvera255 tagged for review and approval to merge into main







