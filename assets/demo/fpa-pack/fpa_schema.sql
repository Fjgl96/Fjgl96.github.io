-- ============================================================
-- FP&A MONTHLY PACK — esquema estrella sintético (Supabase)
-- Caso 100% inventado. Pegar completo en SQL Editor y ejecutar.
-- Idempotente y correctivo: re-ejecutable sin duplicar
-- (ON CONFLICT DO UPDATE: recargar actualiza, nunca ignora).
-- Tablas fpa_*: conviven con panel-minero / vigilante / registro.
-- Supuesto declarado: LY mensual reparte cada canal con la
-- estacionalidad del ppto (ver DICC del Excel).
-- ============================================================

drop view if exists v_fpa_ventas_canal cascade;
drop view if exists v_fpa_ventas_mes cascade;
drop view if exists v_fpa_ventas_linea cascade;
drop view if exists v_fpa_aging_cliente cascade;
drop view if exists v_fpa_sku cascade;

create table if not exists fpa_ventas (
  mes     int not null check (mes between 1 and 6),
  canal   text not null check (canal in ('Ferretero','Constructor','Retail')),
  linea   text not null check (linea in ('Materiales base','Acabados')),
  version text not null check (version in ('LY','PPTO','REAL')),
  monto   numeric(14,2) not null check (monto >= 0),
  primary key (mes, canal, linea, version)
);

create table if not exists fpa_pyg (
  periodo text not null,
  cuenta  text not null,
  monto   numeric(14,2) not null,
  orden   int not null,
  primary key (periodo, cuenta)
);

create table if not exists fpa_balance (
  corte  text not null check (corte in ('2025-12','2026-06')),
  grupo  text not null check (grupo in ('ACTIVO','PASIVO','PATRIMONIO')),
  cuenta text not null,
  monto  numeric(14,2) not null,
  orden  int not null,
  primary key (corte, cuenta)
);

create table if not exists fpa_cxc_aging (
  cliente text not null,
  tramo   text not null check (tramo in ('Corriente','31-60','61-90','90+')),
  monto   numeric(14,2) not null check (monto >= 0),
  primary key (cliente, tramo)
);

create table if not exists fpa_inv_sku (
  sku       text primary key,
  nombre    text not null,
  stock_u   int not null check (stock_u >= 0),
  costo_u   numeric(12,2) not null check (costo_u >= 0),
  vta_mes_u int not null check (vta_mes_u > 0)
);

create table if not exists fpa_puente (
  tipo  text not null check (tipo in ('PVM','EBITDA')),
  paso  text not null,
  monto numeric(14,2) not null,
  orden int not null,
  primary key (tipo, paso)
);

create table if not exists fpa_parametros (
  clave    text primary key,
  valor    numeric(14,4) not null,
  etiqueta text not null
);

create table if not exists fpa_cxc_canal (
  canal text primary key check (canal in ('Ferretero','Constructor','Retail')),
  monto numeric(14,2) not null check (monto >= 0)
);

create table if not exists fpa_inv_linea (
  linea text primary key check (linea in ('Materiales base','Acabados')),
  monto numeric(14,2) not null check (monto >= 0)
);

create table if not exists fpa_acciones (
  id         text primary key,
  nombre     text not null,
  efecto_caja numeric(14,2) not null,
  efecto_py  text not null,
  kpi        text not null
);

-- RLS: lectura publica (misma convencion que panel-minero) --
alter table fpa_ventas enable row level security;
drop policy if exists "lectura publica fpa_ventas" on fpa_ventas;
create policy "lectura publica fpa_ventas" on fpa_ventas for select to anon using (true);

alter table fpa_pyg enable row level security;
drop policy if exists "lectura publica fpa_pyg" on fpa_pyg;
create policy "lectura publica fpa_pyg" on fpa_pyg for select to anon using (true);

alter table fpa_balance enable row level security;
drop policy if exists "lectura publica fpa_balance" on fpa_balance;
create policy "lectura publica fpa_balance" on fpa_balance for select to anon using (true);

