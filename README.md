# MRT crowd-density logger(English)

Collects LTA DataMall PCDRealTime observations every 30 minutes, at minutes 07 and 37 of each hour (UTC; also 00 and 30 in Singapore). Python 3.12's standard library is sufficient; no packages to install.

## Repository layout

Upload the CONTENTS of this folder to the repository root, including the hidden `.github` directory:

```text
.github/workflows/collect-crowd.yml
scripts/log_crowd_density.py
data/crowd_density_log.csv
.gitignore
README.md
```

## Activate on GitHub

1. Create a GitHub repository, or use your existing project repository. Commit these files to its default branch (usually `main`). Preserve the paths above: the workflow must be at `.github/workflows/collect-crowd.yml`, not inside a nested `mrt-crowd-logger` folder.
2. Obtain an LTA DataMall AccountKey through https://datamall.lta.gov.sg/. Do not put the key in source files, CSV, commits, screenshots, or chat.
3. In the repository, open **Settings → Secrets and variables → Actions → New repository secret**. Name it **LTA_ACCOUNT_KEY** and paste the AccountKey as its value. The workflow provides it only to the collection step as an environment variable.
4. Ensure GitHub Actions is enabled and repository/organization policy permits the workflow's `contents: write` permission. The built-in GITHUB_TOKEN handles commits; no personal access token is needed. Branch protection/rules must permit the bot to push to the default branch. If your project requires PRs, use a dedicated collection repository whose default branch permits bot writes.
5. Open **Actions → Collect MRT crowd density → Run workflow**. Select the default branch. A successful run creates a bot commit when new observations exist. Check the CSV and the run's collection counts. Subsequent runs happen automatically; your laptop can be off.

## Data behavior

Columns are Station, StartTime, EndTime, CrowdLevel, TrainLine, and CollectedAt. CollectedAt includes Singapore's +08:00 offset. API interval timestamps are preserved. CrowdLevel means `l` low, `m` moderate, `h` high, or `NA` unavailable. This is station crowdedness, not passenger counts.

All 11 documented MRT/LRT line codes are queried, including extensions. Edit LINES in the script if you want MRT only. Empty results are accepted and produce no fabricated observations. Transient failures retry with bounded waits and request timeouts; any failed line or malformed response fails the run before appending. The script never prints the key or raw API responses.

Exact repeats are skipped using station, interval, crowd level, and line. A changed crowd level for the same interval is retained as a separate observation; analysis should use CollectedAt to choose the latest version when needed. Only the CSV is staged for the bot commit. Workflow runs are serialized; a concurrent conflicting human edit can still cause a visible failed push/rebase.

This builds history from activation onward. A 30-minute sample misses some 10-minute API intervals; it cannot recover observations from missed runs. Change cron to `0,10,20,30,40,50 * * * *` for a 10-minute target, with more Actions usage and commits. Monitor Actions usage/billing, run failures, CSV growth, and gaps. Scheduled runs can be delayed or dropped, run only from the default branch, and public-repository schedules may be disabled after 60 days without repository activity.

## Sources

- LTA endpoint, line codes, fields, and update frequency: https://datamall.lta.gov.sg/content/dam/datamall/datasets/LTA_DataMall_API_User_Guide.pdf
- GitHub Secrets setup: https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets
- Scheduling behavior: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule

No live API validation is possible until you configure your own AccountKey and run the workflow.





# Регистратор плотности пассажиропотока в метро (Русский)

Собирает данные LTA DataMall PCDRealTime каждые 30 минут, в 7 и 37 минут каждого часа (по всемирному координированному времени; в Сингапуре — также в 00 и 30 минут). Достаточно стандартной библиотеки Python 3.12, никаких дополнительных пакетов устанавливать не нужно.

## Структура репозитория

Загрузите СОДЕРЖИМОЕ этой папки в корень репозитория, включая скрытый каталог `.github`:

```text
.github/workflows/collect-crowd.yml
scripts/log_crowd_density.py
data/crowd_density_log.csv
.gitignore
README.md
```

