# How to contribute to the Cifonauta database

Cifonauta is an open platform and welcomes suggestions and contributions from everyone.

## Report an issue

Create a new issue in the [issue tracker](https://github.com/bruvellu/cifonauta/issues).
Describe the problem in detail and remember to add a link to the page where the issue is happening.
Follow the available template, it allow us to identify and solve the issue quicker.
Thanks for reporting!

## Suggest a feature

Open a [new issue](https://github.com/bruvellu/cifonauta/issues) and describe your idea.
We’re looking forward to hearing your thoughts!

## Contribute code

You can also fix a bug or create a new feature yourself, you can do so by submitting a pull request.
We recommend that you:

1. Fork [Cifonauta’s repository](https://github.com/bruvellu/cifonauta/fork).
This will create a copy of the entire repository in your account.
2. Clone the repository locally using `git clone git@github.com:<youruser>/cifonauta.git`
3. Install the required libraries and packages following the [local install](local-install.md) instructions.
4. Create a new branch off the default `develop` branch to develop your feature/bugfix.
Use a descriptive name such as `new-map-visualization` or `fix-navigation-ux`.
5. Create a pull request to the `develop` branch in the main Cifonauta repository.

If you are a collaborator, you don’t need to create a pull request for `develop`, but before merging you should push your local feature branch to remote for testing, review and discussion (see below).

### Branching strategy

We are using a simplified flow based on environment branches (see [GitLab Flow](https://docs.gitlab.com/ee/topics/gitlab_flow.html#environment-branches-with-gitlab-flow)).
It goes from `develop` -> `staging` -> `production` with new features branching off and being merged back into `develop` (default branch).

- **`develop`** (default):
This is where code development happens.
We aim to keep it as stable as possible, but it’s ok if it breaks occasionally.
To develop new features, create a new feature branch from `develop` using a descriptive name (see above).
After doing some coding, push this local branch to remote.
The earlier the better but, importantly, do it before merging with `develop`.
This allows others to get an overview of the features in development, and allows for some automated testing, code review, and discussion.
If all looks good, create a pull request, or locally merge your feature branch into `develop` and push it to remote.
Make your features as concise as possible to avoid merging large chunks of code at once.
- **`staging`**:
This is a (more) stable branch.
Mature features in `develop` get merged into `staging` for testing.
Here, merges must be done via pull requests.
The `staging` branch has integrated tests and deploys to a test server for identifying unforseen issues.
- **`production`**:
This is the stable branch.
It holds the code for the live website in production.
Only features thoroughly tested in `staging` are ready for being merged into `production`.
The branch is protected.
Merging from `staging` must be done via pull requests, never push to `production` directly.
- **`legacy`**:
This is the previous production branch.
It’s now a legacy branch that will be phased out.
It’s protected and should not be changed.

### Commit messages

The preferred language for code comments and commit messages is English.
Please follow this guide on [How to Write a Git Commit Message](https://cbea.ms/git-commit/).
In summary:

- First line should be short and summarize the changes.
- Capitalize the first word and don’t use a period at the end.
- Use the imperative: “**Fix** user form auth exception” instead of “**Fixed**” or “**Fixes**”.
- If needed, add a more detailed description below the subject line.

