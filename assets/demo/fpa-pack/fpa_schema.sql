-- ============================================================
-- FP&A MONTHLY PACK — esquema estrella sintético (Supabase)
-- Caso 100% inventado. Pegar completo en SQL Editor y ejecutar.
-- Idempotente: re-ejecutable sin duplicar (ON CONFLICT DO NOTHING).
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
  canal   text not null check (canal in ('Mayorista','Minorista','Institucional')),
  linea   text not null check (linea in ('Abarrotes importados','Cuidado del hogar')),
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
  canal text primary key check (canal in ('Mayorista','Minorista','Institucional')),
  monto numeric(14,2) not null check (monto >= 0)
);

create table if not exists fpa_inv_linea (
  linea text primary key check (linea in ('Abarrotes importados','Cuidado del hogar')),
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

-- DSO del canal institucional: ventas diarias = 5144000 / 181 --
create or replace view v_fpa_aging_cliente as
select cliente,
  sum(monto) as total,
  sum(case when tramo in ('61-90','90+') then monto else 0 end) as mora60,
  round((sum(monto) / (5144000.0 / 181))::numeric, 1) as dso
from fpa_cxc_aging group by cliente order by total desc;

create or replace view v_fpa_sku as
select sku, nombre, stock_u, costo_u, vta_mes_u,
  round((stock_u * costo_u)::numeric, 0) as valorizado,
  round((stock_u::numeric / vta_mes_u), 1) as cobertura_m
from fpa_inv_sku order by valorizado desc;

-- Seed (idempotente) --
insert into fpa_ventas (mes, canal, linea, version, monto) values
  (1, 'Mayorista', 'Abarrotes importados', 'REAL', 1409617),
  (1, 'Mayorista', 'Cuidado del hogar', 'REAL', 723435),
  (1, 'Minorista', 'Abarrotes importados', 'REAL', 1052608),
  (1, 'Minorista', 'Cuidado del hogar', 'REAL', 540213),
  (1, 'Institucional', 'Abarrotes importados', 'REAL', 544620),
  (1, 'Institucional', 'Cuidado del hogar', 'REAL', 279507),
  (2, 'Mayorista', 'Abarrotes importados', 'REAL', 1301185),
  (2, 'Mayorista', 'Cuidado del hogar', 'REAL', 667787),
  (2, 'Minorista', 'Abarrotes importados', 'REAL', 971638),
  (2, 'Minorista', 'Cuidado del hogar', 'REAL', 498658),
  (2, 'Institucional', 'Abarrotes importados', 'REAL', 502726),
  (2, 'Institucional', 'Cuidado del hogar', 'REAL', 258006),
  (3, 'Mayorista', 'Abarrotes importados', 'REAL', 1471579),
  (3, 'Mayorista', 'Cuidado del hogar', 'REAL', 755235),
  (3, 'Minorista', 'Abarrotes importados', 'REAL', 1098876),
  (3, 'Minorista', 'Cuidado del hogar', 'REAL', 563959),
  (3, 'Institucional', 'Abarrotes importados', 'REAL', 568559),
  (3, 'Institucional', 'Cuidado del hogar', 'REAL', 291792),
  (4, 'Mayorista', 'Abarrotes importados', 'REAL', 1456088),
  (4, 'Mayorista', 'Cuidado del hogar', 'REAL', 747285),
  (4, 'Minorista', 'Abarrotes importados', 'REAL', 1087309),
  (4, 'Minorista', 'Cuidado del hogar', 'REAL', 558022),
  (4, 'Institucional', 'Abarrotes importados', 'REAL', 562575),
  (4, 'Institucional', 'Cuidado del hogar', 'REAL', 288721),
  (5, 'Mayorista', 'Abarrotes importados', 'REAL', 1502559),
  (5, 'Mayorista', 'Cuidado del hogar', 'REAL', 771134),
  (5, 'Minorista', 'Abarrotes importados', 'REAL', 1122010),
  (5, 'Minorista', 'Cuidado del hogar', 'REAL', 575831),
  (5, 'Institucional', 'Abarrotes importados', 'REAL', 580529),
  (5, 'Institucional', 'Cuidado del hogar', 'REAL', 297937),
  (6, 'Mayorista', 'Abarrotes importados', 'REAL', 1657462),
  (6, 'Mayorista', 'Cuidado del hogar', 'REAL', 850634),
  (6, 'Minorista', 'Abarrotes importados', 'REAL', 1237681),
  (6, 'Minorista', 'Cuidado del hogar', 'REAL', 635195),
  (6, 'Institucional', 'Abarrotes importados', 'REAL', 640377),
  (6, 'Institucional', 'Cuidado del hogar', 'REAL', 328651),
  (1, 'Mayorista', 'Abarrotes importados', 'PPTO', 1345500),
  (1, 'Mayorista', 'Cuidado del hogar', 'PPTO', 724500),
  (1, 'Minorista', 'Abarrotes importados', 'PPTO', 1046500),
  (1, 'Minorista', 'Cuidado del hogar', 'PPTO', 563500),
  (1, 'Institucional', 'Abarrotes importados', 'PPTO', 598000),
  (1, 'Institucional', 'Cuidado del hogar', 'PPTO', 322000),
  (2, 'Mayorista', 'Abarrotes importados', 'PPTO', 1287000),
  (2, 'Mayorista', 'Cuidado del hogar', 'PPTO', 693000),
  (2, 'Minorista', 'Abarrotes importados', 'PPTO', 1001000),
  (2, 'Minorista', 'Cuidado del hogar', 'PPTO', 539000),
  (2, 'Institucional', 'Abarrotes importados', 'PPTO', 572000),
  (2, 'Institucional', 'Cuidado del hogar', 'PPTO', 308000),
  (3, 'Mayorista', 'Abarrotes importados', 'PPTO', 1462500),
  (3, 'Mayorista', 'Cuidado del hogar', 'PPTO', 787500),
  (3, 'Minorista', 'Abarrotes importados', 'PPTO', 1137500),
  (3, 'Minorista', 'Cuidado del hogar', 'PPTO', 612500),
  (3, 'Institucional', 'Abarrotes importados', 'PPTO', 650000),
  (3, 'Institucional', 'Cuidado del hogar', 'PPTO', 350000),
  (4, 'Mayorista', 'Abarrotes importados', 'PPTO', 1462500),
  (4, 'Mayorista', 'Cuidado del hogar', 'PPTO', 787500),
  (4, 'Minorista', 'Abarrotes importados', 'PPTO', 1137500),
  (4, 'Minorista', 'Cuidado del hogar', 'PPTO', 612500),
  (4, 'Institucional', 'Abarrotes importados', 'PPTO', 650000),
  (4, 'Institucional', 'Cuidado del hogar', 'PPTO', 350000),
  (5, 'Mayorista', 'Abarrotes importados', 'PPTO', 1521000),
  (5, 'Mayorista', 'Cuidado del hogar', 'PPTO', 819000),
  (5, 'Minorista', 'Abarrotes importados', 'PPTO', 1183000),
  (5, 'Minorista', 'Cuidado del hogar', 'PPTO', 637000),
  (5, 'Institucional', 'Abarrotes importados', 'PPTO', 676000),
  (5, 'Institucional', 'Cuidado del hogar', 'PPTO', 364000),
  (6, 'Mayorista', 'Abarrotes importados', 'PPTO', 1725750),
  (6, 'Mayorista', 'Cuidado del hogar', 'PPTO', 929250),
  (6, 'Minorista', 'Abarrotes importados', 'PPTO', 1342250),
  (6, 'Minorista', 'Cuidado del hogar', 'PPTO', 722750),
  (6, 'Institucional', 'Abarrotes importados', 'PPTO', 767000),
  (6, 'Institucional', 'Cuidado del hogar', 'PPTO', 413000),
  (1, 'Mayorista', 'Abarrotes importados', 'LY', 1259860),
  (1, 'Mayorista', 'Cuidado del hogar', 'LY', 665721),
  (2, 'Mayorista', 'Abarrotes importados', 'LY', 1205083),
  (2, 'Mayorista', 'Cuidado del hogar', 'LY', 636777),
  (3, 'Mayorista', 'Abarrotes importados', 'LY', 1369413),
  (3, 'Mayorista', 'Cuidado del hogar', 'LY', 723610),
  (4, 'Mayorista', 'Abarrotes importados', 'LY', 1369413),
  (4, 'Mayorista', 'Cuidado del hogar', 'LY', 723610),
  (5, 'Mayorista', 'Abarrotes importados', 'LY', 1424189),
  (5, 'Mayorista', 'Cuidado del hogar', 'LY', 752555),
  (6, 'Mayorista', 'Abarrotes importados', 'LY', 1615908),
  (6, 'Mayorista', 'Cuidado del hogar', 'LY', 853861),
  (1, 'Minorista', 'Abarrotes importados', 'LY', 939896),
  (1, 'Minorista', 'Cuidado del hogar', 'LY', 496649),
  (2, 'Minorista', 'Abarrotes importados', 'LY', 899030),
  (2, 'Minorista', 'Cuidado del hogar', 'LY', 475056),
  (3, 'Minorista', 'Abarrotes importados', 'LY', 1021626),
  (3, 'Minorista', 'Cuidado del hogar', 'LY', 539836),
  (4, 'Minorista', 'Abarrotes importados', 'LY', 1021626),
  (4, 'Minorista', 'Cuidado del hogar', 'LY', 539836),
  (5, 'Minorista', 'Abarrotes importados', 'LY', 1062490),
  (5, 'Minorista', 'Cuidado del hogar', 'LY', 561430),
  (6, 'Minorista', 'Abarrotes importados', 'LY', 1205518),
  (6, 'Minorista', 'Cuidado del hogar', 'LY', 637007),
  (1, 'Institucional', 'Abarrotes importados', 'LY', 489945),
  (1, 'Institucional', 'Cuidado del hogar', 'LY', 258892),
  (2, 'Institucional', 'Abarrotes importados', 'LY', 468644),
  (2, 'Institucional', 'Cuidado del hogar', 'LY', 247635),
  (3, 'Institucional', 'Abarrotes importados', 'LY', 532549),
  (3, 'Institucional', 'Cuidado del hogar', 'LY', 281404),
  (4, 'Institucional', 'Abarrotes importados', 'LY', 532549),
  (4, 'Institucional', 'Cuidado del hogar', 'LY', 281404),
  (5, 'Institucional', 'Abarrotes importados', 'LY', 553852),
  (5, 'Institucional', 'Cuidado del hogar', 'LY', 292660),
  (6, 'Institucional', 'Abarrotes importados', 'LY', 628409),
  (6, 'Institucional', 'Cuidado del hogar', 'LY', 332057)
on conflict do nothing;

insert into fpa_pyg (periodo, cuenta, monto, orden) values
  ('H1-2025', 'Ventas netas', 26900000, 1),
  ('H1-2025', 'Costo de ventas', 20659200, 2),
  ('H1-2025', 'Utilidad bruta', 6240800, 3),
  ('H1-2025', 'Gastos operativos', 3480000, 4),
  ('H1-2025', 'EBITDA', 2760800, 5),
  ('H1-2025', 'Depreciación', 430000, 6),
  ('H1-2025', 'EBIT', 2330800, 7),
  ('H1-2025', 'Gastos financieros', 520000, 8),
  ('H1-2025', 'Diferencia de cambio', -120000, 9),
  ('H1-2025', 'EBT', 1690800, 10),
  ('H1-2025', 'Impuesto a la renta 29.5%', 498786, 11),
  ('H1-2025', 'Utilidad neta', 1192014, 12),
  ('H1-2026-PPTO', 'Ventas netas', 30100000, 1),
  ('H1-2026-PPTO', 'Costo de ventas', 22876000, 2),
  ('H1-2026-PPTO', 'Utilidad bruta', 7224000, 3),
  ('H1-2026-PPTO', 'Gastos operativos', 3924000, 4),
  ('H1-2026-PPTO', 'EBITDA', 3300000, 5),
  ('H1-2026-PPTO', 'Depreciación', 450000, 6),
  ('H1-2026-PPTO', 'EBIT', 2850000, 7),
  ('H1-2026-PPTO', 'Gastos financieros', 550000, 8),
  ('H1-2026-PPTO', 'Diferencia de cambio', -100000, 9),
  ('H1-2026-PPTO', 'EBT', 2200000, 10),
  ('H1-2026-PPTO', 'Impuesto a la renta 29.5%', 649000, 11),
  ('H1-2026-PPTO', 'Utilidad neta', 1551000, 12),
  ('H1-2026-REAL', 'Ventas netas', 28400000, 1),
  ('H1-2026-REAL', 'Costo de ventas', 22123600, 2),
  ('H1-2026-REAL', 'Utilidad bruta', 6276400, 3),
  ('H1-2026-REAL', 'Gastos operativos', 3926400, 4),
  ('H1-2026-REAL', 'EBITDA', 2350000, 5),
  ('H1-2026-REAL', 'Depreciación', 450000, 6),
  ('H1-2026-REAL', 'EBIT', 1900000, 7),
  ('H1-2026-REAL', 'Gastos financieros', 680000, 8),
  ('H1-2026-REAL', 'Diferencia de cambio', -280000, 9),
  ('H1-2026-REAL', 'EBT', 940000, 10),
  ('H1-2026-REAL', 'Impuesto a la renta 29.5%', 277300, 11),
  ('H1-2026-REAL', 'Utilidad neta', 662700, 12),
  ('FY-2026-PPTO', 'Ventas netas', 60200000, 1),
  ('FY-2026-PPTO', 'EBITDA', 6700000, 5),
  ('FY-2026-PPTO', 'Utilidad neta', 3100000, 12),
  ('FY-2026-BASE', 'Ventas netas', 58500000, 1),
  ('FY-2026-BASE', 'EBITDA', 5400000, 5),
  ('FY-2026-BASE', 'Utilidad neta', 1700000, 12)
on conflict do nothing;

insert into fpa_balance (corte, grupo, cuenta, monto, orden) values
  ('2025-12', 'ACTIVO', 'Caja', 1200000, 1),
  ('2025-12', 'ACTIVO', 'Cuentas por cobrar', 6800000, 2),
  ('2025-12', 'ACTIVO', 'Inventarios', 6650000, 3),
  ('2025-12', 'ACTIVO', 'Otros AC', 400000, 4),
  ('2025-12', 'ACTIVO', 'Activo fijo neto', 8450000, 5),
  ('2025-12', 'PASIVO', 'Cuentas por pagar', 4500000, 6),
  ('2025-12', 'PASIVO', 'Deuda CP', 3800000, 7),
  ('2025-12', 'PASIVO', 'Otros pasivos CP', 1000000, 8),
  ('2025-12', 'PASIVO', 'Deuda LP', 4970000, 9),
  ('2025-12', 'PATRIMONIO', 'Patrimonio', 9230000, 10),
  ('2026-06', 'ACTIVO', 'Caja', 950000, 1),
  ('2026-06', 'ACTIVO', 'Cuentas por cobrar', 8160000, 2),
  ('2026-06', 'ACTIVO', 'Inventarios', 7450000, 3),
  ('2026-06', 'ACTIVO', 'Otros AC', 400000, 4),
  ('2026-06', 'ACTIVO', 'Activo fijo neto', 8350000, 5),
  ('2026-06', 'PASIVO', 'Cuentas por pagar', 4320000, 6),
  ('2026-06', 'PASIVO', 'Deuda CP', 6097300, 7),
  ('2026-06', 'PASIVO', 'Otros pasivos CP', 1100000, 8),
  ('2026-06', 'PASIVO', 'Deuda LP', 3900000, 9),
  ('2026-06', 'PATRIMONIO', 'Patrimonio', 9892700, 10)
on conflict do nothing;

insert into fpa_cxc_aging (cliente, tramo, monto) values
  ('Municipalidad de San Juan', 'Corriente', 300000),
  ('Municipalidad de San Juan', '31-60', 150000),
  ('Municipalidad de San Juan', '61-90', 70000),
  ('Municipalidad de San Juan', '90+', 0),
  ('Red Salud Norte', 'Corriente', 200000),
  ('Red Salud Norte', '31-60', 120000),
  ('Red Salud Norte', '61-90', 60000),
  ('Red Salud Norte', '90+', 30000),
  ('EduCorp S.A.', 'Corriente', 250000),
  ('EduCorp S.A.', '31-60', 80000),
  ('EduCorp S.A.', '61-90', 20000),
  ('EduCorp S.A.', '90+', 0),
  ('Minera Cascajal', 'Corriente', 280000),
  ('Minera Cascajal', '31-60', 0),
  ('Minera Cascajal', '61-90', 0),
  ('Minera Cascajal', '90+', 0),
  ('Agroindustrial del Valle', 'Corriente', 100000),
  ('Agroindustrial del Valle', '31-60', 50000),
  ('Agroindustrial del Valle', '61-90', 30000),
  ('Agroindustrial del Valle', '90+', 0),
  ('Constructora VialSur', 'Corriente', 40000),
  ('Constructora VialSur', '31-60', 30000),
  ('Constructora VialSur', '61-90', 20000),
  ('Constructora VialSur', '90+', 30000),
  ('Gobierno Regional', 'Corriente', 0),
  ('Gobierno Regional', '31-60', 20000),
  ('Gobierno Regional', '61-90', 30000),
  ('Gobierno Regional', '90+', 40000),
  ('Otros menores', 'Corriente', 30000),
  ('Otros menores', '31-60', 20000),
  ('Otros menores', '61-90', 0),
  ('Otros menores', '90+', 0)
on conflict do nothing;

insert into fpa_inv_sku (sku, nombre, stock_u, costo_u, vta_mes_u) values
  ('HOG-014', 'Detergente industrial 20kg', 14000, 18.5, 3200),
  ('HOG-022', 'Jabon liquido 5L', 22000, 12.8, 4800),
  ('HOG-031', 'Papel toalla x12', 30000, 9.4, 7500),
  ('HOG-007', 'Desinfectante 1L', 45000, 4.2, 12000),
  ('HOG-045', 'Escobas premium', 18000, 6.9, 2100),
  ('HOG-046', 'Trapeadores', 25000, 5.6, 3000),
  ('HOG-052', 'Bolsas basura 100L x50', 60000, 7.3, 9000),
  ('HOG-VAR', 'Varios Hogar (agregado)', 163620, 10.0, 77914)
on conflict do nothing;

insert into fpa_puente (tipo, paso, monto, orden) values
  ('PVM', 'Ventas ppto', 30100000, 0),
  ('PVM', 'Efecto volumen', -1100000, 1),
  ('PVM', 'Efecto precio (+2% lista parcial)', 250000, 2),
  ('PVM', 'Efecto mix canal/linea', -450000, 3),
  ('PVM', 'Descuento comercial defensivo', -400000, 4),
  ('PVM', 'Ventas real H1', 28400000, 5),
  ('EBITDA', 'EBITDA ppto', 3300000, 0),
  ('EBITDA', 'Efecto volumen', -410000, 1),
  ('EBITDA', 'Efecto precio / mix', -120000, 2),
  ('EBITDA', 'Efecto costo FX (TC 3.72->3.81)', -300000, 3),
  ('EBITDA', 'Descuento comercial defensivo', -120000, 4),
  ('EBITDA', 'Fletes y personal', -180000, 5),
  ('EBITDA', 'Ahorro marketing y variables', 180000, 6),
  ('EBITDA', 'EBITDA real H1', 2350000, 7)
on conflict do nothing;

insert into fpa_parametros (clave, valor, etiqueta) values
  ('tc_ppto', 3.72, 'Tipo de cambio presupuesto 2026'),
  ('tc_real_h1', 3.81, 'TC promedio real H1'),
  ('tc_jun', 3.84, 'TC cierre junio'),
  ('tasa_ir', 0.295, 'Impuesto a la renta'),
  ('dias_h1', 181, 'Dias del semestre'),
  ('pct_compras_usd', 0.7, 'Compras en USD'),
  ('exposicion_usd', 1100000, 'Exposicion neta pasiva USD'),
  ('pico_deuda_oct', 11200000, 'Pico de deuda octubre (base)'),
  ('linea_adicional', 2500000, 'Linea revolvente propuesta')
on conflict do nothing;

insert into fpa_cxc_canal (canal, monto) values
  ('Mayorista', 3900000),
  ('Minorista', 2260000),
  ('Institucional', 2000000)
on conflict do nothing;

insert into fpa_inv_linea (linea, monto) values
  ('Abarrotes importados', 4100000),
  ('Cuidado del hogar', 3350000)
on conflict do nothing;

insert into fpa_acciones (id, nombre, efecto_caja, efecto_py, kpi) values
  ('A1', 'Cobranza institucional + pronto pago', 950000, '- S/ 60k descuento financiero', 'DSO 52 -> 46 dias'),
  ('A2', 'Ajuste lista de precios 2H (+2%)', 550000, '+ S/ 550k margen', 'Margen bruto +90 pbs en 2H'),
  ('A3', 'Recorte compra hogar -15%', 700000, 'neutro', 'DIO 61 -> 55 dias'),
  ('A4', 'Forward 50% exposicion 90 dias', 0, 'acota riesgo 110k -> 55k por 10 cts', 'Exposicion neta USD 1.10M -> 0.55M'),
  ('A5', 'Linea revolvente +S/ 2.5M', 2500000, '- S/ 90k intereses 2H', 'Cubre pico de octubre')
on conflict do nothing;

-- Verificacion post-carga (deben devolver una fila 'OK' cada una) --
-- select case when sum(monto)=28400000 then 'OK ventas REAL' else 'FALLA' end from fpa_ventas where version='REAL';
-- select case when sum(monto)=2000000 then 'OK aging' else 'FALLA' end from fpa_cxc_aging;
-- select case when sum(stock_u*costo_u)=1713800 then 'OK skus' else 'FALLA' end from fpa_inv_sku;