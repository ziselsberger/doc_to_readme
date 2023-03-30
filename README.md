# Automatic Module Documentation in README

## What's this?

Automated docstring extraction and creation/update of module documentation in README File.

### Why?

Because it's nice :-)

### How?

[doc_to_md.py](src/doc_to_md.py) loops through all Python files in the Repository and extracts the function calls + the
corresponding short description from the docstrings. These are added to a dictionary and afterwards converted to
Markdown Table.  
Finally, the section 'Functions & Classes' is appended / updated in the README File.

**Open TODOs:**

- add Unittests

### Where?

Works in GitLab, Bitbucket & GitHub :-) Yay!
> * The Pipeline YAML files differ a little bit, so pay attention to the infos below :-)
> * This pipe-internal `*push` script  checks for changes (using git status) and if so, commits and pushes the changes in the README File.

### GitHub

The least complicated one :-)

1. **Add dir `.github/workflows`**

2. **Create [Workflow file (.yml)](.github/workflows/update_readme.yml)**

    - https://medium.com/@michaelekpang/creating-a-ci-cd-pipeline-using-github-actions-b65bb248edfe
    - https://joht.github.io/johtizen/build/2022/01/20/github-actions-push-into-repository.html

```yaml
name: Update README.md

on:
  push:
    branches:
      - main

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

#### Some further info:

- In contrast to GitLab and Bitbucket no access token is needed.
- To skip the Pipeline `[skip ci]` is added to the commit message.

---

### GitLab

Super helpful blog post on how to update files in Repo within CI/CD
Pipeline: https://parsiya.net/blog/2021-10-11-modify-gitlab-repositories-from-the-ci-pipeline/

#### How to update files within GitLab Pipeline:

1. **Add Project Access Token**: Settings > `Access Tokens`

   ![](images/create_project_access_token_medium.png)  
   ![](images/project_access_token.png)


2. **Add GIT_PUSH_TOKEN to CICD Variables**: Settings > `CICD` > Variables

   ![](images/cicd_variables.png)

    * **Key** = GIT_PUSH_TOKEN
    * **Value** = Access Token
    * **Type** = Variable
    * `[x] Mask variable`!


3. **Create [GitLab Pipeline](.gitlab-ci.yml)**

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
    git config --global user.name "${BOT_NAME}"
    git config --global user.email "${BOT_EMAIL}"
    git add ../README.md
    git commit -m "${COMMIT_MESSAGE}"
    git push -o ci.skip "https://${BOT_NAME}:${GIT_PUSH_TOKEN}@${CI_REPOSITORY_URL#*@}" $BRANCH_NAME
  fi 

update_docu:
  image: alpine:latest
  before_script:
    - apk add bash git
    - apk add --no-cache python3
    - git config --global pull.rebase false
    - git fetch
    - git checkout $BRANCH_NAME
    - git pull
    - cd ./src
  script:
    - python doc_to_md.py
    - *push
```

#### Some further info:

- Environment variables: `GIT_PUSH_TOKEN` (Repository Access Token) and `CI_REPOSITORY_URL`
- Local variables are listed in the YAML File.
- It's necessary to set the git user.name and user.email
- It's necessary to check out the main branch and pull again, otherwise a merge conflict happens.
- `-o ci.skip` is necessary for not triggering the CI again (and again) with the update of the README File

---

### Bitbucket

#### How to update files within Bitbucket Pipeline:

1. **Enable Pipelines**: Repository Settings > `PIPELINES` > Settings

2. **Create Repository Access Token**: Repository Settings > `SECURITY` > Access tokens

   ![](images/access_token_info.png)

   **Scopes** > `Repositories`  
   [x] read   
   [x] write


3. **Add Repository Variables**: Repository Settings > `PIPELINES` > Repository Variables

   ![](images/repo_variables.png)

* **GIT_PUSH_TOKEN** = Access Token (**secure!**)
* **BRANCH_NAME** = Branch to be updated automatically
* **REPO_URL** = URL without https://


4. **Create [Bitbucket Pipeline](bitbucket-pipelines.yml)**

```yaml
image: alpine:latest

pipelines:
  default:
    - step:
        name: update_docu
        .push: &push |
          lines=$(git status -s | wc -l)
          if [ $lines -gt 0 ];then
            git add ../README.md
            git commit -m "Auto-update README.md [skip ci]"
            echo "git push 'https://x-token-auth:${GIT_PUSH_TOKEN}@${REPO_URL}' ${BRANCH_NAME}"
            git push "https://x-token-auth:${GIT_PUSH_TOKEN}@${REPO_URL}" $BRANCH_NAME
          fi 
        script:
          - apk add bash git
          - apk add --no-cache python3
          - git fetch
          - cd ./src
          - python3 doc_to_md.py
          - *push
```

#### Some further info:

- All variables are stored as repository variables.
- The **User** in the git push command has to be **x-token-auth**.
- Bitbucket does not allow push options like GitLab (`-o ci.skip`).  
  To skip the Pipeline you have to add `[skip ci]` or `[ci skip]` to the commit message.

## Functions & Classes  
| Module | Type | Name/Call | Description |
| --- | --- | --- | --- |
| [main](./main.py) | function  | `hello_world()` | Just says hello |
| [functions](./src/functions.py) | function  | `mean(x: int = 1, y: int = 2) -> float` | Calculate mean of x and y. |
| [functions](./src/functions.py) | function  | `add(x: int = 4, y: int = 5) -> int` | Add two numbers (x and y). |
| [functions](./src/functions.py) | function  | `multiply(x: int = 6, y: int = 7) -> int` | Multiply two numbers (x and y). |
| [run_qc_checks](./src/run_qc_checks.py) | class  | `TechnicalQualityTests` | Base class for all technical QC Tests. |
| [run_qc_checks](./src/run_qc_checks.py) | method (TechnicalQualityTests) | `reference_file(self) -> str` | Updates path to reference file, in case placeholders are used, which need to be replace for every file, that shall be checked. e.g. when the filename includes a Tile ID. |
| [run_qc_checks](./src/run_qc_checks.py) | method (TechnicalQualityTests) | `add_to_dict(self, test_name: str, test_result: Tuple[bool, str]) -> None` | Add QC result to dictionary. |
| [run_qc_checks](./src/run_qc_checks.py) | method (TechnicalQualityTests) | `execute_test(self, test_name: str, func: Callable[..., Any], inp: Union[str, RasterProfile, DatasetReader], specification: Optional[Any] = '', header: Optional[str] = '', **kwargs) -> None` | Run QC function and write results in a dictionary. |
| [run_qc_checks](./src/run_qc_checks.py) | method (TechnicalQualityTests) | `run_qc(self)` | Run QC checks |
| [run_qc_checks](./src/run_qc_checks.py) | method (TechnicalQualityTests) | `finalise_qc(self) -> dict` | Finalise QC checks. |
| [run_qc_checks](./src/run_qc_checks.py) | method (TechnicalQualityTests) | `tests(self) -> None` | Includes all QC checks (independent of data format). Only those checks are executed, where a specification could be extracted from the config file. |
| [run_qc_checks](./src/run_qc_checks.py) | function  | `main(config_file=None, test_input=None)` | None |

---
**Created:** 2023-03-15  
**Last Update:** 2023-03-29