alter table fpa_cxc_aging enable row level security;
drop policy if exists "lectura publica fpa_cxc_aging" on fpa_cxc_aging;
create policy "lectura publica fpa_cxc_aging" on fpa_cxc_aging for select to anon using (true);

alter table fpa_inv_sku enable row level security;
drop policy if exists "lectura publica fpa_inv_sku" on fpa_inv_sku;
create policy "lectura publica fpa_inv_sku" on fpa_inv_sku for select to anon using (true);

alter table fpa_puente enable row level security;
drop policy if exists "lectura publica fpa_puente" on fpa_puente;
create policy "lectura publica fpa_puente" on fpa_puente for select to anon using (true);

alter table fpa_parametros enable row level security;
drop policy if exists "lectura publica fpa_parametros" on fpa_parametros;
create policy "lectura publica fpa_parametros" on fpa_parametros for select to anon using (true);

alter table fpa_cxc_canal enable row level security;
drop policy if exists "lectura publica fpa_cxc_canal" on fpa_cxc_canal;
create policy "lectura publica fpa_cxc_canal" on fpa_cxc_canal for select to anon using (true);

alter table fpa_inv_linea enable row level security;
drop policy if exists "lectura publica fpa_inv_linea" on fpa_inv_linea;
create policy "lectura publica fpa_inv_linea" on fpa_inv_linea for select to anon using (true);

alter table fpa_acciones enable row level security;
drop policy if exists "lectura publica fpa_acciones" on fpa_acciones;
create policy "lectura publica fpa_acciones" on fpa_acciones for select to anon using (true);

-- Vistas de agregados: lo que consume el demo --
create or replace view v_fpa_ventas_canal as
select version, canal, sum(monto) as monto from fpa_ventas group by version, canal;

create or replace view v_fpa_ventas_mes as
select version, mes, sum(monto) as monto from fpa_ventas group by version, mes order by version, mes;

create or replace view v_fpa_ventas_linea as
select version, linea, sum(monto) as monto from fpa_ventas group by version, linea;

-- DSO del canal Constructor, calculado de fpa_ventas (sin hardcode) --
create or replace view v_fpa_aging_cliente as
select cliente,
  sum(monto) as total,
  sum(case when tramo in ('61-90','90+') then monto else 0 end) as mora60,
  round((sum(monto) / ((select sum(monto) from fpa_ventas
    where version = 'REAL' and canal = 'Constructor') / 181.0))::numeric, 1) as dso
from fpa_cxc_aging group by cliente order by total desc;

create or replace view v_fpa_sku as
select sku, nombre, stock_u, costo_u, vta_mes_u,
  round((stock_u * costo_u)::numeric, 0) as valorizado,
  round((stock_u::numeric / vta_mes_u), 1) as cobertura_m
from fpa_inv_sku order by valorizado desc;

-- Recarga limpia: las tablas son solo seed sintético versionado;
-- truncar antes de sembrar evita mezclar casos viejos con nuevos.
truncate fpa_ventas, fpa_pyg, fpa_balance, fpa_cxc_aging, fpa_inv_sku,
  fpa_puente, fpa_parametros, fpa_cxc_canal, fpa_inv_linea, fpa_acciones;

