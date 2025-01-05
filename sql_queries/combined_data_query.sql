SELECT DISTINCT ON ("unique_id") 
  CASE
    WHEN LOWER("brand") IN ('maf', 'maf pro') THEN 'Maf Pro'
    ELSE "brand"
  END AS "brand",
  "New Title" AS "new_title",
  "Unicommerce SKU ID" AS "unicommerce_sku_id",
  "Combined_ASIN_ProductID" AS "Product_ID",
  "SKU" AS "sku_id",
  "order_date",
  "Platform" AS "platform",
  "gross_units",
  "Combined_GMV_Gross_Price" AS "Gross_Price",
  "fulfillment-channel" AS "fulfillment_channel",
  "sales-channel" AS "sales_channel",
  "unique_id"
FROM (
  SELECT
    "public"."AZ_Sales_Report"."purchase-date" AS "order_date",
    "public"."AZ_Sales_Report"."fulfillment-channel" AS "fulfillment-channel",
    "public"."AZ_Sales_Report"."sales-channel" AS "sales-channel",
    "public"."AZ_Sales_Report"."sku" AS "SKU",
    CASE
      WHEN "public"."AZ_Sales_Report"."quantity" = 0 THEN 1
      ELSE "public"."AZ_Sales_Report"."quantity"
    END AS "gross_units",
    CASE
      WHEN "Amazon Pricing Data - Sku"."Title" IS NULL THEN "public"."AZ_Sales_Report"."product-name"
      ELSE "Amazon Pricing Data - Sku"."Title"
    END AS "New Title",
    "public"."AZ_Sales_Report"."unique_id" AS "unique_id",
    "Amazon Pricing Data - Sku"."Brand Name" AS "brand",
    "Amazon Pricing Data - Sku"."Unicommerce SKU ID" AS "Unicommerce SKU ID",
    "public"."AZ_Sales_Report"."asin" AS "Combined_ASIN_ProductID",
    CASE
      WHEN "public"."AZ_Sales_Report"."item-price" IS NOT NULL THEN "public"."AZ_Sales_Report"."item-price"
      WHEN "public"."AZ_Sales_Report"."item-price" IS NULL THEN "Amazon Pricing Data - Sku"."Final Price"
    END AS "Combined_GMV_Gross_Price",
    'Amazon' AS "Platform"
  FROM
    "public"."AZ_Sales_Report"
  LEFT JOIN "public"."amazon_pricing_data" AS "Amazon Pricing Data - Sku"
    ON "public"."AZ_Sales_Report"."sku" = "Amazon Pricing Data - Sku"."SKU ID"

  UNION ALL

  SELECT
    "public"."FK_Sales_Report"."order_date" AS "order_date",
    'Flipkart' AS "fulfillment-channel",
    'Flipkart' AS "sales-channel",
    "public"."FK_Sales_Report"."sku_id" AS "SKU",
    "public"."FK_Sales_Report"."gross_units" AS "gross_units",
    "Fk Data - Sku"."Title" AS "New Title",
    "public"."FK_Sales_Report"."unique_id" AS "unique_id",
    "public"."FK_Sales_Report"."brand" AS "brand",
    "Fk Data - Sku"."ll" AS "Unicommerce SKU ID",
    "public"."FK_Sales_Report"."product_id" AS "Combined_ASIN_ProductID",
    "public"."FK_Sales_Report"."gmv" AS "Combined_GMV_Gross_Price",
    'Flipkart' AS "Platform"
  FROM
    "public"."FK_Sales_Report"
  LEFT JOIN "public"."fk_data" AS "Fk Data - Sku"
    ON "public"."FK_Sales_Report"."sku_id" = "Fk Data - Sku"."FK SKU ID"
) AS CombinedData
LIMIT 1048575;
