# Gitflow

All about this project Git branching model.

Our branching model is based on [Gtiflow Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow),
and another one  [Vincent Driessen](https://nvie.com/posts/a-successful-git-branching-model/).

## Main Branches

- `main`
- `develop`

## Release Branches

- `release/$version` (e.g. release/1.2.1)

## Hotfix Branches

- `hotfix/$version` (e.g. hotfix/1.2.1-hf1)

## The coding flow

- A `develop` branch is created from `main`
- A `release` branch is created from `develop`
- `Feature` branches are created from `develop`
- When a `feature` is complete it is merged into the `develop` branch
- When the `release` branch is done it is merged into `develop` and `main`
- If an issue in `main` is detected a hotfix branch is created from `main`
- Once the `hotfix` is complete it is merged to both `develop` and `main`
- The release tag will be applied on the `main` branch

## The CI/CD

- The `develop` branch will be deployed to the DEV environment automatically
- `release/$version` branches will be deployed to the STAGING environment `manually`
- `hotfix/$version` branches will be deployed to the STAGING environment `manually`
- The `main` branch will be deployed to the PRODUCTION environment `manually`
- Using a tag to trigger the release pipeline instead of via a code merge.

# Conventions

## Commit messages

- AVOID `robotic commit` (e.g should not copy exactly the title of the task and repeat it for every related commit)
- AVOID `lazy` and `meaningless` commits like `update` `test` `fix` `continue`
- MUST make it humanized as much as possible: The code commit message must be from your mind, your words.
- MUST keep in mind: What you have done is what you write.
- MUST include the `task ID` in the commit message.

### Good commit message examples: 

- PROJ-1234 make a minor change to decorate the form
- Fix the border to make it thinner PROJ-1523

### Bad commit messasge examples:

- Update
- Test
- Continue
- Fixed

## Pull (merge) request conventions

### Default template

Ensure this default [merge request template](.gitlab/merge_request_templates/default.md) is deployed to the GitLab repository.