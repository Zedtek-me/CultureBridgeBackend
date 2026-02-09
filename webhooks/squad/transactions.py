from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action

from services.payments.base import PaymentService, Training

from utils.core_utils import TrainingUtil
from utils.exception_utils import CustomException


class TransactionHooks(ViewSet):

    @action(detail=False, methods=["post"], url_path="squad-events")
    def handle_squad_txn_events(self, request):
        """verifies and update payment status"""
        payment_service = PaymentService("squad")
        event_data = request.data
        payment_ref = event_data.get("reference")
        p_txn = TrainingUtil.get_payment_txn({"txn_reference": payment_ref})
        txn_training: Training = p_txn.training
        response = payment_service.verify_txn_status(ref=payment_ref)
        txn_status = response.get("data", {}).get("status")
        amount = float(response.get("data", {}).get("amount", 0))
        if txn_status != "success" or amount < p_txn.amount:
            p_txn.status = "FAILED"
            p_txn.meta["failure_reason"] = (
                "Amount paid is lesser than actual fee!" if (amount < p_txn.amount) else
                "Unable to verify txn status from provider!"
            )
            p_txn.save()
            raise CustomException(
                "Unable to verify transaction at the moment; try again later!", 503
            )
        p_txn.status = "PAID"
        txn_training.payment_status = "PAID"
        txn_training.status = "ONGOING"
        p_txn.save()
        txn_training.save()
