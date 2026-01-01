class Calculator:
    """Helpers for cart quantity and price math."""

    @staticmethod
    def calculate_quantity_total_in_cart(products):
        """Return the sum of all product quantities."""
        if not products:
            raise ValueError("Products list cannot be empty")

        quantity_total = 0
        for product in products:
            if "quantidade" not in product:
                raise ValueError(f"Product missing 'quantidade' field: {product}")
            quantity_total += product["quantidade"]
        return quantity_total

    @staticmethod
    def calculate_price_total_in_cart(price, quantity):
        """Return price multiplied by quantity."""
        price_total = price * quantity
        return price_total
