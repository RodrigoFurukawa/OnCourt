# AGENTS.md — OnCourt

Contexto persistente do projeto para agentes de IA (Claude Code, ChatGPT, etc.).
Mantenha este arquivo atualizado quando decisões de arquitetura ou estado do projeto mudarem.

---

## 1. O que é

**OnCourt** — aplicação web de locação/reserva de quadras esportivas (futsal, tênis,
vôlei, beach tennis) para clubes em São Paulo. Usuário busca clubes, vê quadras e
horários, reserva slots; admin gerencia disponibilidade.

- **Framework:** Django 6.0 (server-side rendering, templates Django).
- **App principal:** `booking`.
- **Projeto/config:** `courton`.
- **Idioma da UI:** Português (BR).

## 2. Stack e decisões de arquitetura

| Camada | Hoje | Protótipo (nuvem) | Produção (alvo) |
|---|---|---|---|
| App Django | local (`runserver`) | **Render** (gunicorn) | **AWS** — App Runner/ECS preferível a EC2 |
| Banco | SQLite (só auth/sessions) | **Supabase Postgres** | **AWS RDS Postgres** |
| Estáticos | `runserver` | WhiteNoise | WhiteNoise ou S3+CloudFront |

**Decisões tomadas (2026-06-29):**
1. **Postgres em todos os ambientes** (paridade dev/prod). Dev local via Docker; nuvem
   troca apenas a `DATABASE_URL`. Nada de saltar SQLite → Supabase → RDS com engines
   diferentes.
2. **Host de protótipo = Render + Supabase** (não Vercel). Vercel é serverless/frontend
   e hostiliza Django (cold start, sem worker, estáticos/admin problemáticos). Render
   trata Django como cidadão de primeira classe.
3. **Supabase é usado só como Postgres gerenciado.** Auth/RLS do Supabase NÃO são usados
   — o Django tem auth próprio (`django.contrib.auth`).
4. **Produção AWS:** RDS sempre. EC2 só se for necessário controle total de SO; caso
   contrário App Runner/ECS Fargate (menos ops).
5. **Criar models Django reais + seed** a partir de `mock_data.py` (ver §4).

## 3. Estado atual (importante)

- ✅ **MVP rodando no banco.** Views e templates usam o ORM; `mock_data.py` foi **removido**.
- ✅ **Schema relacional** em [`booking/models.py`](booking/models.py) — ver §3.1.
- ✅ **Disponibilidade por dia da semana** em [`booking/availability.py`](booking/availability.py):
  os horários são GERADOS por data a partir das janelas (`CourtSchedule`) + `Court.slot_minutes`,
  e o status (available/booked/blocked) considera `Reservation` e `SlotBlock` daquela data.
- ✅ **Reservas persistidas** no model `Reservation` (com unicidade court+date+start_time).
- ✅ **Seed** sem fixtures externas: `python manage.py seed_data [--flush]` →
  3 clubes, 6 quadras, 42 janelas de horário.
- ✅ **`settings.py` env-izado** (`SECRET_KEY`/`DEBUG`/`ALLOWED_HOSTS`/`DATABASE_URL` via
  `.env`), WhiteNoise, `STATIC_ROOT`, flags de segurança fora de DEBUG. Models no admin.
- ⚠️ **Banco atual ainda é SQLite** (fallback): Docker baixado mas pendente de reiniciar o PC.
  Trocar é só definir `DATABASE_URL` (Postgres local ou Supabase) e rodar `migrate` + `seed_data`.

### 3.1 Modelo de dados

- **`Club`** — clube. Local estruturado (`address`, `neighborhood`, `city`, `state`,
  `postal_code`, `latitude`/`longitude`), contato (`phone`, `email`, `website`), `rating`,
  `featured`, `slug`. Propriedades: `.location` (resumo legível) e `.sports` (derivado).
- **`Court`** — quadra (FK `club`). Especificidades: `sport`, `size`, `surface`,
  `is_indoor`, `price_per_hour`, `rating`, `tags`, `slot_minutes` (duração do horário).
- **`CourtSchedule`** — janela de funcionamento por `weekday` (`opening_time`/`closing_time`).
  Pode haver várias por dia (manhã/noite). É a base da geração de horários.
- **`Reservation`** — `user`, `court`, `date`, `start_time`, `status`. Único por
  (court, date, start_time). Propriedades de conveniência p/ templates.
- **`CourtBlock`** — bloqueio da quadra inteira (motivo/prazo). `SlotBlock` — bloqueio de um
  horário específico em uma data.

## 4. Roadmap de migração (status)

