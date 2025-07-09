import json
from db_models import Product
def ingest_products(jsonpath: str):
    with open(jsonpath, "r", encoding='UTF-8') as f:
        products = json.load(f)
    
    products_with_embeddings = []

    for product in products:
        product_json = json.dumps(product, ensure_ascii=False)
        embedding = embedding_model.generate_embeddings(product_json)

        entry = (product, embedding)
        products_with_embeddings.append(entry)


    database.bulk_add_products(products_with_embeddings)

ingest_products('zus_coffee_products.json')

