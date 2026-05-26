-- Limpia todos los registros de la tabla 'titanic' en Supabase.
-- Úsalo si quieres eliminar todos los datos antiguos no deseados y mantener solo los registros nuevos.

DELETE FROM titanic;

-- Si tu tabla tiene una secuencia de id, reiníciala a 1 (opcional).
-- Cambia titanic_id_seq por el nombre real de tu secuencia si es distinto.
ALTER SEQUENCE IF EXISTS titanic_id_seq RESTART WITH 1;
