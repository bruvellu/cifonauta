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

### Branching strategy

- **`develop`**: Default branch.
Features and bug fixes should branch off `develop` and be merged back via pull requests.
Make your features as concise as possible to avoid merging large chunks of code at once.
If you are a collaborator, first push your local feature/bugfix branch to remote for automated testing, code review and discussion.
This is just a precaution step and a way to see the features in development; no approval is needed to push to `develop`—*it’s ok if it breaks occasionally*.
In case everything seems fine, merge locally back to `develop` and push to remote.
- **`staging`**: Staging branch. That’s where the mature features are first merged for testing. Merge must be done via pull requests. The `staging` branch has integrated tests and deploys to a test server to check for potential issues.
- **`production`**: Production branch. This branch holds the current code for the live website in production. Once features have been thoroughly tested on `staging`, they are ready for `production`. The branch is protected and merging from staging must be done via pull requests (never push to `production` directly).
- **`legacy`**: Previous production branch, now a legacy branch. It’s also protected and should not be changed.

### Commit messages

The preferred language for code comments and commit messages is English.
Please follow this guide on [How to Write a Git Commit Message](https://cbea.ms/git-commit/).
In summary:

- First line should be short and summarize the changes.
- Capitalize the first word and don’t use a period at the end.
- Use the imperative: “**Fix** user form auth exception” instead of “**Fixed**” or “**Fixes**”.
- If needed, add a more detailed description below the subject line.

