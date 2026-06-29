# Deploy — Render + Supabase (protótipo)

Passo a passo para colocar o OnCourt rodando na nuvem. O banco é o **Supabase**
(Postgres gerenciado) e a app roda no **Render**. Já validado em Postgres local.

## 0. Pré-requisitos no código (já prontos neste repo)
- `requirements.txt` (gunicorn, psycopg, dj-database-url, whitenoise, python-dotenv)
- `settings.py` lê tudo de variáveis de ambiente (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`,
  `DATABASE_URL`, `CSRF_TRUSTED_ORIGINS`); WhiteNoise + `STATIC_ROOT` para estáticos.
- `build.sh` — `pip install` + `collectstatic` + `migrate` + `seed_data`.
- `render.yaml` — blueprint do web service.
- `.python-version` — `3.13.4` (Render).

## 1. Commit & push (git)
`.env` está no `.gitignore` (o segredo local NÃO vai pro repo). Suba o resto:

```bash
git add -A
git commit -m "feat: schema relacional + ORM + deploy Render/Supabase"
git push origin main
```

## 2. Supabase (banco)
1. https://supabase.com → **New project**. Região: **South America (São Paulo)**.
   Defina uma senha forte para o banco (guarde-a).
2. **Project Settings → Database → Connection string → URI**.
3. Use a string do **Session pooler** (porta `5432`) — é compatível com IPv4 (o Render
   precisa). Formato:
   ```
   postgresql://postgres.<ref>:<SENHA>@aws-0-sa-east-1.pooler.supabase.com:5432/postgres
   ```
   Substitua `<SENHA>`. Essa string inteira é o `DATABASE_URL`.

> Obs.: a app força SSL em produção (`ssl_require` quando `DEBUG=False`) — o Supabase exige
> SSL, então isso já está coberto.

## 3. Render (app)
1. https://render.com → **New → Blueprint** → conecte o repo `RodrigoFurukawa/OnCourt`.
   O Render lê o `render.yaml` e cria o web service `oncourt`.
2. Em **Environment**, defina o secret:
   - `DATABASE_URL` = a URI do Supabase do passo 2.
   (As demais já vêm do `render.yaml`: `SECRET_KEY` gerada, `DEBUG=False`,
   `ALLOWED_HOSTS=.onrender.com,...`, `CSRF_TRUSTED_ORIGINS=https://*.onrender.com`.)
3. **Create / Deploy**. O `build.sh` roda `migrate` e `seed_data` automaticamente.
4. Acesse `https://oncourt.onrender.com` (o nome pode variar).

## 4. Verificação
- Abrir a home, `/clubes/`, entrar num clube e numa modalidade (grid de horários por data).
- Criar usuário em `/cadastro/`, fazer uma reserva, conferir em `/minhas-reservas/`.
- Admin: criar superuser pelo **Render Shell** → `python manage.py createsuperuser`,
  depois `/admin/` e `/painel-admin/`.

## 5. Pós-primeiro-deploy (opcional)
- Remover a linha `python manage.py seed_data` do `build.sh` para não resetar dados a
  cada deploy (o seed é idempotente, mas sobrescreve edições de clube/quadra).
- Restringir `ALLOWED_HOSTS` ao domínio exato.

## Próximo destino: produção AWS
Mesma codebase. Trocar `DATABASE_URL` para o **RDS Postgres** e hospedar em **App Runner/
ECS** (ou EC2). Nada de código muda — só variáveis de ambiente.

---

## Dev local com Postgres (Docker)
```bash
docker compose up -d                 # sobe Postgres em localhost:5432
# no .env: DATABASE_URL=postgres://oncourt:oncourt@localhost:5432/oncourt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
docker compose down                  # parar (use -v para apagar os dados)
```