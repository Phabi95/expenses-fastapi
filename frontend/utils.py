import requests
import streamlit as st


def extract_detail(res: requests.Response, fallback: str) -> str:

    try:
        return res.json().get("detail", fallback)
    except ValueError:
        return fallback


def handle_expired_session(res: requests.Response) -> bool:

    if res.status_code == 401:
        st.session_state.pop("token", None)
        st.error(
            f"{extract_detail(res, 'Η συνεδρία έληξε.')} Παρακαλώ συνδεθείτε ξανά."
        )
        st.rerun()
        return True
    return False


def handle_expense_errors(res: requests.Response) -> bool:

    if handle_expired_session(res):
        return True
    if res.status_code == 403:
        st.error(extract_detail(res, "Δεν έχετε πρόσβαση σε αυτό το έξοδο."))
        return True
    if res.status_code == 404:
        st.error(extract_detail(res, "Δεν βρέθηκε έξοδο με αυτό το ID."))
        return True
    return False


def run_request(fn, *args, **kwargs):

    try:
        return fn(*args, **kwargs)
    except requests.exceptions.ConnectionError:
        st.error("Δεν βρέθηκε σύνδεση με το API.")
        return None
    except Exception as e:
        st.error(f"Σφάλμα σύνδεσης: {e}")
        return None
