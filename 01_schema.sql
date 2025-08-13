create extension if not exists pgcrypto;

create table if not exists profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text,
  locale text default 'en',
  base_currency text default 'USD',
  created_at timestamptz default now()
);

create table if not exists categories (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  name text not null,
  icon text default '💸',
  created_at timestamptz default now()
);

create table if not exists expenses (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  category_id uuid references categories(id) on delete set null,
  amount numeric not null,
  currency text not null,
  note text,
  spent_at timestamptz not null default now(),
  created_at timestamptz default now()
);

alter table profiles enable row level security;
alter table categories enable row level security;
alter table expenses enable row level security;

create policy "profiles are viewable by owner"
on profiles for select using (auth.uid() = id);

create policy "insert own profile"
on profiles for insert with check (auth.uid() = id);

create policy "update own profile"
on profiles for update using (auth.uid() = id);

create policy "categories owner CRUD"
on categories for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "expenses owner CRUD"
on expenses for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