-- Seed correctivo: ON CONFLICT DO UPDATE (recargar actualiza) --
insert into fpa_ventas (mes, canal, linea, version, monto) values
  (1, 'Ferretero', 'Materiales base', 'REAL', 526780),
  (1, 'Ferretero', 'Acabados', 'REAL', 272229),
  (1, 'Constructor', 'Materiales base', 'REAL', 394315),
  (1, 'Constructor', 'Acabados', 'REAL', 203774),
  (1, 'Retail', 'Materiales base', 'REAL', 239259),
  (1, 'Retail', 'Acabados', 'REAL', 123643),
  (2, 'Ferretero', 'Materiales base', 'REAL', 502836),
  (2, 'Ferretero', 'Acabados', 'REAL', 259855),
  (2, 'Constructor', 'Materiales base', 'REAL', 376392),
  (2, 'Constructor', 'Acabados', 'REAL', 194511),
  (2, 'Retail', 'Materiales base', 'REAL', 228383),
  (2, 'Retail', 'Acabados', 'REAL', 118023),
  (3, 'Ferretero', 'Materiales base', 'REAL', 568683),
  (3, 'Ferretero', 'Acabados', 'REAL', 293883),
  (3, 'Constructor', 'Materiales base', 'REAL', 425681),
  (3, 'Constructor', 'Acabados', 'REAL', 219983),
  (3, 'Retail', 'Materiales base', 'REAL', 258291),
  (3, 'Retail', 'Acabados', 'REAL', 133479),
  (4, 'Ferretero', 'Materiales base', 'REAL', 562697),
  (4, 'Ferretero', 'Acabados', 'REAL', 290790),
  (4, 'Constructor', 'Materiales base', 'REAL', 421200),
  (4, 'Constructor', 'Acabados', 'REAL', 217667),
  (4, 'Retail', 'Materiales base', 'REAL', 255572),
  (4, 'Retail', 'Acabados', 'REAL', 132074),
  (5, 'Ferretero', 'Materiales base', 'REAL', 583648),
  (5, 'Ferretero', 'Acabados', 'REAL', 301617),
  (5, 'Constructor', 'Materiales base', 'REAL', 436883),
  (5, 'Constructor', 'Acabados', 'REAL', 225772),
  (5, 'Retail', 'Materiales base', 'REAL', 265088),
  (5, 'Retail', 'Acabados', 'REAL', 136992),
  (6, 'Ferretero', 'Materiales base', 'REAL', 637524),
  (6, 'Ferretero', 'Acabados', 'REAL', 329458),
  (6, 'Constructor', 'Materiales base', 'REAL', 477211),
  (6, 'Constructor', 'Acabados', 'REAL', 246611),
  (6, 'Retail', 'Materiales base', 'REAL', 289558),
  (6, 'Retail', 'Acabados', 'REAL', 149638),
  (1, 'Ferretero', 'Materiales base', 'PPTO', 526500),
  (1, 'Ferretero', 'Acabados', 'PPTO', 283500),
  (1, 'Constructor', 'Materiales base', 'PPTO', 409500),
  (1, 'Constructor', 'Acabados', 'PPTO', 220500),
  (1, 'Retail', 'Materiales base', 'PPTO', 234000),
  (1, 'Retail', 'Acabados', 'PPTO', 126000),
  (2, 'Ferretero', 'Materiales base', 'PPTO', 511875),
  (2, 'Ferretero', 'Acabados', 'PPTO', 275625),
  (2, 'Constructor', 'Materiales base', 'PPTO', 398125),
  (2, 'Constructor', 'Acabados', 'PPTO', 214375),
  (2, 'Retail', 'Materiales base', 'PPTO', 227500),
  (2, 'Retail', 'Acabados', 'PPTO', 122500),
  (3, 'Ferretero', 'Materiales base', 'PPTO', 585000),
  (3, 'Ferretero', 'Acabados', 'PPTO', 315000),
  (3, 'Constructor', 'Materiales base', 'PPTO', 455000),
  (3, 'Constructor', 'Acabados', 'PPTO', 245000),
  (3, 'Retail', 'Materiales base', 'PPTO', 260000),
  (3, 'Retail', 'Acabados', 'PPTO', 140000),
  (4, 'Ferretero', 'Materiales base', 'PPTO', 585000),
  (4, 'Ferretero', 'Acabados', 'PPTO', 315000),
  (4, 'Constructor', 'Materiales base', 'PPTO', 455000),
  (4, 'Constructor', 'Acabados', 'PPTO', 245000),
  (4, 'Retail', 'Materiales base', 'PPTO', 260000),
  (4, 'Retail', 'Acabados', 'PPTO', 140000),
  (5, 'Ferretero', 'Materiales base', 'PPTO', 614250),
  (5, 'Ferretero', 'Acabados', 'PPTO', 330750),
  (5, 'Constructor', 'Materiales base', 'PPTO', 477750),
  (5, 'Constructor', 'Acabados', 'PPTO', 257250),
  (5, 'Retail', 'Materiales base', 'PPTO', 273000),
  (5, 'Retail', 'Acabados', 'PPTO', 147000),
  (6, 'Ferretero', 'Materiales base', 'PPTO', 687375),
  (6, 'Ferretero', 'Acabados', 'PPTO', 370125),
  (6, 'Constructor', 'Materiales base', 'PPTO', 534625),
  (6, 'Constructor', 'Acabados', 'PPTO', 287875),
  (6, 'Retail', 'Materiales base', 'PPTO', 305500),
  (6, 'Retail', 'Acabados', 'PPTO', 164500),
  (1, 'Ferretero', 'Materiales base', 'LY', 497664),
  (1, 'Ferretero', 'Acabados', 'LY', 252336),
  (2, 'Ferretero', 'Materiales base', 'LY', 483840),
  (2, 'Ferretero', 'Acabados', 'LY', 245327),
  (3, 'Ferretero', 'Materiales base', 'LY', 552959),
  (3, 'Ferretero', 'Acabados', 'LY', 280374),
  (4, 'Ferretero', 'Materiales base', 'LY', 552959),
  (4, 'Ferretero', 'Acabados', 'LY', 280374),
  (5, 'Ferretero', 'Materiales base', 'LY', 580607),
  (5, 'Ferretero', 'Acabados', 'LY', 294393),
  (6, 'Ferretero', 'Materiales base', 'LY', 649728),
  (6, 'Ferretero', 'Acabados', 'LY', 329439),
  (1, 'Constructor', 'Materiales base', 'LY', 358318),
  (1, 'Constructor', 'Acabados', 'LY', 181682),
  (2, 'Constructor', 'Materiales base', 'LY', 348364),
  (2, 'Constructor', 'Acabados', 'LY', 176636),
  (3, 'Constructor', 'Materiales base', 'LY', 398131),
  (3, 'Constructor', 'Acabados', 'LY', 201869),
  (4, 'Constructor', 'Materiales base', 'LY', 398131),
  (4, 'Constructor', 'Acabados', 'LY', 201869),
  (5, 'Constructor', 'Materiales base', 'LY', 418037),
  (5, 'Constructor', 'Acabados', 'LY', 211963),
  (6, 'Constructor', 'Materiales base', 'LY', 467804),
  (6, 'Constructor', 'Acabados', 'LY', 237196),
  (1, 'Retail', 'Materiales base', 'LY', 209019),
  (1, 'Retail', 'Acabados', 'LY', 105981),
  (2, 'Retail', 'Materiales base', 'LY', 203213),
  (2, 'Retail', 'Acabados', 'LY', 103037),
  (3, 'Retail', 'Materiales base', 'LY', 232243),
  (3, 'Retail', 'Acabados', 'LY', 117757),
  (4, 'Retail', 'Materiales base', 'LY', 232243),
  (4, 'Retail', 'Acabados', 'LY', 117757),
  (5, 'Retail', 'Materiales base', 'LY', 243855),
  (5, 'Retail', 'Acabados', 'LY', 123645),
  (6, 'Retail', 'Materiales base', 'LY', 272886),
  (6, 'Retail', 'Acabados', 'LY', 138364)
