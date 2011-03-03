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
-- TODO Add in next commit.
CREATE OR REPLACE FUNCTION update_tsv() RETURNS trigger AS $$
DECLARE

authors varchar;
sources varchar;
taxa varchar;
parents varchar;
tags varchar;

taxa_common varchar;
parents_common varchar;

sublocation varchar;
city varchar;
state varchar;
country varchar;

title_en varchar;
caption_en varchar;
notes_en varchar;
country_en varchar;
tags_en varchar;

BEGIN

-- Select directly from id
IF NEW.sublocation_id IS NOT NULL THEN
    SELECT name INTO STRICT sublocation FROM meta_sublocation WHERE id = NEW.sublocation_id;
END IF;
IF NEW.city_id IS NOT NULL THEN
    SELECT name INTO STRICT city FROM meta_city WHERE id = NEW.city_id;
END IF;
IF NEW.state_id IS NOT NULL THEN
    SELECT name INTO STRICT state FROM meta_state WHERE id = NEW.state_id;
END IF;
IF NEW.country_id IS NOT NULL THEN
    SELECT name INTO STRICT country FROM meta_country WHERE id = NEW.country_id;
END IF;

-- Many to many relationships
SELECT concat((SELECT name FROM meta_tag WHERE id = tag_id)||' ') INTO tags FROM meta_tag_images WHERE image_id = NEW.id;
SELECT concat((SELECT name FROM meta_author WHERE id = author_id)||' ') INTO authors FROM meta_author_images WHERE image_id = NEW.id;
SELECT concat((SELECT name FROM meta_source WHERE id = source_id)||' ') INTO sources FROM meta_source_images WHERE image_id = NEW.id;
SELECT concat((SELECT name FROM meta_taxon WHERE id = taxon_id)||' ') INTO taxa FROM meta_taxon_images WHERE image_id = NEW.id;

SELECT concat((SELECT common FROM meta_taxon WHERE id = taxon_id)||' ') INTO taxa_common FROM meta_taxon_images WHERE image_id = NEW.id;

-- Parent from taxa
SELECT concat((SELECT name FROM meta_taxon WHERE id = (SELECT coalesce(parent_id, 1) FROM meta_taxon WHERE id = taxon_id))||' ') INTO parents FROM meta_taxon_images WHERE image_id = NEW.id;
SELECT concat((SELECT common FROM meta_taxon WHERE id = (SELECT coalesce(parent_id, 1) FROM meta_taxon WHERE id = taxon_id))||' ') INTO parents_common FROM meta_taxon_images WHERE image_id = NEW.id;

-- Translations
SELECT value INTO title_en FROM datatrans_keyvalue WHERE digest=(SELECT digest FROM datatrans_keyvalue WHERE value=NEW.title AND language='pt-BR') AND language='en';
SELECT value INTO caption_en FROM datatrans_keyvalue WHERE digest=(SELECT digest FROM datatrans_keyvalue WHERE value=NEW.caption AND language='pt-BR') AND language='en';
SELECT value INTO notes_en FROM datatrans_keyvalue WHERE digest=(SELECT digest FROM datatrans_keyvalue WHERE value=NEW.notes AND language='pt-BR') AND language='en';
SELECT value INTO country_en FROM datatrans_keyvalue WHERE digest=(SELECT digest FROM datatrans_keyvalue WHERE value=country AND language='pt-BR') AND language='en';

-- Many to many
SELECT concat((SELECT (SELECT value FROM datatrans_keyvalue WHERE digest=(SELECT digest FROM datatrans_keyvalue WHERE value=name AND language='pt-BR') AND language='en') FROM meta_tag WHERE id = tag_id)||' ') INTO tags_en FROM meta_tag_images WHERE image_id = NEW.id;


NEW.tsv := 
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(tags, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(tags), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.english', COALESCE(tags_en, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(NEW.title, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(NEW.title), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.english', COALESCE(title_en, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(NEW.caption, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(NEW.caption), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.english', COALESCE(caption_en, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(NEW.notes, '')), 'D') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(NEW.notes), '')), 'D') ||
    setweight(to_tsvector('pg_catalog.english', COALESCE(notes_en, '')), 'D') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(authors, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(authors), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(sources, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(sources), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(taxa, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(taxa), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(taxa_common, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(taxa_common), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(sublocation, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(sublocation), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(city, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(city), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(state, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(state), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(country, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(country), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.english', COALESCE(country_en, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(parents, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(parents), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(parents_common, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(parents_common), '')), 'A');
return new;
END
$$ LANGUAGE plpgsql;

-- Function that refreshes tsv column after translation table is updated
-- TODO Add in next commit.
CREATE OR REPLACE FUNCTION refresh_tsv() RETURNS trigger AS $$
BEGIN
    UPDATE meta_image SET tsv='';
    UPDATE meta_video SET tsv='';
    return new;
END
$$ LANGUAGE plpgsql;

-- Trigger to keep up with updates
CREATE TRIGGER update_imagetsv BEFORE INSERT OR UPDATE ON meta_image 
    FOR EACH ROW EXECUTE PROCEDURE update_tsv();
CREATE TRIGGER update_videotsv BEFORE INSERT OR UPDATE ON meta_video
    FOR EACH ROW EXECUTE PROCEDURE update_tsv();
-- TODO Add in next commit.
CREATE TRIGGER refreshall_tsv AFTER INSERT OR UPDATE ON datatrans_keyvalue EXECUTE PROCEDURE refresh_tsv();

-- Create index to optimize search
CREATE INDEX meta_image_tsv ON meta_image USING gin(tsv);
CREATE INDEX meta_video_tsv ON meta_video USING gin(tsv);
