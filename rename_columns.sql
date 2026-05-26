-- Script para renombrar las columnas de la tabla 'titanic' en Supabase
-- Ejecuta esto en el SQL Editor de Supabase: https://app.supabase.com/project/[tu-proyecto]/sql/new

-- Renombrar columnas en español
ALTER TABLE titanic RENAME COLUMN survived TO sobrevivio;
ALTER TABLE titanic RENAME COLUMN pclass TO clase;
ALTER TABLE titanic RENAME COLUMN sex TO sexo;
ALTER TABLE titanic RENAME COLUMN age TO edad;
ALTER TABLE titanic RENAME COLUMN sibsp TO hermanos_cony;
ALTER TABLE titanic RENAME COLUMN parch TO padres_hijos;
ALTER TABLE titanic RENAME COLUMN fare TO tarifa;
ALTER TABLE titanic RENAME COLUMN embarked TO puerto_embarque;
ALTER TABLE titanic RENAME COLUMN who TO quien;
ALTER TABLE titanic RENAME COLUMN adult_male TO adulto_hombre;
ALTER TABLE titanic RENAME COLUMN embark_town TO ciudad_puerto;
ALTER TABLE titanic RENAME COLUMN alone TO solo_a;
ALTER TABLE titanic RENAME COLUMN class TO categorías;

-- Verificar que se renombraron correctamente
SELECT * FROM titanic LIMIT 1;
