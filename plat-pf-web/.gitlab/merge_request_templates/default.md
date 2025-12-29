When the developer creates the merge request, please ensure the checklists below are added to the PR description and that all the points are checked before asking the code owner to review them before merging.

- Codeowners, please update the checklist to fit your project characteristics.
- Developers, please override the checklist if your merge request is not development related.

## Process checklist

With this pull/merge request, I ensure:

- [ ] PR: Minimum conditions
    - The target `branch` to merge is correct.
    - No code `conflicts` when I created the PR.
    - If the implementation changes the UI, the `screenshots` are attached to the PR description or comments.
- [ ] PR: The `title`
    - The `title` begins with the task ID.
    - The `title` ends with the author's name IF it's created by another developer. E.g., `... the title (John Doe)`
    - Well-formed `title`: What we do what we say in the PR title.
- [ ] PR: The `changelog`
    - The `changelog` record has been appropriately updated with the exact text as the PR title.
    - The `changelog` record is in the correct location (in alphabetical order).
- [ ] PR: The `labels`
    - The `[Care]` tag has been considered for the **(1)** _PR title_, **(2)** _task title_, and **(3)** _changelog record_ if the implementation involves significant risk or uncertainty.
    - The `[Config]` tag has been considered for the **(1)** _PR title_, **(2)** _task title_, **(3)** _task description in the config section_, and **(4)** _changelog record_ IF the implementation changes configuration or environment variables.
    - The `[Migration]` tag has been considered for the **(1)** _PR title_, **(2)** _task title_, **(3)** _task description in the migration section_, and **(4)** _changelog record_ IF the implementation changes the database structure.
    - The `[Docs]` tag has been considered for the **(1)** _PR title_, **(2)** _task title_, **(3)** _task description in the documentation section_, **(4)** _PR description_, and **(5)** _the changelog record_ IF the implementation changes the documentation.
- [ ] The `tasks`
    - Task: The developer `implementation details` have been added to the task description.
    - Task: The developer `testing checklist` has been added to the task description.
- [ ] The `AI`
    - AI: Provide your outstanding prompts by the instructions given by the [AI.md](/AI.md)
    - AI: Ask AI to `review` the main code. The developer must then deal smartly with the AI recommendations.
    - AI: Ask AI to `suggest` code `comments` or `refactors` or `naming` conventions. The developer must then deal smartly with the AI recommendations.
- [ ] Help: Please understand the above terms. If you need an explanation, don't hesitate to contact the person handling them (mainly your direct supervisor, but it could be anyone on the team who learned this).

## Coding conventions checklist

This section can be changed by different projects (Look out! Codemasters.). But here are a few of the most generic rules:

- [ ] I have read and ensured all the points below are considered
    - Ensure the best (of your) `English` for the PR title.
    - Ensure the best (of your) `English` for variable, method, and class names.
    - For the private variable of a class, please use `_` as the prefix.
    - Ensure there is no variable with convention violation (the project's convention is `TheNameCanBeAlsoTheComment`  aka. as explicit as possible).
    - Ensure no typo in the name of the variables and methods (exception is acceptable, but you need to be very careful; we have a lot of `typo issues`).
    - Ensure no `redundant code or comments` in the codebase (useless code or comments should be removed).