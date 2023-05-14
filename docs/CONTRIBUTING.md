# How to contribute to the Cifonauta database

Cifonauta is an open platform and welcomes suggestions and contributions from all.

## Report an issue

Create a new issue in the [issue tracker](https://github.com/bruvellu/cifonauta/issues) describing the problem and, if possible, with a link to the page where the issue is happening.

## Contribute code

If you want to fix a bug or create a new feature yourself, you can do so by submitting a pull request.
We recommend that you:

1. Fork [Cifonauta’s repository](https://github.com/bruvellu/cifonauta/fork).
This will create a copy of the entire repository in your account.
2. Clone the repository locally using `git clone git@github.com:<youruser>/cifonauta.git`
3. Install the required libraries and packages following the [local install](local-install.md) instructions.
4. Create a new branch off the default `develop` branch to develop your feature/bugfix.
Use a descriptive name such as `new-map-visualization` or `fix-navigation-ux`.
5. Create a pull request to the `develop` branch in the main Cifonauta repository.

### Branching strategy

- **`develop`**: Default branch.
Features and bug fixes should branch off `develop` and be merged back via pull requests.
Make your features as concise as possible to avoid merging large chunks of code at once.
If you are a collaborator, first push your local feature/bugfix branch to remote for automated testing, code review and discussion.
This is just a precaution step and a way to see the features in development; no approval is needed to push to `develop` (it’s ok if it breaks occasionally).
In case everything seems fine, merge locally back to `develop` and push to remote.
- **`production`**: Production branch. This branch holds the current code for the live website in production. The branch is protected (pushing to it directly is not possible). Features from `develop` are merged to `production` via pull requests.
- **`legacy`**: Previous production branch, now a legacy branch. It’s also protected and should not be changed.

### Commit messages

The preferred language for code comments and commit messages is English.
Please follow this guide on [How to Write a Git Commit Message](https://cbea.ms/git-commit/).
In summary:

- First line should be short and summarize the changes.
- Capitalize the first word and don’t use a period at the end.
- Use the imperative: “**Fix** user form auth exception” instead of “**Fixed**” or “**Fixes**”.
- If needed, add a more detailed description below the subject line.

