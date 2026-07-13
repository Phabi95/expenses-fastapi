import requests

from constants import API_URL


class ApiClient:
    def __init__(
        self, base_url: str = API_URL, cookies: dict | None = None, timeout: int = 5
    ):
        self.base_url = base_url
        self.cookies = cookies
        self.timeout = timeout

    def login(self, username: str, password: str) -> requests.Response:
        return requests.post(
            f"{self.base_url}/auth/login",
            data={"username": username, "password": password},
            timeout=self.timeout,
        )

    def register(self, email: str, password: str) -> requests.Response:
        return requests.post(
            f"{self.base_url}/auth/register",
            json={"email": email, "password": password},
            timeout=self.timeout,
        )

    def forgot_password(self, email: str) -> requests.Response:
        return requests.post(
            f"{self.base_url}/auth/forgot_password",
            json=email,
            timeout=self.timeout,
        )

    def reset_password(self, token: str, new_password: str) -> requests.Response:
        return requests.post(
            f"{self.base_url}/auth/reset_password",
            json={"token": token, "new_password": new_password},
            timeout=self.timeout,
        )

    def get_admin_dashboard(self) -> requests.Response:
        return requests.get(
            f"{self.base_url}/admin/dashboard",
            cookies=self.cookies,
            timeout=self.timeout,
        )

    def create_expense(
        self, amount: float, category: str, payment_method: str
    ) -> requests.Response:
        return requests.post(
            f"{self.base_url}/expenses/",
            json={
                "amount": amount,
                "category": category,
                "payment_method": payment_method,
            },
            cookies=self.cookies,
            timeout=self.timeout,
        )

    def get_expense(self, expense_id: int) -> requests.Response:
        return requests.get(
            f"{self.base_url}/expenses/{expense_id}",
            cookies=self.cookies,
            timeout=self.timeout,
        )

    def update_expense(
        self, expense_id: int, amount: float, category: str, payment_method: str
    ) -> requests.Response:
        return requests.patch(
            f"{self.base_url}/expenses/{expense_id}",
            json={
                "amount": amount,
                "category": category,
                "payment_method": payment_method,
            },
            cookies=self.cookies,
            timeout=self.timeout,
        )

    def delete_expense(self, expense_id: int) -> requests.Response:
        return requests.delete(
            f"{self.base_url}/expenses/{expense_id}",
            cookies=self.cookies,
            timeout=self.timeout,
        )

    def list_expenses(self, params: dict) -> requests.Response:
        return requests.get(
            f"{self.base_url}/expenses/",
            cookies=self.cookies,
            params=params,
            timeout=self.timeout,
        )

    def get_purchases_summary(self, params: dict) -> requests.Response:
        return requests.get(
            f"{self.base_url}/expenses/Purchases",
            cookies=self.cookies,
            params=params,
            timeout=self.timeout,
        )
