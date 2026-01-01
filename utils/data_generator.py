import random

from faker import Faker

from utils.file_manager import FileManager

fake = Faker()


class DataGenerator:
    """Generate fake ServeRest fixtures for users, products, and carts."""

    @staticmethod
    def generate_user_data_for_create(num_users):
        """Create user payloads for POST scenarios."""
        file_name = "create_user_data.json"
        users = []

        num_admins = 0

        for _ in range(num_users):
            if num_admins == 0 or random.random() < 0.2:
                is_admin = True
                num_admins += 1
            else:
                is_admin = False

            users.append(
                {
                    "nome": fake.name(),
                    "email": fake.email(),
                    "password": fake.password(),
                    "administrador": str(is_admin).lower(),
                }
            )

        if num_admins == 0:
            if not users:
                raise ValueError("Cannot set admin: users list is empty")
            random_user = random.choice(users)
            random_user["administrador"] = "true"

        data = {"usuarios": users}

        FileManager.clear_file(file_name)
        FileManager.update_file(file_name, data)

    @staticmethod
    def generate_user_data_for_update(num_users):
        """Create user payloads for PUT scenarios."""
        file_name = "update_user_data.json"
        users = []

        num_admins = 0

        for _ in range(num_users):
            if num_admins == 0 or random.random() < 0.2:
                is_admin = True
                num_admins += 1
            else:
                is_admin = False

            users.append(
                {
                    "nome": fake.name(),
                    "email": fake.email(),
                    "password": fake.password(),
                    "administrador": str(is_admin).lower(),
                }
            )

        if num_admins == 0:
            if not users:
                raise ValueError("Cannot set admin: users list is empty")
            random_user = random.choice(users)
            random_user["administrador"] = "true"

        data = {"usuarios": users}

        FileManager.clear_file(file_name)
        FileManager.update_file(file_name, data)

    @staticmethod
    def generate_product_data_for_create(num_products):
        """Create product payloads for POST scenarios."""
        file_name = "create_product_data.json"
        products = []

        for _ in range(num_products):
            products.append(
                {
                    "nome": fake.catch_phrase(),
                    "preco": random.randint(100, 1000),
                    "descricao": fake.catch_phrase(),
                    "quantidade": random.randint(10, 100),
                }
            )

        data = {"produtos": products}

        FileManager.clear_file(file_name)
        FileManager.update_file(file_name, data)

    @staticmethod
    def generate_product_data_for_update(num_products):
        """Create product payloads for PUT scenarios."""
        file_name = "update_product_data.json"
        products = []

        for _ in range(num_products):
            products.append(
                {
                    "nome": fake.catch_phrase(),
                    "preco": random.randint(100, 1000),
                    "descricao": fake.catch_phrase(),
                    "quantidade": random.randint(10, 100),
                }
            )

        data = {"produtos": products}

        FileManager.clear_file(file_name)
        FileManager.update_file(file_name, data)

    @staticmethod
    def generate_cart_data_for_create(
        product_ids, products_quantity, num_carts, max_products_per_cart, max_quantity_per_product
    ):
        """Create cart payloads constrained by available inventory."""
        if not product_ids:
            raise ValueError("product_ids cannot be empty")
        if not products_quantity:
            raise ValueError("products_quantity cannot be empty")

        file_name = "create_cart_data.json"
        carts = []

        for _ in range(num_carts):
            num_products = min(random.randint(1, max_products_per_cart), len(product_ids))
            products = []
            available_products = [product_id for product_id in product_ids if products_quantity.get(product_id, 0) > 0]

            random.shuffle(available_products)
            available_products = available_products[:num_products]

            for product_id in available_products:
                available_quantity = products_quantity.get(product_id, 0)
                quantity_cap = min(max_quantity_per_product, available_quantity)
                quantity = min(
                    random.randint(1, quantity_cap),
                    max_quantity_per_product,
                )

                product = {"idProduto": product_id, "quantidade": quantity}
                products.append(product)
                products_quantity[product_id] -= quantity

            cart = {"produtos": products}
            carts.append(cart)

        data = {"carrinhos": carts}

        FileManager.clear_file(file_name)
        FileManager.update_file(file_name, data)
