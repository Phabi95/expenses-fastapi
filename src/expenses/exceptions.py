from fastapi import HTTPException, status

class ExpenseNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Το έξοδο δεν βρέθηκε"
        )

class ExpenseAccessDenied(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Δεν έχετε δικαίωμα πρόσβασης σε αυτό το έξοδο"
        )