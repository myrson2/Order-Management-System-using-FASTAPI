from pathlib import Path
def json_product_cleaning() -> None:
    import json
    try:
        product_json = Path(__file__).resolve().parent.parent.joinpath("database\\products.json")
        print("JSON: ", product_json)
        if product_json.exists():
            with open(product_json, "r") as f:
                products = json.load(f)
            return products
        else:
            raise FileNotFoundError(f"The file {product_json} does not exist")
    except FileNotFoundError as e:
        print(e)

