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
taxa_name varchar;
taxa_common varchar;
taxa_rank varchar;
taxa_parents_name varchar;
taxa_parents_common varchar;
tags varchar;
tagcats varchar;

sublocation varchar;
city varchar;
state varchar;
country varchar;

title_en varchar;
caption_en varchar;
notes_en varchar;
country_en varchar;
tags_en varchar;
tagcats_en varchar;
taxa_common_en varchar;
taxa_rank_en varchar;
taxa_parents_common_en varchar;

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
SELECT concat((SELECT name FROM meta_taxon WHERE id = taxon_id)||' ') INTO taxa_name FROM meta_taxon_images WHERE image_id = NEW.id;
SELECT concat((SELECT common FROM meta_taxon WHERE id = taxon_id)||' ') INTO taxa_common FROM meta_taxon_images WHERE image_id = NEW.id;
SELECT concat((SELECT rank FROM meta_taxon WHERE id = taxon_id)||' ') INTO taxa_rank FROM meta_taxon_images WHERE image_id = NEW.id;

-- Parent from taxa
SELECT concat((SELECT name FROM meta_taxon WHERE id = (SELECT coalesce(parent_id, 1) FROM meta_taxon WHERE id = taxon_id))||' ') INTO taxa_parents_name FROM meta_taxon_images WHERE image_id = NEW.id;
SELECT concat((SELECT common FROM meta_taxon WHERE id = (SELECT coalesce(parent_id, 1) FROM meta_taxon WHERE id = taxon_id))||' ') INTO taxa_parents_common FROM meta_taxon_images WHERE image_id = NEW.id;
-- Parents from tags (tagcats)
SELECT concat((SELECT name FROM meta_tagcategory WHERE id = (SELECT coalesce(parent_id, 1) FROM meta_tag WHERE id = tag_id))||' ') INTO tagcats FROM meta_tag_images WHERE image_id = NEW.id;

-- Translations
-- title
SELECT value INTO title_en FROM datatrans_keyvalue WHERE digest=(SELECT digest FROM datatrans_keyvalue WHERE value=NEW.title AND language='pt-br') AND language='en';
-- caption
SELECT value INTO caption_en FROM datatrans_keyvalue WHERE digest=(SELECT digest FROM datatrans_keyvalue WHERE value=NEW.caption AND language='pt-br') AND language='en';
-- notes
SELECT value INTO notes_en FROM datatrans_keyvalue WHERE digest=(SELECT digest FROM datatrans_keyvalue WHERE value=NEW.notes AND language='pt-br') AND language='en';
-- country
SELECT value INTO country_en FROM datatrans_keyvalue WHERE digest=(SELECT digest FROM datatrans_keyvalue WHERE value=country AND language='pt-br') AND language='en';

-- Many to many
-- tags
SELECT concat((SELECT (SELECT value FROM datatrans_keyvalue WHERE digest=(SELECT digest FROM datatrans_keyvalue WHERE value=name AND language='pt-br') AND language='en') FROM meta_tag WHERE id = tag_id)||' ') INTO tags_en FROM meta_tag_images WHERE image_id = NEW.id;
-- tagcats
SELECT concat((SELECT (SELECT value FROM datatrans_keyvalue WHERE digest=(SELECT digest FROM datatrans_keyvalue WHERE value=name AND language='pt-br') AND language='en') FROM meta_tagcategory WHERE id = (SELECT coalesce(parent_id, 1) FROM meta_tag WHERE id = tag_id))||' ') INTO tagcats_en FROM meta_tag_images WHERE image_id = NEW.id;
-- taxa common
SELECT concat((SELECT (SELECT value FROM datatrans_keyvalue WHERE digest=(SELECT digest FROM datatrans_keyvalue WHERE value=common AND language='pt-br') AND language='en') FROM meta_taxon WHERE id = taxon_id)||' ') INTO taxa_common_en FROM meta_taxon_images WHERE image_id = NEW.id;
-- taxa rank
SELECT concat((SELECT (SELECT value FROM datatrans_keyvalue WHERE digest=(SELECT digest FROM datatrans_keyvalue WHERE value=rank AND language='pt-br') AND language='en') FROM meta_taxon WHERE id = taxon_id)||' ') INTO taxa_rank_en FROM meta_taxon_images WHERE image_id = NEW.id;
-- taxa parents common
SELECT concat((SELECT (SELECT value FROM datatrans_keyvalue WHERE digest=(SELECT digest FROM datatrans_keyvalue WHERE value=common AND language='pt-br') AND language='en') FROM meta_taxon WHERE id = (SELECT coalesce(parent_id, 1) FROM meta_taxon WHERE id = taxon_id))||' ') INTO taxa_parents_common_en FROM meta_taxon_images WHERE image_id = NEW.id;

