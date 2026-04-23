## Создание allure отчёта

# Вариант 1. Allure-отчёт на GitHub Pages

GitHub Pages позволяет публиковать Allure-отчёт как статический сайт, он будет доступен по публичному URL после каждого `git push`. История запусков сохраняется (по умолчанию последние 20 сборок).

### Как это работает

При каждом пуше в `main` GitHub Actions:
1. Запускает тесты на `ubuntu-latest`
2. Генерирует Allure-отчёт из результатов
3. Подтягивает историю предыдущих запусков из ветки `gh-pages`
4. Публикует обновлённый отчёт обратно в `gh-pages`

Результат доступен по адресу `https://ВАШ_АККАУНТ.github.io/ВАШ_РЕПОЗИТОРИЙ/`.

### Шаг 1. Включить GitHub Pages

1. Откройте репозиторий на GitHub
2. **Settings** → **Pages**
3. Source: **Deploy from a branch**
4. Branch: **gh-pages** / **/ (root)**
5. Нажмите **Save**

> Ветка `gh-pages` создаётся автоматически при первом запуске workflow.

#### Если ветка по какой-то причине не была создана автоматически, используйте консоль локально:
```bash
git checkout --orphan gh-pages
git reset --hard
git commit --allow-empty -m "Init gh-pages"
git push origin gh-pages
git checkout main
```
### Шаг 2. Создать workflow

Создайте файл `.github/workflows/test.yaml` со следующим содержимым в вашем репозитории:

```yaml
name: Test

on:
  push:
    branches:
      - "main"

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: Install Chrome
        run: |
          sudo apt-get update
          sudo apt-get install -y google-chrome-stable

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest --alluredir=allure-results
        env:
          CI: true

      - name: Get Allure history
        uses: actions/checkout@v4
        if: always()
        continue-on-error: true
        with:
          ref: gh-pages
          path: gh-pages

      - name: Generate Allure report
        uses: simple-elf/allure-report-action@master
        if: always()
        with:
          allure_results: allure-results
          allure_history: allure-history
          keep_reports: 20

      - name: Deploy to GitHub Pages
        if: always()
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_branch: gh-pages
          publish_dir: allure-history
```

### Шаг 3. Запустить

Сделайте коммит в ветку `main`, и workflow запустится автоматически. Прогресс видно во вкладке **Actions** репозитория.

После завершения отчёт будет доступен по адресу:
```
https://ВАШ_АККАУНТ.github.io/ВАШ_РЕПОЗИТОРИЙ/
```

### Переменные окружения в GitHub Actions

Если тесты требуют `SELENOID_URL` или другие секреты, добавьте их в **Settings** → **Secrets and variables** → **Actions** → **New repository secret**, затем передайте в workflow:

```yaml
      - name: Run tests
        run: pytest --alluredir=allure-results
        env:
          CI: true
          SELENOID_URL: ${{ secrets.SELENOID_URL }}
```

### Важные моменты

- `CI: true` - активирует headless-режим браузера в `conftest.py`, без него Chrome упадёт (нет дисплея)
- `permissions: contents: write` - обязательно, иначе workflow не сможет записать в ветку `gh-pages`
- `continue-on-error: true` на шаге получения истории - нужно для первого запуска, когда ветки `gh-pages` ещё нет
- `keep_reports: 20` - хранить историю последних 20 сборок (можно изменить)

### Локальная сборка allure отчёта:

1. Запустите выполнение тестов:
> pytest --alluredir=allure-results

2. Запустите скрипт для генерации отчёта локально:
> allure serve .\allure-results\

---

# Вариант 2. Jenkins + Selenoid + pytest + Allure

Локальная CI-среда для запуска автотестов на Python с генерацией Allure-отчётов и записью видео через Selenoid.

## Стек

| Компонент | Назначение |
|---|---|
| Jenkins | CI-сервер, запускает pipeline и хранит историю сборок |
| Selenoid | Запускает браузеры в Docker-контейнерах |
| Selenoid UI | Веб-интерфейс для наблюдения за сессиями браузеров |
| pytest + allure-pytest | Запуск тестов и сбор данных для отчёта |
| Allure Jenkins Plugin | Генерирует HTML-отчёт прямо в UI Jenkins |

## Предварительные требования

- Docker Desktop (Windows / macOS) или Docker Engine (Linux)
- Git

> ⚠️ **Windows + видео**: запись видео через Selenoid на Docker Desktop для Windows работает крайне нестабильно из-за особенностей WSL2. Видео гарантированно работает на macOS и Linux. На Windows рекомендуется использовать внешний Selenoid (в данном примере использовался `selenoid.autotests.cloud`) или облачный сервер.

---

