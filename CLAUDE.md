# CLAUDE.md

> **Fonte de verdade do projeto:** [`AGENTS.md`](AGENTS.md). Leia-o primeiro — contém
> stack, decisões de arquitetura, roadmap de migração, layout, rotas e convenções.
> Este arquivo guarda apenas notas específicas de uso com o Claude Code.

## Resumo de 30 segundos

- **OnCourt** = app Django 6 de reserva de quadras esportivas (PT-BR). App: `booking`.
- Domínio no ORM: `Club` → `Court` → `CourtSchedule` (janelas por dia da semana);
  reservas em `Reservation`. Lógica de horários em `booking/availability.py` (gera slots
  por data). Detalhes do schema em `AGENTS.md` §3.1.
- **Plano:** Postgres em todos os ambientes → protótipo em **Render + Supabase** →
  produção **AWS RDS** (App Runner/ECS preferível a EC2). Detalhes e ordem em `AGENTS.md` §4.
- Banco atual ainda é SQLite (fallback); trocar = definir `DATABASE_URL`.

## Como o dono quer que você trabalhe

(Completo em `AGENTS.md` §8.)
- Não chute dados faltantes — pergunte, curto e numerado.
- Responda direto; não avance para próximos passos sozinho.
- MVP primeiro; mudanças mínimas; refactor amplo só com aprovação.
- Termine oferecendo opções de próximo passo e espere a decisão.

## Comandos úteis

```bash
cd OnCourt
.\venv\Scripts\Activate.ps1
python manage.py runserver
python manage.py makemigrations && python manage.py migrate
```

## Ambiente

- Windows / PowerShell. `venv/` local (preferir `requirements.txt`, ainda inexistente).
- Repositório git fica em `OnCourt/` (não na pasta `projects/` pai).