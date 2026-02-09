from abc import ABC, abstractmethod


class PaymentInterface(ABC):
    """Payment interface"""

    @abstractmethod
    def handle_payment(self, *args, **kwargs) -> dict:
        """handles according to platforms"""
        pass

    @abstractmethod
    def handle_card_payment(
        self, *args, **kwargs
    ) -> dict:
        """handles card payment"""
        pass

    @abstractmethod
    def handle_general_payment(
        self, *args, **kwargs
    ) -> dict:
        """handles general payment"""
        pass
