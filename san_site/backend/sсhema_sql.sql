CREATE OR REPLACE FUNCTION ReindexDB() RETURNS VOID AS
$$
BEGIN
  REINDEX TABLE san_site_courses;
  REINDEX TABLE san_site_currency;
  REINDEX TABLE san_site_customer;
  REINDEX TABLE san_site_customersfiles;
  REINDEX TABLE san_site_customersprices;
  REINDEX TABLE san_site_inventories;
  REINDEX TABLE san_site_order;
  REINDEX TABLE san_site_orderitem;
  REINDEX TABLE san_site_person;
  REINDEX TABLE san_site_prices;
  REINDEX TABLE san_site_pricessale;
  REINDEX TABLE san_site_product;
  REINDEX TABLE san_site_section;
  REINDEX TABLE san_site_store;
END
$$ LANGUAGE PLPGSQL;

DO $$
  BEGIN
    PERFORM reindexdb();
  END;
  $$;