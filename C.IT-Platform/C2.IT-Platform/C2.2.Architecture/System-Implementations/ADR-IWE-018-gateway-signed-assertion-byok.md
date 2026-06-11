# ADR-IWE-018 — Gateway-signed assertion для opaque-token доступа к user-profile-service (Ф-byok)

- **Статус:** Accepted (ArchGate пройден 2026-06-11, peer-сессия 2026-06-11-36 Claude+Kimi)
- **Контекст РП:** WP-410 Ф-byok
- **Связанные:** ADR-IWE-017 (чистый шлюз-маршрутизатор), DP.SC.172, принцип «Gateway с одной ответственностью ≠ Gateway с прикладной логикой»

## Контекст

Шлюз (`gateway-mcp`) вызывал `user-profile-service` REST `/byok` (расшифрованный BYOK-ключ, класс `secrets`) и `/tier` через симметричный `USER_PROFILE_SHARED_SECRET` + доверяемый заголовок `X-User-Id`. **P1:** утёк секрет (с любой из двух сторон — он симметричный) → `X-User-Id=victim` → расшифрованный ключ любого пользователя. Секрет лежит на обеих сторонах и не самолечится.

4 call-site неоднородны по доступному контексту: `/tier` legacy-JWT (user-JWT есть), `/tier` opaque OAuth (claude.ai/CLI/VS Code — JWT нет), `/tier` Hydra-hook (пользователя нет, s2s), `/byok` hermes_chat (JWT или opaque). `get_byok_key` намеренно убран из MCP в Ф4б — ключ не должен светиться в публичном fan-out.

## Решение

**Гибрид по типу токена.** Шлюз перестаёт быть держателем симметричного секрета на user-path:

| Путь | Что шлёт шлюз | Чем валидирует сервис |
|------|---------------|------------------------|
| JWT (бот, web-JWT) | `Authorization: Bearer <user-JWT>` как есть | локально jose/JWKS (как `/mcp`) |
| opaque (claude.ai/CLI/VS Code, ict_) | `X-Gateway-Assertion: <RS256 JWS>` (iss=`iwe-gateway`, aud=`user-profile-service`, sub, purpose=`byok\|tier`, exp 60s, kid, jti) | публичным ключом шлюза из `/gateway/.well-known/jwks.json` |
| Hydra-hook /tier (s2s, нет пользователя) | существующий секрет | как сейчас (P2-остаток) |

**Обоснование подписи:** шлюз и так заявляет «это пользователь X» заголовком `X-User-Id` (он auth-граница, обязан резолвить identity для opaque-токена). Подписанное утверждение — криптографически защищённая форма того же заявления, не новая логика-посредник: верификатор держит только публичный ключ, forge-способный материал — только у шлюза (асимметрия снижает blast-radius утечки).

**Переход:** сервис принимает все три credential **presence-based** (форма пришедшего выбирает путь, без последовательного fallback — иначе держатель секрета откатывается на слабый способ), **route-aware** (`/byok` отвергает секрет после cut-over через `BYOK_ALLOW_SECRET=false`; `/tier` держит для hook).

## Отвергнутые альтернативы

- **Дизайн-2-везде** (сервис сам интроспектирует opaque через Ory): новая способность, двойная интроспекция, ❌ устойчивость при падении Ory, N-интроспекций на fan-out.
- **Дизайн-1-везде** (assertion и для JWT): лишний слой поверх валидного JWT, антипаттерн.
- **Вынос BYOK в Hermes-рантайм**: расширяет доверенную границу на внешний рантайм.
- **Сужение hook-секрета**: scope creep ради одного s2s-call-site, не на пути ключа.

## ЭМОГССБ (профиль)

7✅ при 2 управляемых ⚠️-суб-пунктах Безопасности; вето-фильтр чист по 4 критическим (Безопасность/Эволюционируемость/Скорость/Современность). Полный профиль + сравнительная таблица + NBR → `DS-my-strategy/sessions/2026-06/2026-06-11-36-wp410-byok-archgate-design/archgate.md`.

## Последствия

- **+** P1 закрыт (на /byok после cut-over); шлюз без симметричного секрета на user-path; снижение knowledge-coupling.
- **−/риски:** шлюз держит приватный ключ подписи (Worker secret) — ротация через kid+JWKS+overlap-окно. Replay assertion в окне exp 60с — trim: aud+purpose+TLS+короткий exp (для /byok рассмотреть 30с + jti single-use, требует shared-store). Hydra-hook /tier секрет остаётся (P2).
- **Action items:** B2.1 Secrets Inventory (+ gateway signing key; USER_PROFILE_SHARED_SECRET → s2s-only); cut-over под аутентифицированную проверку пилота (нет живого user-токена в агентской сессии).

## Реализация

Ветки `wp-410-fbyok-jwt-assertion`: user-profile-service `4cff420`, gateway-mcp `634e375` (НЕ в main — шлюз авто-деплоится при push в main). Тесты: сервис 16 / шлюз 159 PASS (вкл. round-trip с реальной криптографией). Cold-review: 0 Critical/High.
