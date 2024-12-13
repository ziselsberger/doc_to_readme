## Set up a pipeline to update README on every push

> * [GitHub](#github)
> * [GitLab](#gitlab)

### GitHub

#### 1. Add dir `.github/workflows`

#### 2. Create [Workflow file (.yml)](.github/workflows/update_readme.yml)

- In contrast to GitLab no access token is needed.
- To avoid an infinite loop of updates, `[skip ci]` is added to the commit message.
- `on: workflow_dispatch` adds the possibility to trigger the pipeline manually.

```yaml
name: Update README.md

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  update-docu:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Checkout Repo
        uses: actions/checkout@v2
      - name: Install Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Update README
        env:
          CI_COMMIT_MESSAGE: Auto-update README.md [skip ci]
          CI_COMMIT_AUTHOR: mjam
          CI_COMMIT_MAIL: ziselsberger@users.noreply.github.com
        run: |
          cd ./src
          python3 doc_to_md.py
          lines=$(git status -s | wc -l)
          if [ $lines -gt 0 ];then
            git config --global user.name "${{ env.CI_COMMIT_AUTHOR }}"
            git config --global user.email "${{ env.CI_COMMIT_MAIL }}"
            git add ../README.md
            git commit -m "${{ env.CI_COMMIT_MESSAGE }}"
            git push
          fi
```

---

> [!TIP]
> - https://medium.com/@michaelekpang/creating-a-ci-cd-pipeline-using-github-actions-b65bb248edfe
> - https://joht.github.io/johtizen/build/2022/01/20/github-actions-push-into-repository.html

---

### GitLab

#### 1. Add [Project Access Token](images/project_access_token.png)

* Settings > `Access Tokens`
* **Scope**: [write_repository](images/create_project_access_token_medium.png)

#### 2. Add GIT_PUSH_TOKEN to [CICD Variables](images/cicd_variables.png)

* Settings > `CICD` > Variables

    * **Key** = GIT_PUSH_TOKEN
    * **Value** = Access Token
    * **Type** = Variable
    * `[x] Mask variable`!

#### 3. Create [GitLab Pipeline](.gitlab-ci.yml)

- CICD variables: `GIT_PUSH_TOKEN`, `CI_REPOSITORY_URL`
- Local variables are listed in the YAML File.
- Set `git config user.name` and `user.email`!
- It's necessary to check out the main branch and pull again to avoid a merge conflict. 
- The pipe-internal `*push` script checks for changes (using git status) and if so, commits and pushes the changes in
  the README File.
  - `-o ci.skip` is necessary for not triggering the CI again (and again) with the update of the README File

```yaml
variables:
  BRANCH_NAME: "main"
  BOT_NAME: "MJAM"
  BOT_EMAIL: "mjam@update_readme.com"
  COMMIT_MESSAGE: "Auto-update README.md"

.push: &push |
  git status
  lines=$(git status -s | wc -l)
  if [ $lines -gt 0 ];then
    git config user.name "${BOT_NAME}"
    git config user.email "${BOT_EMAIL}"
    git add $PATH_TO_README
    git commit -m "${COMMIT_MESSAGE}"
    git push -o ci.skip "https://${BOT_NAME}:${GIT_PUSH_TOKEN}@${CI_REPOSITORY_URL#*@}" $BRANCH_NAME
  fi 

update_docu:
  image: alpine:latest
  before_script:
    - apk add bash git
    - apk add --no-cache python3
    - git checkout $BRANCH_NAME
    - git pull --ff
    - cd ./src
  script:
    - python doc_to_md.py
    - *push
```

> [!TIP]
> Super helpful blog post on how to update files in Repo within CI/CD Pipeline:  
> https://parsiya.net/blog/2021-10-11-modify-gitlab-repositories-from-the-ci-pipeline/
