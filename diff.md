diff --git a/apps/orders/views.py b/apps/orders/views.py
index 1818c64..99688ad 100644
--- a/apps/orders/views.py
+++ b/apps/orders/views.py
@@ -3,6 +3,7 @@ from django.http import Http404
 from django.shortcuts import get_object_or_404, redirect, render
 from django.utils import timezone
 from yookassa import Configuration, Payment
+from yookassa.domain.exceptions import ApiError, NotFoundError
 
 from apps.catalog.models import Bouquet, Event
 
@@ -110,7 +111,12 @@ def payment_success(request, order_id):
     Configuration.account_id = settings.YOOKASSA_SHOP_ID
     Configuration.secret_key = settings.YOOKASSA_SECRET_KEY
 
-    payment = Payment.find_one(order.payment_id)
+    try:
+        payment = Payment.find_one(order.payment_id)
+    except NotFoundError:
+        return render(request, "order_done.html", {"order": order})
+    except ApiError:
+        return render(request, "order_done.html", {"order": order})
     if payment.status == "succeeded":
         order.status = "paid"
         order.paid_at = timezone.now()