## Активация на GitHub

1. Создайте репозиторий на GitHub или используйте существующий репозиторий проекта. Добавьте эти файлы в ветку по умолчанию (обычно это ветка main). Сохраните указанные выше пути: рабочий процесс должен находиться в файле `.github/workflows/collect-crowd.yml`, а не во вложенной папке `mrt-crowd-logger`.
2. Получите ключ учетной записи LTA DataMall через https://datamall.lta.gov.sg/. Не указывайте ключ в исходных файлах, CSV, коммитах, скриншотах или чате.
3. В репозитории откройте ** Настройки → Секреты и переменные → Действия → Новый секрет репозитория**. Назовите его **LTA_ACCOUNT_KEY** и вставьте AccountKey в качестве его значения. Рабочий процесс предоставляет его только на этапе сбора данных в качестве переменной среды.
4. Убедитесь, что активирован GitHub Actions, а политика репозитория/организации разрешает рабочему процессу "содержимое: запись". Встроенный GITHUB_TOKEN обрабатывает коммиты; личный токен доступа не требуется. Защита ветки/правила должны позволять боту переходить к ветке по умолчанию. Если вашему проекту требуется PR, используйте специальный репозиторий коллекций, ветка которого по умолчанию разрешает запись ботом.
5. Откройте **Actions → Сбор данных о плотности аудитории MRT → Запуск workflow**. Выберите ветку по умолчанию. При успешном запуске создается фиксация бота при появлении новых наблюдений. Проверьте CSV и количество собранных данных при запуске. Последующие запуски выполняются автоматически; ваш ноутбук может быть выключен.

## Поведение данных

В столбцах указаны станция, время начала, время окончания, уровень скопления людей, линия поезда и дата сбора. Дата сбора включает в себя сингапурское смещение на +08:00. Временные метки интервалов API сохраняются. Уровень переполненности означает "l" низкий, "m" средний, "h" высокий или "NA" недоступен. Это показатель переполненности станции, а не количества пассажиров.

Запрашиваются все 11 задокументированных кодов линий MRT/LRT, включая добавочные номера. Отредактируйте СТРОКИ в скрипте, если вы хотите использовать только MRT. Принимаются пустые результаты, которые не приводят к сфабрикованным наблюдениям. Временные сбои повторяются с ограниченным временем ожидания и тайм-аутами запросов; любая строка с ошибкой или неправильно сформированный ответ завершается сбоем при запуске перед добавлением. Скрипт никогда не выводит ключ или необработанные ответы API.

Точные повторы пропускаются при использовании station, interval, crowd level и line. Измененный уровень посещаемости за тот же интервал сохраняется как отдельное наблюдение; при анализе следует использовать CollectedAt для выбора последней версии, когда это необходимо. Для фиксации ботом используется только CSV-файл. Рабочие процессы выполняются последовательно; одновременное конфликтующее редактирование пользователем все равно может привести к заметному сбою отправки/перебазирования.

При этом создается хронология с момента активации. В выборке за 30 минут отсутствуют некоторые 10-минутные интервалы API; она не может восстановить наблюдения из пропущенных прогонов. Измените cron на `0,10,20,30,40,50 * * * *`, чтобы получить данные с интервалом в 10 минут, при этом увеличьте количество использований и коммитов в Actions. Следите за использованием и оплатой Actions, сбоями при выполнении, ростом размера CSV-файла и пробелами в данных. Запланированные прогоны могут быть отложены или отменены, выполняться только из ветки по умолчанию, а расписания для публичных репозиториев могут быть отключены через 60 дней бездействия в репозитории.

## Источники

- Конечная точка LTA, коды строк, поля и частота обновления: https://datamall.lta.gov.sg/content/dam/datamall/datasets/LTA_DataMall_API_User_Guide.pdf
- Настройка GitHub Secrets: https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets
- Поведение при планировании: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule

До тех пор, пока вы не настроите собственный AccountKey и не запустите рабочий процесс, проверка API в реальном времени будет невозможна.