## Структура файлов
В данном репозитории файлы для инфраструктуры находятся в папке "jenkins-docker/"
Данная папка не обязательна в репозитории, и находится здесь для примера в рамках изучения.
```
jenkins-docker/
├── Dockerfile          # Кастомный образ Jenkins с Python
├── docker-compose.yml  # Оркестрация всех сервисов
└── browsers.json       # Конфигурация браузеров для Selenoid
```

---

## Шаг 1. Подготовка файлов

### Dockerfile

Расширяем базовый образ Jenkins - добавляем Python:

```dockerfile
FROM jenkins/jenkins:lts-jdk25
USER root
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*
USER jenkins
```

### browsers.json

Конфигурация браузеров для Selenoid. Укажите нужные браузеры и версии:

```json
{
  "chrome": {
    "default": "128.0",
    "versions": {
      "128.0": {
        "image": "selenoid/chrome:128.0",
        "port": "4444",
        "path": "/",
        "recorder": {
          "image": "selenoid/video-recorder:latest-release"
        }
      }
    }
  },
  "firefox": {
    "default": "130.0",
    "versions": {
      "130.0": {
        "image": "selenoid/firefox:130.0",
        "port": "4444",
        "path": "/wd/hub",
        "recorder": {
          "image": "selenoid/video-recorder:latest-release"
        }
      }
    }
  },
  "MicrosoftEdge": {
    "default": "128.0",
    "versions": {
      "128.0": {
        "image": "browsers/edge:128.0",
        "port": "4444",
        "path": "/",
        "recorder": {
          "image": "selenoid/video-recorder:latest-release"
        }
      }
    }
  }
}
```

### docker-compose.yml

```yaml
services:

  jenkins:
    build: .
    container_name: jenkins
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - selenoid-network

  selenoid:
    image: aerokube/selenoid:latest
    container_name: selenoid
    ports:
      - "4444:4444"
    volumes:
      - ./browsers.json:/etc/selenoid/browsers.json
      - /var/run/docker.sock:/var/run/docker.sock
      - selenoid_video:/opt/selenoid/video
    environment:
      - DOCKER_API_VERSION=1.44
    command: [
      "-conf", "/etc/selenoid/browsers.json",
      "-limit", "5",
      "-container-network", "jenkins-docker_selenoid-network",
      "-video-output-dir", "/opt/selenoid/video"
    ]
    networks:
      - selenoid-network

  selenoid-ui:
    image: aerokube/selenoid-ui:latest
    container_name: selenoid-ui
    ports:
      - "8888:8080"
    volumes:
      - selenoid_video:/opt/selenoid/video
    environment:
      - SELENOID_URI=http://selenoid:4444
    depends_on:
      - selenoid
    networks:
      - selenoid-network

volumes:
  jenkins_home:
  selenoid_video:

networks:
  selenoid-network:
    driver: bridge
```

---

## Шаг 2. Скачать образы браузеров

До первого запуска скачайте образы браузеров и video-recorder:

```bash
docker pull selenoid/chrome:128.0
docker pull selenoid/firefox:130.0
docker pull selenoid/video-recorder:latest-release
```

> Edge (`browsers/edge:128.0`) скачивается автоматически при первом запросе.

---

## Шаг 3. Запуск стека

```bash
cd jenkins-docker
docker-compose up -d --build
```

Флаг `--build` нужен при первом запуске или после изменения `Dockerfile`. В дальнейшем достаточно `docker-compose up -d`.

После запуска доступны:

| Сервис | URL |
|---|---|
| Jenkins | http://localhost:8080 |
| Selenoid UI | http://localhost:8888 |

---

## Шаг 4. Первоначальная настройка Jenkins

### Получить пароль администратора

```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### Войти и настроить

1. Откройте `http://localhost:8080`
2. Введите полученный пароль
3. Выберите **Install suggested plugins**
4. Создайте пользователя-администратора
5. Оставьте URL по умолчанию (`http://localhost:8080/`) и нажмите **Save and Finish**

### Установить плагин Allure

1. **Manage Jenkins** → **Plugins** → вкладка **Available plugins**
2. Найдите `Allure` → установите
3. **Manage Jenkins** → **Tools** → **Allure Commandline** → **Add**
4. Имя: `allurecommandline`, версия: `2.39.0`, галочка **Install automatically**
5. Сохраните

---

## Шаг 5. Настройка репозитория с тестами

### Структура проекта

```
your-project/
├── conftest.py
├── pytest.ini
├── requirements.txt
├── tests/
│   └── ...
└── utils/
    └── attach.py
```

### conftest.py

