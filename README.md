# Commands
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
#config.ini (replace with local database)
uvicorn app.main:app --reload


# Todo:
- Currently, clicking "Proceed to Payment" directly creates the order.
- The order should only be created after a successful payment to prevent users from going back to the previous page before completing the payment.
- The order should be linked to the corresponding user ID (it needs to be associated with the user).