on conflict (mes, canal, linea, version) do update set monto = excluded.monto;

insert into fpa_pyg (periodo, cuenta, monto, orden) values
  ('H1-2025', 'Ventas netas', 10700000, 1),
  ('H1-2025', 'Costo de ventas', 8014300, 2),
  ('H1-2025', 'Utilidad bruta', 2685700, 3),
  ('H1-2025', 'Gastos operativos', 1450000, 4),
  ('H1-2025', 'EBITDA', 1235700, 5),
  ('H1-2025', 'Depreciación', 430000, 6),
  ('H1-2025', 'EBIT', 1065700, 7),
  ('H1-2025', 'Gastos financieros', 210000, 8),
  ('H1-2025', 'Diferencia de cambio', -50000, 9),
  ('H1-2025', 'EBT', 805700, 10),
  ('H1-2025', 'Impuesto a la renta 29.5%', 237682, 11),
  ('H1-2025', 'Utilidad neta', 568018, 12),
  ('H1-2026-PPTO', 'Ventas netas', 12000000, 1),
  ('H1-2026-PPTO', 'Costo de ventas', 8880000, 2),
  ('H1-2026-PPTO', 'Utilidad bruta', 3120000, 3),
  ('H1-2026-PPTO', 'Gastos operativos', 1680000, 4),
  ('H1-2026-PPTO', 'EBITDA', 1440000, 5),
  ('H1-2026-PPTO', 'Depreciación', 450000, 6),
  ('H1-2026-PPTO', 'EBIT', 1260000, 7),
  ('H1-2026-PPTO', 'Gastos financieros', 220000, 8),
  ('H1-2026-PPTO', 'Diferencia de cambio', -40000, 9),
  ('H1-2026-PPTO', 'EBT', 1000000, 10),
  ('H1-2026-PPTO', 'Impuesto a la renta 29.5%', 295000, 11),
  ('H1-2026-PPTO', 'Utilidad neta', 705000, 12),
  ('H1-2026-REAL', 'Ventas netas', 11300000, 1),
  ('H1-2026-REAL', 'Costo de ventas', 8565400, 2),
  ('H1-2026-REAL', 'Utilidad bruta', 2734600, 3),
  ('H1-2026-REAL', 'Gastos operativos', 1684600, 4),
  ('H1-2026-REAL', 'EBITDA', 1050000, 5),
  ('H1-2026-REAL', 'Depreciación', 450000, 6),
  ('H1-2026-REAL', 'EBIT', 870000, 7),
  ('H1-2026-REAL', 'Gastos financieros', 275000, 8),
  ('H1-2026-REAL', 'Diferencia de cambio', -110000, 9),
  ('H1-2026-REAL', 'EBT', 485000, 10),
  ('H1-2026-REAL', 'Impuesto a la renta 29.5%', 143075, 11),
  ('H1-2026-REAL', 'Utilidad neta', 341925, 12),
  ('FY-2026-PPTO', 'Ventas netas', 24000000, 1),
  ('FY-2026-PPTO', 'EBITDA', 2880000, 5),
  ('FY-2026-PPTO', 'Utilidad neta', 1410000, 12),
  ('FY-2026-BASE', 'Ventas netas', 23100000, 1),
  ('FY-2026-BASE', 'EBITDA', 2250000, 5),
  ('FY-2026-BASE', 'Utilidad neta', 720000, 12)
