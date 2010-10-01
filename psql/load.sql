-- Command to create db:
-- createdb -E UTF8 -T template0 --lc-collate=pt_BR.UTF8 --lc-ctype=pt_BR.UTF8 cebimar

-- Create tsvector columns for files
ALTER TABLE meta_image ADD COLUMN tsv tsvector;
ALTER TABLE meta_video ADD COLUMN tsv tsvector;

-- Needed for the function update_tsv()
CREATE LANGUAGE 'plpgsql';

-- Used for case-insensitive search
CREATE OR REPLACE FUNCTION make_ai(TEXT) RETURNS TEXT
AS $$
    SELECT translate($1, 'áàâãäåāăąÁÀÂÃÄÅĀĂĄéèêëēĕėęěÉÈÊËĒĔĖĘĚìíîïìĩīĭÌÍÎÏÌĨĪĬóòôõöōŏőÒÓÔÕÖŌŎŐùúûüũūŭůÙÚÛÜŨŪŬŮç', 'aaaaaaaaaaaaaaaaaaeeeeeeeeeeeeeeeeeeiiiiiiiiiiiiiiiioooooooooooooooouuuuuuuuuuuuuuuuc');
$$ LANGUAGE SQL;

-- Concatenate strings
-- PostgreSQL 9.0 has a function for this
CREATE AGGREGATE concat(
  basetype    = text,
  sfunc       = textcat,
  stype       = text,
  initcond    = ''
);

-- Function that updates tsv column after table is updated
CREATE OR REPLACE FUNCTION update_tsv() RETURNS trigger AS $$
DECLARE

authors varchar;
taxa varchar;
genera varchar;
spp varchar;
parents varchar;
tags varchar;

taxa_common varchar;
genera_common varchar;
spp_common varchar;
parents_common varchar;

source varchar;
sublocation varchar;
city varchar;
state varchar;
country varchar;

BEGIN

-- Select directly from id
SELECT name INTO STRICT source FROM meta_source WHERE id = NEW.source_id;
SELECT name INTO STRICT sublocation FROM meta_sublocation WHERE id = NEW.sublocation_id;
SELECT name INTO STRICT city FROM meta_city WHERE id = NEW.city_id;
SELECT name INTO STRICT state FROM meta_state WHERE id = NEW.state_id;
SELECT name INTO STRICT country FROM meta_country WHERE id = NEW.country_id;

-- Many to many relationships
SELECT concat((SELECT name FROM meta_tag WHERE id = tag_id)||' ') INTO tags FROM meta_tag_images WHERE image_id = NEW.id;
SELECT concat((SELECT name FROM meta_author WHERE id = author_id)||' ') INTO authors FROM meta_author_images WHERE image_id = NEW.id;
SELECT concat((SELECT name FROM meta_taxon WHERE id = taxon_id)||' ') INTO taxa FROM meta_taxon_images WHERE image_id = NEW.id;
SELECT concat((SELECT name FROM meta_genus WHERE id = genus_id)||' ') INTO genera FROM meta_genus_images WHERE image_id = NEW.id;
SELECT concat((SELECT name FROM meta_species WHERE id = species_id)||' ') INTO spp FROM meta_species_images WHERE image_id = NEW.id;

SELECT concat((SELECT common FROM meta_taxon WHERE id = taxon_id)||' ') INTO taxa_common FROM meta_taxon_images WHERE image_id = NEW.id;
SELECT concat((SELECT common FROM meta_genus WHERE id = genus_id)||' ') INTO genera_common FROM meta_genus_images WHERE image_id = NEW.id;
SELECT concat((SELECT common FROM meta_species WHERE id = species_id)||' ') INTO spp_common FROM meta_species_images WHERE image_id = NEW.id;

-- Parent from taxon
SELECT concat((SELECT name FROM meta_taxon WHERE id = (SELECT coalesce(parent_id, 1) FROM meta_taxon WHERE id = taxon_id))||' ') INTO parents FROM meta_taxon_images WHERE image_id = NEW.id;
SELECT concat((SELECT common FROM meta_taxon WHERE id = (SELECT coalesce(parent_id, 1) FROM meta_taxon WHERE id = taxon_id))||' ') INTO parents_common FROM meta_taxon_images WHERE image_id = NEW.id;

NEW.tsv := 
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(tags, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(tags), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(NEW.title, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(NEW.title), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(NEW.caption, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(NEW.caption), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(NEW.notes, '')), 'D') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(NEW.notes), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(authors, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(authors), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(taxa, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(taxa), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(genera, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(genera), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(spp, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(spp), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(taxa_common, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(taxa_common), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(genera_common, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(genera_common), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(spp_common, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(spp_common), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(source, '')), 'C') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(source), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(sublocation, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(sublocation), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(city, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(city), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(state, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(state), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(country, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(country), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(parents, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(parents), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(parents_common, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(parents_common), '')), 'A');
return new;
END                 
$$ LANGUAGE plpgsql;

-- Trigger to keep up with updates
CREATE TRIGGER updatetsvectors BEFORE INSERT OR UPDATE ON meta_image 
    FOR EACH ROW EXECUTE PROCEDURE update_tsv();
CREATE TRIGGER updatetsvectors BEFORE INSERT OR UPDATE ON meta_video
    FOR EACH ROW EXECUTE PROCEDURE update_tsv();

-- Create index to optimize search
CREATE INDEX meta_image_tsv ON meta_image USING gin(tsv);
CREATE INDEX meta_video_tsv ON meta_video USING gin(tsv);
