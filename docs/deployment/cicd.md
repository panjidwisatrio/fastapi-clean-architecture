# CI/CD Pipeline

Automated testing and deployment workflows.

## GitHub Actions

### Basic CI Workflow

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
          SECRET_KEY: test-secret-key
        run: |
          pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### CD to Docker Hub

Create `.github/workflows/docker.yml`:

```yaml
name: Docker Build and Push

on:
  push:
    tags:
      - 'v*'

jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: yourusername/fastapi-app:latest,yourusername/fastapi-app:${{ github.ref_name }}
```

### Deploy to Heroku

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Heroku

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: akhileshns/heroku-deploy@v3.12.14
        with:
          heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
          heroku_app_name: "your-app-name"
          heroku_email: "your-email@example.com"
```

## GitLab CI/CD

Create `.gitlab-ci.yml`:

```yaml
stages:
  - test
  - build
  - deploy

variables:
  POSTGRES_DB: test_db
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres

test:
  stage: test
  image: python:3.11
  services:
    - postgres:15
  before_script:
    - pip install -r requirements.txt
    - pip install pytest pytest-cov
  script:
    - pytest --cov=app
  coverage: '/TOTAL.*\s+(\d+%)$/'

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t registry.gitlab.com/username/fastapi-app .
    - docker push registry.gitlab.com/username/fastapi-app
  only:
    - main

deploy:
  stage: deploy
  script:
    - echo "Deploy to production"
  only:
    - main
  when: manual
```

## Jenkins Pipeline

Create `Jenkinsfile`:

```groovy
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/yourusername/fastapi-clean-architecture.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    pip install pytest
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest
                '''
            }
        }

        stage('Build Docker') {
            steps {
                sh 'docker build -t fastapi-app .'
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    docker-compose down
                    docker-compose up -d
                '''
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
```

## CircleCI

Create `.circleci/config.yml`:

```yaml
version: 2.1

jobs:
  test:
    docker:
      - image: python:3.11
      - image: postgres:15
        environment:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db

    steps:
      - checkout

      - run:
          name: Install dependencies
          command: |
            pip install -r requirements.txt
            pip install pytest

      - run:
          name: Run tests
          command: pytest

  deploy:
    machine: true
    steps:
      - checkout

      - run:
          name: Deploy to server
          command: |
            ssh user@server "cd /app && git pull && docker-compose up -d"

workflows:
  version: 2
  test_and_deploy:
    jobs:
      - test
      - deploy:
          requires:
            - test
          filters:
            branches:
              only: main
```

## Automated Database Migrations

Add migration step to CI/CD:

```yaml
- name: Run migrations
  run: |
    alembic upgrade head
```

## Environment Secrets

### GitHub Secrets

Add in repository settings:

- `DATABASE_URL`
- `SECRET_KEY`
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`
- `HEROKU_API_KEY`

### GitLab CI/CD Variables

Add in Settings > CI/CD > Variables

### Use Secrets in Workflow

```yaml
- name: Deploy
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
    SECRET_KEY: ${{ secrets.SECRET_KEY }}
  run: |
    ./deploy.sh
```

## Notifications

### Slack Notifications

```yaml
- name: Slack Notification
  uses: rtCamp/action-slack-notify@v2
  env:
    SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
    SLACK_MESSAGE: 'Deployment completed!'
```

### Email Notifications

```yaml
- name: Send email
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 587
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: Build ${{ job.status }}
    body: Build completed with status ${{ job.status }}
    to: team@example.com
```

## Best Practices

- Run tests on every commit
- Use separate staging environment
- Automate database migrations
- Store secrets securely
- Use semantic versioning tags
- Implement rollback strategy
- Monitor deployments
- Cache dependencies for speed

## Rollback Strategy

```yaml
- name: Rollback on failure
  if: failure()
  run: |
    docker-compose down
    git checkout main~1
    docker-compose up -d
```

See [Production Deployment](production.md) for deployment details.
