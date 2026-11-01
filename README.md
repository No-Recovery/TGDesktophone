# TGdesktophone — Telegram с десктопным ландшафтом на iPhone

Мод для Telegram-iOS: в горизонтальной ориентации iPhone включается широкий
(split) layout как в Telegram Desktop — слева вертикальная колонка папок, справа
список чатов и открытый чат.

Репозиторий **не содержит исходников Telegram**. Workflow клонирует официальный
[TelegramMessenger/Telegram-iOS](https://github.com/TelegramMessenger/Telegram-iOS)
на закреплённом коммите, применяет файлы из `changes/` и собирает **unsigned IPA**
на macOS-раннере GitHub. Подписывается `.ipa` уже на iPhone — например, в eSign.

## Что меняется

| Файл | Изменение |
| --- | --- |
| `submodules/Display/Source/WindowContent.swift` | в ландшафте у iPhone включается wide/split layout |
| `submodules/Display/Source/Navigation/NavigationSplitContainer.swift` | ширина левой панели под колонку папок |
| `submodules/ChatListUI/Sources/ChatListControllerNode.swift` | колонка папок, выбор папки, скрытие горизонтальных табов |
| `submodules/ChatListUI/Sources/ChatListFolderRailView.swift` | новый файл: вертикальная колонка папок |

Upstream: `279f89e4d4f63f17227bf877dc3d8990f22ecd58` (Telegram 13.1.2, Xcode 27.1).

## Что нужно

- `TG_API_ID` и `TG_API_HASH` с [my.telegram.org](https://my.telegram.org) →
  **API development tools** (создай приложение, платформа любая);
- eSign (или другой подписывальщик) и сертификат на iPhone;
- ~1 час.

## Запуск

1. **Settings → Secrets and variables → Actions → New repository secret**:
   - `TG_API_ID` — число;
   - `TG_API_HASH` — 32 hex-символа.
2. Вкладка **Actions** → **Build unsigned IPA** → **Run workflow**.
3. `bundle_id` можно оставить `com.dassd.tglandscape`. Меняй только если твой
   сертификат eSign привязан к конкретному App ID.
4. Ждать 60–90 минут. Первый прогон дольше: Bazel прогревается.
5. Скачать внизу run'а артефакт **telegram-landscape-unsigned**, распаковать.

## Подпись в eSign

1. Перекинь `.ipa` на iPhone (Файлы / Saved Messages / AirDrop).
2. eSign → **Import** → выбери IPA → подпиши сертификатом → установи.
3. Bundle ID при подписи оставь тот же, что собирал.
4. **Настройки → Основные → VPN и управление устройством** → доверь профилю.

## Если упало

- **Нет секретов** — добавь `TG_API_ID` и `TG_API_HASH`, перезапусти.
- **Ошибка Swift в патче** — пришли текст из лога, поправим файл в `changes/`.
- **`xcode-27` недоступен** — GitHub может убрать preview-образ; тогда меняем
  `runs-on` и версию Xcode/upstream вместе.
- **Чёрный экран после установки** — известная проблема App Group у
  бесплатных/некоторых сертификатов, нужен отдельный fallback-патч.

## Структура

```
.github/workflows/build-ipa.yml   — весь конвейер сборки
changes/                          — четыре файла патча (источник истины)
tg-desktop-landscape.patch        — тот же патч в виде diff, для справки
scripts/apply_patch.sh            — копирует changes/ в checkout
scripts/make_config.py            — собирает build config из секретов
scripts/enable_unsigned_build.py  — отключает профили и подпись в Bazel
scripts/package_ipa.py            — чистит подписи и упаковывает IPA
```

Сборка для личного использования. Не распространяй клиент под именем Telegram.