on conflict (periodo, cuenta) do update set monto = excluded.monto, orden = excluded.orden;

insert into fpa_balance (corte, grupo, cuenta, monto, orden) values
  ('2025-12', 'ACTIVO', 'Caja', 480000, 1),
  ('2025-12', 'ACTIVO', 'Cuentas por cobrar', 2720000, 2),
  ('2025-12', 'ACTIVO', 'Inventarios', 2660000, 3),
  ('2025-12', 'ACTIVO', 'Otros AC', 160000, 4),
  ('2025-12', 'ACTIVO', 'Activo fijo neto', 3380000, 5),
  ('2025-12', 'PASIVO', 'Cuentas por pagar', 1800000, 6),
  ('2025-12', 'PASIVO', 'Deuda CP', 1520000, 7),
  ('2025-12', 'PASIVO', 'Otros pasivos CP', 400000, 8),
  ('2025-12', 'PASIVO', 'Deuda LP', 1990000, 9),
  ('2025-12', 'PATRIMONIO', 'Patrimonio', 3690000, 10),
  ('2026-06', 'ACTIVO', 'Caja', 380000, 1),
  ('2026-06', 'ACTIVO', 'Cuentas por cobrar', 3246400, 2),
  ('2026-06', 'ACTIVO', 'Inventarios', 2886895, 3),
  ('2026-06', 'ACTIVO', 'Otros AC', 160000, 4),
  ('2026-06', 'ACTIVO', 'Activo fijo neto', 3370000, 5),
  ('2026-06', 'PASIVO', 'Cuentas por pagar', 1651700, 6),
  ('2026-06', 'PASIVO', 'Deuda CP', 2359670, 7),
  ('2026-06', 'PASIVO', 'Otros pasivos CP', 440000, 8),
  ('2026-06', 'PASIVO', 'Deuda LP', 1560000, 9),
  ('2026-06', 'PATRIMONIO', 'Patrimonio', 4031925, 10)