```python
import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selene.support.shared import browser
from utils import attach


@pytest.fixture(scope='function')
def setup_browser():
    options = Options()
    selenoid_url = os.getenv("SELENOID_URL")

    if selenoid_url:
        options.capabilities.update({
            "browserName": "chrome",
            "browserVersion": "128.0",
            "selenoid:options": {
                "enableVNC": True,
                "enableVideo": True
            }
        })
        driver = webdriver.Remote(
            command_executor=selenoid_url,
            options=options
        )
        browser.config.driver = driver
    else:
        if os.getenv("CI"):
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
        browser.config.driver_options = options

    yield browser

    attach.add_screenshot(browser)
    attach.add_logs(browser)
    attach.add_html(browser)
    if selenoid_url:
        attach.add_video(browser)
    browser.quit()
```

### utils/attach.py

```python
import os
import allure
from allure_commons.types import AttachmentType


def add_screenshot(browser):
    png = browser.driver.get_screenshot_as_png()
    allure.attach(body=png, name='screenshot', attachment_type=AttachmentType.PNG, extension='.png')


def add_logs(browser):
    log = "".join(f'{text}\n' for text in browser.driver.get_log(log_type='browser'))
    allure.attach(log, 'browser_logs', AttachmentType.TEXT, '.log')


def add_html(browser):
    html = browser.driver.page_source
    allure.attach(html, 'page_source', AttachmentType.HTML, '.html')


def add_video(browser):
    selenoid_url = os.getenv("SELENOID_URL", "")

    if "@" in selenoid_url:
        # Облачный Selenoid: https://user:pass@host/wd/hub -> https://host
        base = selenoid_url.split("@")[1].replace("/wd/hub", "")
        protocol = selenoid_url.split("://")[0]
        video_url = f"{protocol}://{base}/video/{browser.driver.session_id}.mp4"
    else:
        # Локальный Selenoid: http://selenoid:4444/wd/hub -> http://selenoid:4444
        base = selenoid_url.replace("/wd/hub", "")
        video_url = f"{base}/video/{browser.driver.session_id}.mp4"

    html = "<html><body><video width='100%' height='100%' controls autoplay><source src='" \
           + video_url \
           + "' type='video/mp4'></video></body></html>"
    allure.attach(html, 'video_' + browser.driver.session_id, AttachmentType.HTML, '.html')
```

---

## Шаг 6. Создание Pipeline в Jenkins

1. Главная страница → **+ Создать Item**
2. Имя: `my-first-pipeline`, тип: **Pipeline** → OK
3. Прокрутите до секции **Pipeline** → в поле **Script** вставьте:

```groovy
pipeline {
    agent any

    environment {
        SELENOID_URL = 'http://selenoid:4444/wd/hub'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/ВАШ_АККАУНТ/ВАШ_РЕПО.git'
            }
        }

        stage('Setup') {
            steps {
                sh '''
                    python3 -m venv venv
                    ./venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                sh './venv/bin/pytest tests/ --alluredir=allure-results -v'
            }
        }
    }

    post {
        always {
            allure([
                includeProperties: false,
                results: [[path: 'allure-results']]
            ])
        }
    }
}
```

4. Нажмите **Save**
5. Нажмите **Собрать сейчас**

После завершения сборки в левом меню появится кнопка **Allure Report**.

---

## Остановка и перезапуск

```bash
# Остановить все контейнеры
docker-compose down

# Запустить снова (данные Jenkins сохраняются в volume)
docker-compose up -d
```

> Данные Jenkins хранятся в именованном volume `jenkins_home` и не теряются при перезапуске контейнеров.

---

## Известные проблемы

### Windows: видео не записывается локально

Selenoid на Docker Desktop для Windows не может корректно передать видео между контейнерами из-за особенностей WSL2. Решения:

**Вариант 1: использовать внешний Selenoid:**
```groovy
environment {
    SELENOID_URL = 'https://user1:1234@selenoid.autotests.cloud/wd/hub'
}
```

**Вариант 2: развернуть стек на Linux-сервере** (рекомендуется для продакшена).

### Порт 8080 занят

Если Jenkins уже установлен как Windows-служба и занимает порт 8080:

```powershell
# От имени администратора
Stop-Service -Name Jenkins
Set-Service -Name Jenkins -StartupType Disabled
```

### Docker не запущен

При ошибке `failed to connect to the docker API` - запустите Docker Desktop и дождитесь статуса **Engine running**.

---

## Что видно в Allure-отчёте

Для каждого браузерного теста в секции **Tear down** доступны:

- 📸 **screenshot** - скриншот в момент завершения теста
- 📋 **browser_logs** - логи консоли браузера
- 🌐 **page_source** - HTML-код страницы
- 🎥 **video** - запись всего прогона теста (при использовании Selenoid)