1. ✅ **`requirements.txt`** — instalado no venv.
2. ✅ **Env-izar `settings.py`**.
3. ⏸️ **Postgres local** — `docker-compose.yml` pronto; falta reiniciar p/ Docker subir,
   OU apontar `DATABASE_URL` direto pro Supabase.
4. ✅ **Schema relacional** — Club, Court, CourtSchedule, Reservation, CourtBlock, SlotBlock.
5. ✅ **Seed** próprio (`seed_data`), sem `mock_data`.
6. ✅ **Views/templates no ORM** + reservas persistidas + dimensão de data nas telas.
7. 🟡 **Deploy Render + Supabase** — arquivos prontos (`render.yaml`, `build.sh`,
   `.python-version`) e paridade Postgres validada localmente. Passo a passo em
   [`DEPLOY.md`](DEPLOY.md). Falta executar (criar Supabase + Render + push).
8. ⬜ **Produção AWS** — RDS + App Runner/ECS; mesma codebase, env vars diferentes.

> Princípio: MVP → reforços. Não "frameworkizar" cedo. Mudanças mínimas por etapa.

## 5. Layout do projeto

```
OnCourt/
├── manage.py
├── manage.py
├── requirements.txt      # deps (instaladas no venv)
├── docker-compose.yml    # Postgres local (paridade dev/prod)
├── .env / .env.example   # config por ambiente (.env é gitignored)
├── courton/              # config do projeto
│   ├── settings.py       # env-izado (SECRET_KEY/DEBUG/DATABASE_URL/WhiteNoise)
│   ├── urls.py
│   └── wsgi.py / asgi.py
├── booking/              # app principal
│   ├── models.py         # Club, Court, CourtSchedule, Reservation, CourtBlock, SlotBlock
│   ├── availability.py   # geração de horários por data + status (lógica central)
│   ├── admin.py          # models registrados
│   ├── views.py          # usa ORM + availability + dimensão de data
│   ├── urls.py           # rotas em PT: /clubes, /quadras/<id>/reservar, etc.
│   ├── forms.py          # ClubFilterForm, SignUpForm
│   ├── management/commands/seed_data.py   # popula o banco (dados inline, sem mock)
│   └── migrations/       # 0001_initial
├── templates/booking/    # base.html + páginas (home, club_detail, reserve_court...)
├── static/css|images/
└── venv/                 # não versionar; usar requirements.txt
```

## 6. Rotas (booking/urls.py)

`home` `/` · `about` `/sobre/` · `faq` `/faq/` · `contact` `/contato/` ·
`signup` `/cadastro/` · `club_list` `/clubes/` · `club_detail` `/clubes/<id>/` ·
`club_sport_courts` `/clubes/<id>/esportes/<sport>/quadras/` ·
`reserve_court` `/quadras/<id>/reservar/` · `my_reservations` `/minhas-reservas/` ·
`admin_dashboard` `/painel-admin/`.

## 7. Como rodar (dev atual)

```bash
cd OnCourt
.\venv\Scripts\Activate.ps1      # PowerShell (Windows)
python manage.py migrate         # auth/sessions
python manage.py runserver
```

## 8. Convenções de trabalho (do dono do projeto)

Derivado de `gpt_guideliine.md`. Em ordem de prioridade:

1. **Não chutar dados faltantes** — se faltar nome de coluna/schema/caminho/constraint,
   pare e pergunte (curto e numerado). Nunca assumir nomes de campos.
2. **Responder direto o que foi perguntado**, sem expandir para etapas futuras sozinho.
3. **Evolução incremental (MVP → reforços).** Simples primeiro; robustez (validação,
   logging, retries, edge cases) só quando pedido.
4. **Mudanças mínimas** em código existente; refactor amplo só com aprovação explícita.
5. **Ao concluir, ofereça opções de próximo passo** (gated) e espere a decisão.

## 9. Pendências / riscos conhecidos

- [x] ~~`requirements.txt` inexistente.~~
- [x] ~~`SECRET_KEY` hardcoded e `DEBUG=True`.~~ → env-izado.
- [x] ~~Domínio só em memória / `mock_data.py`.~~ → schema relacional + ORM.
- [x] ~~Reservas efêmeras.~~ → persistidas em `Reservation`.
- [ ] Postgres real não conectado (Docker baixado, pendente reiniciar; ou usar Supabase).
- [ ] Sem testes automatizados (`booking/tests.py` vazio) — cobrir `availability.py`.
- [ ] Telas assumem `slot_minutes=60`; durações variáveis não foram exercitadas na UI.
- [ ] `forms.SPORT_CHOICES` é uma lista própria; idealmente derivar de `Sport.choices`.
- [ ] `README.md` praticamente vazio.