on conflict (corte, cuenta) do update set monto = excluded.monto, orden = excluded.orden;

insert into fpa_cxc_aging (cliente, tramo, monto) values
  ('Municipalidad de San Juan', 'Corriente', 120000),
  ('Municipalidad de San Juan', '31-60', 60000),
  ('Municipalidad de San Juan', '61-90', 28000),
  ('Municipalidad de San Juan', '90+', 0),
  ('Red Salud Norte', 'Corriente', 80000),
  ('Red Salud Norte', '31-60', 48000),
  ('Red Salud Norte', '61-90', 24000),
  ('Red Salud Norte', '90+', 12000),
  ('EduCorp S.A.', 'Corriente', 100000),
  ('EduCorp S.A.', '31-60', 32000),
  ('EduCorp S.A.', '61-90', 8000),
  ('EduCorp S.A.', '90+', 0),
  ('Minera Cascajal', 'Corriente', 112000),
  ('Minera Cascajal', '31-60', 0),
  ('Minera Cascajal', '61-90', 0),
  ('Minera Cascajal', '90+', 0),
  ('Agroindustrial del Valle', 'Corriente', 40000),
  ('Agroindustrial del Valle', '31-60', 20000),
  ('Agroindustrial del Valle', '61-90', 12000),
  ('Agroindustrial del Valle', '90+', 0),
  ('Constructora VialSur', 'Corriente', 16000),
  ('Constructora VialSur', '31-60', 12000),
  ('Constructora VialSur', '61-90', 8000),
  ('Constructora VialSur', '90+', 12000),
  ('Gobierno Regional', 'Corriente', 0),
  ('Gobierno Regional', '31-60', 8000),
  ('Gobierno Regional', '61-90', 12000),
  ('Gobierno Regional', '90+', 16000),
  ('Otros menores', 'Corriente', 12000),
  ('Otros menores', '31-60', 8000),
  ('Otros menores', '61-90', 0),
  ('Otros menores', '90+', 0)
on conflict (cliente, tramo) do update set monto = excluded.monto;

insert into fpa_inv_sku (sku, nombre, stock_u, costo_u, vta_mes_u) values
  ('CER-101', 'Porcelanato 60x60 caja', 2100, 68.0, 475),
  ('PIN-020', 'Pintura latex 20L', 1900, 92.5, 390),
  ('PEG-025', 'Pegamento ceramico 25kg', 4500, 24.8, 1100),
  ('LAC-011', 'Laca selladora 1L', 3250, 18.9, 850),
  ('PER-008', 'Perfiles aluminio 6m', 1200, 45.0, 140),
  ('SAN-031', 'Griferia cocina', 950, 62.0, 115),
  ('ILU-044', 'Focos LED 12W caja x24', 2500, 38.4, 360),
  ('ACA-VAR', 'Varios Acabados (agregado)', 68642, 10.0, 32687)
