# Tasker

## Предназначение
Проект разработан для изучения различных языков программирования

## Структура сайта
На сайте доступно два вида пользователей - учителя и ученики. Учителя могут создавать курсы, уроки и задачи, ученики же могут эти задачи решать

## Реализация
Бэк:
- [aiohttp](https://github.com/aio-libs/aiohttp) - сервер
- [tortoise](https://github.com/tortoise/tortoise-orm) + [asyncpg](https://github.com/MagicStack/asyncpg) - БД

Фронт:
- Jinja2 (в частности [aiohttp_jinja2](https://github.com/aio-libs/aiohttp-jinja2)) - шаблоны
- jQuery + JS - различные скрипты
- [highlight.js](https://highlightjs.org/) - подсветка синтаксиса
