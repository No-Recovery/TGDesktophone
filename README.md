# TGDesktophone

Патч для Telegram-iOS: на iPhone в горизонтальной ориентации включается интерфейс
в духе Telegram Desktop — вертикальная колонка папок слева, список чатов в центре,
открытый чат справа.

Исходников Telegram в репозитории нет. Здесь только изменённые файлы, скрипты и
workflow, который собирает из официального репозитория **неподписанный IPA**.
Подпись делается на телефоне. Релизов пока нет, проект в разработке.

## Изменённые файлы

Все файлы лежат в `changes/`, пути совпадают с upstream.

- `Display/Source/WindowContent.swift` — в ландшафте iPhone отдаёт regular width
  class, из-за чего включается split-режим.
- `Display/Source/Navigation/NavigationSplitContainer.swift` — левая панель шире:
  `max(340, 38% ширины)`, но не больше половины экрана.
- `ChatListUI/Sources/ChatListControllerNode.swift` — колонка папок, скрытие
  горизонтальных табов, место под колонку через `safeInsets`.
- `ChatListUI/Sources/ChatListFolderRailView.swift` — новый файл, сама колонка.

Ширина колонки — `ChatListFolderRailView.railWidth` (64 pt), порог ландшафта —
640 pt в `WindowContent.swift`.

## Сборка

1. В **Settings → Secrets and variables → Actions** добавить секреты `TG_API_ID`
   и `TG_API_HASH` (my.telegram.org → API development tools).
2. **Actions → Build unsigned IPA → Run workflow**.
3. Через 60–90 минут скачать артефакт `telegram-landscape-unsigned`.

Upstream закреплён на коммите `279f89e4` (Telegram 13.1.2). Сборка идёт на
раннере `xcode-27` с Xcode 27.1, минимальная iOS — 15.0, bundle id по умолчанию
`com.dassd.tglandscape`.

## Подпись

IPA неподписанный: импортировать в eSign, подписать сертификатом, установить.
Bundle id при подписи должен совпадать с тем, что собирали.

## Ограничения

- Только iPhone в ландшафте, портрет остаётся штатным.
- Нет ручного включения и настройки ширины.
- С некоторыми сертификатами возможен чёрный экран из-за App Group.
- На маленьких экранах список чатов получается узким.

## Структура

- `.github/workflows/build-ipa.yml` — сборка IPA;
- `changes/` — файлы патча;
- `scripts/` — применение патча, конфиг, отключение подписи, упаковка;
- `tg-desktop-landscape.patch` — тот же патч в виде diff, для справки.

Собрано из [TelegramMessenger/Telegram-iOS](https://github.com/TelegramMessenger/Telegram-iOS).
Не официальный клиент, для личного использования.