on conflict (sku) do update set nombre = excluded.nombre, stock_u = excluded.stock_u, costo_u = excluded.costo_u, vta_mes_u = excluded.vta_mes_u;

insert into fpa_puente (tipo, paso, monto, orden) values
  ('PVM', 'Ventas ppto', 12000000, 0),
  ('PVM', 'Efecto volumen', -450000, 1),
  ('PVM', 'Efecto precio (+2% lista parcial)', 110000, 2),
  ('PVM', 'Efecto mix canal/linea', -180000, 3),
  ('PVM', 'Descuento comercial defensivo', -180000, 4),
  ('PVM', 'Ventas real H1', 11300000, 5),
  ('EBITDA', 'EBITDA ppto', 1440000, 0),
  ('EBITDA', 'Efecto volumen (margen std 26%)', -117000, 1),
  ('EBITDA', 'Efecto precio / mix / descuento', -65000, 2),
  ('EBITDA', 'Costo FX (TC 3.72->3.81)', -120000, 3),
  ('EBITDA', 'Otros costos', -83400, 4),
  ('EBITDA', 'Opex neto', -4600, 5),
  ('EBITDA', 'EBITDA real H1', 1050000, 6)
on conflict (tipo, paso) do update set monto = excluded.monto, orden = excluded.orden;

insert into fpa_parametros (clave, valor, etiqueta) values
  ('tc_ppto', 3.72, 'Tipo de cambio presupuesto 2026'),
  ('tc_real_h1', 3.81, 'TC promedio real H1'),
  ('tc_jun', 3.84, 'TC cierre junio'),
  ('tasa_ir', 0.295, 'Impuesto a la renta'),
  ('dias_h1', 181, 'Dias del semestre'),
  ('pct_compras_usd', 0.4, 'Compras en USD'),
  ('exposicion_usd', 180000, 'Exposicion neta pasiva USD'),
  ('pico_deuda_oct', 4500000, 'Pico de deuda octubre (base)'),
  ('linea_adicional', 1000000, 'Linea revolvente propuesta')
on conflict (clave) do update set valor = excluded.valor, etiqueta = excluded.etiqueta;

insert into fpa_cxc_canal (canal, monto) values
  ('Ferretero', 1566400),
  ('Constructor', 800000),
  ('Retail', 880000)
on conflict (canal) do update set monto = excluded.monto;

insert into fpa_inv_linea (linea, monto) values
  ('Materiales base', 1500000),
  ('Acabados', 1386895)
on conflict (linea) do update set monto = excluded.monto;

insert into fpa_acciones (id, nombre, efecto_caja, efecto_py, kpi) values
  ('A1', 'Cobranza constructor + pronto pago', 375000, '- S/ 25k descuento financiero', 'DSO 52 -> 46 dias'),
  ('A2', 'Ajuste lista de precios 2H (+2%)', 220000, '+ S/ 220k margen', 'Margen bruto +80 pbs en 2H'),
  ('A3', 'Recorte compra acabados -15%', 280000, 'neutro', 'DIO 61 -> 55 dias'),
  ('A4', 'Forward 50% exposicion 90 dias', 0, 'acota riesgo 18k -> 9k por 10 cts', 'Exposicion neta USD 180k -> 90k'),
  ('A5', 'Linea revolvente +S/ 1.0M', 1000000, '- S/ 35k intereses 2H', 'Cubre pico de octubre')
on conflict (id) do update set nombre = excluded.nombre, efecto_caja = excluded.efecto_caja, efecto_py = excluded.efecto_py, kpi = excluded.kpi;

-- Verificacion post-carga (deben devolver una fila 'OK' cada una) --
-- select case when sum(monto)=11300000 then 'OK ventas REAL' else 'FALLA' end from fpa_ventas where version='REAL';
-- select case when sum(monto)=800000 then 'OK aging' else 'FALLA' end from fpa_cxc_aging;
-- select case when sum(stock_u*costo_u)=1386900 then 'OK skus' else 'FALLA' end from fpa_inv_sku;