SELECT concat((SELECT (SELECT value FROM datatrans_keyvalue WHERE digest=(SELECT digest FROM datatrans_keyvalue WHERE value=name AND language='pt-br') AND language='en') FROM meta_tagcategory WHERE id = (SELECT coalesce(parent_id, 1) FROM meta_tag WHERE id = tag_id))||' ') INTO tagcats_en FROM meta_tag_images WHERE image_id = NEW.id;

NEW.tsv := 
    -- tags
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(tags, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(tags), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.english', COALESCE(tags_en, '')), 'A') ||
    -- tagcats
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(tagcats, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(tagcats), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.english', COALESCE(tagcats_en, '')), 'A') ||
    -- title
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(NEW.title, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(NEW.title), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.english', COALESCE(title_en, '')), 'A') ||
    -- caption
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(NEW.caption, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(NEW.caption), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.english', COALESCE(caption_en, '')), 'A') ||
    -- notes
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(NEW.notes, '')), 'D') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(NEW.notes), '')), 'D') ||
    setweight(to_tsvector('pg_catalog.english', COALESCE(notes_en, '')), 'D') ||
    -- authors
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(authors, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(authors), '')), 'A') ||
    -- sources
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(sources, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(sources), '')), 'A') ||
    -- taxa name
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(taxa_name, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.english', COALESCE(taxa_name, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(taxa_name), '')), 'A') ||
    -- taxa common
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(taxa_common, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(taxa_common), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.english', COALESCE(taxa_common_en, '')), 'A') ||
    -- taxa rank
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(taxa_rank, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(taxa_rank), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.english', COALESCE(taxa_rank_en, '')), 'A') ||
    -- taxa parents name
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(taxa_parents_name, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.english', COALESCE(taxa_parents_name, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(taxa_parents_name), '')), 'A') ||
    -- taxa parents common
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(taxa_parents_common, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(taxa_parents_common), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.english', COALESCE(taxa_parents_common_en, '')), 'A') ||
    -- sublocation
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(sublocation, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(sublocation), '')), 'A') ||
    -- city
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(city, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(city), '')), 'A') ||
    -- state
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(state, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(state), '')), 'A') ||
    -- country
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(country, '')), 'A') ||
    setweight(to_tsvector('pg_catalog.portuguese', COALESCE(make_ai(country), '')), 'A') ||
    setweight(to_tsvector('pg_catalog.english', COALESCE(country_en, '')), 'A');
    return new;
END
$$ LANGUAGE plpgsql;

-- Function that refreshes tsv column after translation table is updated
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
-- XXX Taking too long to respond after translation updates. Find better way.
--CREATE TRIGGER refreshall_tsv AFTER UPDATE ON datatrans_keyvalue EXECUTE 
--PROCEDURE refresh_tsv();

-- Create index to optimize search
CREATE INDEX meta_image_tsv ON meta_image USING gin(tsv);
CREATE INDEX meta_video_tsv ON meta_video USING gin(tsv);
