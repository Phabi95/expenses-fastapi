import pandas as pd
import streamlit as st

from api_client import ApiClient
from constants import (
    CATEGORY_LABELS,
    CUSTOM_CSS,
    CATEGORY_DISPLAY_MAP,
    FILTER_CATEGORY_LABELS,
    FILTER_PAYMENT_LABELS,
    ORDER_LABELS,
    PAGE_CONFIG,
    PAYMENT_DISPLAY_MAP,
    PAYMENT_METHOD_LABELS,
    SORT_LABELS,
    SUMMARY_CATEGORY_LABELS,
)
from utils import (
    extract_detail,
    handle_expense_errors,
    handle_expired_session,
    run_request,
)


def render_url_reset_page(client: ApiClient, url_token: str) -> None:
    st.title("🔑 Επαναφορά Κωδικού")
    st.info("Το token βρέθηκε στο URL. Εισάγετε τον νέο σας κωδικό.")

    with st.form("reset_form_url"):
        new_password = st.text_input("Νέος Κωδικός", type="password")
        submit_reset = st.form_submit_button("Αποθήκευση Νέου Κωδικού", type="primary")

        if submit_reset:
            if not new_password:
                st.error("Συμπληρώστε τον νέο κωδικό.")
                return
            with st.spinner("Ενημέρωση κωδικού..."):
                res = run_request(client.reset_password, url_token, new_password)
            if res is None:
                return
            if res.status_code == 200:
                st.success("Ο κωδικός άλλαξε επιτυχώς! Μπορείτε να συνδεθείτε.")
                st.query_params.clear()
            else:
                st.error(extract_detail(res, "Το link έχει λήξει ή είναι άκυρο."))


def render_login_tab(client: ApiClient) -> None:
    with st.form("login_form"):
        username = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button(
            "Login", type="primary", use_container_width=True
        )

        if submit:
            if not username or not password:
                st.warning("Συμπληρώστε email και password.")
                return
            with st.spinner("Σύνδεση..."):
                res = run_request(client.login, username, password)
            if res is None:
                return
            if res.status_code == 200:
                st.session_state["token"] = res.cookies.get("access_token")
                st.toast("Επιτυχής σύνδεση!", icon="✅")
                st.rerun()
            else:
                st.error(extract_detail(res, "Λάθος στοιχεία σύνδεσης"))


def render_register_tab(client: ApiClient) -> None:
    st.caption("Δημιουργήστε νέο λογαριασμό.")
    with st.form("register_form"):
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Κωδικός", type="password", key="reg_password")
        reg_password_confirm = st.text_input(
            "Επιβεβαίωση Κωδικού", type="password", key="reg_password_confirm"
        )
        submit = st.form_submit_button(
            "Δημιουργία Λογαριασμού", type="primary", use_container_width=True
        )

        if submit:
            if not reg_email or not reg_password:
                st.warning("Συμπληρώστε email και κωδικό.")
                return
            if reg_password != reg_password_confirm:
                st.warning("Οι κωδικοί δεν ταιριάζουν.")
                return
            with st.spinner("Δημιουργία λογαριασμού..."):
                res = run_request(client.register, reg_email, reg_password)
            if res is None:
                return
            if res.status_code in (200, 201):
                st.success("Ο λογαριασμός δημιουργήθηκε! Μπορείτε να συνδεθείτε.")
                st.toast("Καλωσήρθατε!", icon="🎉")
            elif res.status_code == 422:
                st.error("Μη έγκυρο email ή κωδικός.")
            else:
                st.error(extract_detail(res, "Άγνωστο σφάλμα."))


def render_forgot_tab(client: ApiClient) -> None:
    st.caption("Θα σας σταλεί email με link επαναφοράς.")
    with st.form("forgot_form"):
        email = st.text_input("Email")
        submit = st.form_submit_button("Αποστολή", use_container_width=True)

        if submit:
            if not email:
                st.warning("Συμπληρώστε email.")
                return
            with st.spinner("Αποστολή..."):
                res = run_request(client.forgot_password, email)
            if res is None:
                return
            if res.status_code == 200:
                st.success("Ελέγξτε το email σας για οδηγίες.")
            else:
                st.error("Σφάλμα επικοινωνίας")


def render_manual_reset_tab(client: ApiClient) -> None:
    st.caption("Επικολλήστε το token που λάβατε.")
    with st.form("reset_form_manual"):
        token = st.text_input("Reset Token")
        new_password = st.text_input(
            "Νέος Κωδικός", type="password", key="manual_new_pw"
        )
        submit = st.form_submit_button("Επαναφορά", use_container_width=True)

        if submit:
            if not token or not new_password:
                st.warning("Συμπληρώστε token και νέο κωδικό.")
                return
            with st.spinner("Ενημέρωση..."):
                res = run_request(client.reset_password, token, new_password)
            if res is None:
                return
            if res.status_code == 200:
                st.success("Ο κωδικός άλλαξε επιτυχώς!")
            else:
                st.error(extract_detail(res, "Άκυρο token ή σφάλμα"))


def render_auth_page(client: ApiClient) -> None:
    left, mid, right = st.columns([1, 2, 1])
    with mid:
        st.title("💶 Διαχείριση Εξόδων")
        st.caption("Συνδεθείτε για να συνεχίσετε")

        tab_login, tab_register, tab_forgot, tab_reset = st.tabs(
            ["🔐 Σύνδεση", "📝 Εγγραφή", "❓ Ξέχασα Κωδικό", "🔄 Επαναφορά με Token"]
        )
        with tab_login:
            render_login_tab(client)
        with tab_register:
            render_register_tab(client)
        with tab_forgot:
            render_forgot_tab(client)
        with tab_reset:
            render_manual_reset_tab(client)


def render_sidebar(client: ApiClient, auth_cookies: dict | None) -> None:
    with st.sidebar:
        st.markdown("### 👤 Μενού Χρήστη")
        st.divider()

        with st.expander("🛡️ Πίνακας Διαχειριστή"):
            if st.button("Φόρτωση Admin Δεδομένων", use_container_width=True):
                if not auth_cookies:
                    st.error("Απαιτείται νέα σύνδεση.")
                else:
                    with st.spinner("Έλεγχος δικαιωμάτων..."):
                        admin_res = run_request(client.get_admin_dashboard)
                    if admin_res is not None:
                        if admin_res.status_code == 200:
                            st.session_state["admin_data"] = admin_res.json()
                        elif handle_expired_session(admin_res):
                            st.session_state["admin_data"] = None
                        else:
                            st.session_state["admin_data"] = None
                            if admin_res.status_code == 403:
                                st.error(
                                    extract_detail(
                                        admin_res, "Δεν έχετε δικαιώματα διαχειριστή."
                                    )
                                )
                            else:
                                st.error(
                                    f"Σφάλμα {admin_res.status_code}: {extract_detail(admin_res, '')}"
                                )

            admin_data = st.session_state.get("admin_data")
            if admin_data:
                st.success(admin_data.get("message", "Πρόσβαση επιτυχής"))
                extra = {k: v for k, v in admin_data.items() if k != "message"}
                if extra:
                    st.json(extra)

        st.divider()
        if st.button("🚪 Αποσύνδεση", use_container_width=True):
            st.session_state.pop("token", None)
            st.session_state.pop("admin_data", None)
            st.rerun()


def render_add_expense(client: ApiClient, auth_cookies: dict | None) -> None:
    with st.expander("➕ Προσθήκη Νέου Εξόδου", expanded=False):
        with st.form("add_expense_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                amount = st.number_input("Ποσό (€)", min_value=0.1, step=1.0)
            with c2:
                category_label = st.selectbox("Κατηγορία", list(CATEGORY_LABELS.keys()))
                category = CATEGORY_LABELS[category_label]
            with c3:
                payment_label = st.selectbox(
                    "Τρόπος Πληρωμής", list(PAYMENT_METHOD_LABELS.keys())
                )
                payment_method = PAYMENT_METHOD_LABELS[payment_label]

            submit = st.form_submit_button("Αποθήκευση", type="primary")

            if submit:
                if not auth_cookies:
                    st.error("Απαιτείται νέα σύνδεση.")
                    st.stop()
                with st.spinner("Αποθήκευση..."):
                    res = run_request(
                        client.create_expense, amount, category, payment_method
                    )
                if res is None:
                    return
                if res.status_code in (200, 201):
                    st.toast("Το έξοδο αποθηκεύτηκε!", icon="✅")
                elif handle_expired_session(res):
                    pass
                else:
                    st.error(extract_detail(res, f"Σφάλμα {res.status_code}"))


def render_edit_delete_expense(client: ApiClient, auth_cookies: dict | None) -> None:
    with st.expander("✏️ Επεξεργασία ή Διαγραφή Εξόδου", expanded=False):
        edit_id = st.number_input(
            "ID Εξόδου", min_value=1, step=1, key="edit_expense_id"
        )

        if st.button("🔎 Φόρτωση Εξόδου", key="load_expense_btn"):
            if not auth_cookies:
                st.error("Απαιτείται νέα σύνδεση.")
            else:
                with st.spinner("Φόρτωση..."):
                    res = run_request(client.get_expense, int(edit_id))
                if res is not None:
                    if res.status_code == 200:
                        st.session_state["edit_expense_data"] = res.json()
                    elif handle_expense_errors(res):
                        st.session_state["edit_expense_data"] = None
                    else:
                        st.session_state["edit_expense_data"] = None
                        st.error(extract_detail(res, f"Σφάλμα {res.status_code}"))

        edit_data = st.session_state.get("edit_expense_data")
        if not edit_data:
            return

        st.caption(f"Επεξεργασία εξόδου #{edit_data.get('id', edit_id)}")

        with st.form("update_expense_form"):
            ec1, ec2, ec3 = st.columns(3)
            with ec1:
                upd_amount = st.number_input(
                    "Ποσό (€)",
                    min_value=0.1,
                    step=1.0,
                    value=float(edit_data.get("amount", 0.1)),
                )
            with ec2:
                cat_labels_list = list(CATEGORY_LABELS.keys())
                cat_values_list = list(CATEGORY_LABELS.values())
                current_category = edit_data.get("category", "other")
                cat_idx = (
                    cat_values_list.index(current_category)
                    if current_category in cat_values_list
                    else 0
                )
                upd_category_label = st.selectbox(
                    "Κατηγορία", cat_labels_list, index=cat_idx
                )
                upd_category = CATEGORY_LABELS[upd_category_label]
            with ec3:
                pay_labels_list = list(PAYMENT_METHOD_LABELS.keys())
                pay_values_list = list(PAYMENT_METHOD_LABELS.values())
                current_payment = edit_data.get("payment_method", "card")
                pay_idx = (
                    pay_values_list.index(current_payment)
                    if current_payment in pay_values_list
                    else 0
                )
                upd_payment_label = st.selectbox(
                    "Τρόπος Πληρωμής", pay_labels_list, index=pay_idx
                )
                upd_payment_method = PAYMENT_METHOD_LABELS[upd_payment_label]

            save = st.form_submit_button(
                "💾 Αποθήκευση Αλλαγών", type="primary", use_container_width=True
            )

            if save:
                with st.spinner("Ενημέρωση..."):
                    res = run_request(
                        client.update_expense,
                        int(edit_id),
                        upd_amount,
                        upd_category,
                        upd_payment_method,
                    )
                if res is not None:
                    if res.status_code == 200:
                        st.toast("Το έξοδο ενημερώθηκε!", icon="✅")
                        st.session_state["edit_expense_data"] = res.json()
                    elif handle_expense_errors(res):
                        pass
                    else:
                        st.error(extract_detail(res, f"Σφάλμα {res.status_code}"))

        st.divider()
        confirm_delete = st.checkbox(
            "Επιβεβαιώνω ότι θέλω να διαγράψω αυτό το έξοδο",
            key="confirm_delete_expense",
        )
        if st.button(
            "🗑️ Διαγραφή Εξόδου", disabled=not confirm_delete, key="delete_expense_btn"
        ):
            with st.spinner("Διαγραφή..."):
                res = run_request(client.delete_expense, int(edit_id))
            if res is not None:
                if res.status_code == 204:
                    st.toast("Το έξοδο διαγράφηκε!", icon="🗑️")
                    st.session_state["edit_expense_data"] = None
                    st.rerun()
                elif handle_expense_errors(res):
                    pass
                else:
                    st.error(extract_detail(res, f"Σφάλμα {res.status_code}"))


def render_summary(client: ApiClient, auth_cookies: dict | None) -> None:
    with st.expander("📈 Σύνοψη Εξόδων", expanded=False):
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            summary_category_label = st.selectbox(
                "Κατηγορία (προαιρετικό)",
                list(SUMMARY_CATEGORY_LABELS.keys()),
                key="summary_category",
            )
            summary_category = SUMMARY_CATEGORY_LABELS[summary_category_label]
        with sc2:
            summary_start = st.date_input("Από", value=None, key="summary_start")
        with sc3:
            summary_end = st.date_input("Έως", value=None, key="summary_end")

        if st.button("Υπολογισμός Συνόλου", use_container_width=True):
            if not auth_cookies:
                st.error("Απαιτείται νέα σύνδεση.")
                return

            params = {}
            if summary_category != "Όλες":
                params["category"] = summary_category
            if summary_start:
                params["start_date"] = summary_start.isoformat()
            if summary_end:
                params["end_date"] = summary_end.isoformat()

            with st.spinner("Υπολογισμός..."):
                res = run_request(client.get_purchases_summary, params)
            if res is None:
                return
            if res.status_code == 200:
                total = res.json().get("total", 0)
                try:
                    total = float(total)
                except (TypeError, ValueError):
                    total = 0.0
                st.metric("Σύνολο", f"{total:.2f} €")
            elif handle_expired_session(res):
                pass
            else:
                st.error(extract_detail(res, f"Σφάλμα {res.status_code}"))


def render_filters() -> dict:
    with st.expander("🔍 Φίλτρα & Ταξινόμηση", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_category_label = st.selectbox(
                "Κατηγορία", list(FILTER_CATEGORY_LABELS.keys())
            )
            filter_category = FILTER_CATEGORY_LABELS[filter_category_label]
            filter_payment_label = st.selectbox(
                "Τρόπος Πληρωμής", list(FILTER_PAYMENT_LABELS.keys())
            )
            filter_payment = FILTER_PAYMENT_LABELS[filter_payment_label]
        with col2:
            filter_min = st.number_input("Ελάχιστο Ποσό", min_value=0.0, step=1.0)
            filter_max = st.number_input("Μέγιστο Ποσό", min_value=0.0, step=1.0)
        with col3:
            sort_by_label = st.selectbox("Ταξινόμηση κατά", list(SORT_LABELS.keys()))
            order_label = st.selectbox("Σειρά", list(ORDER_LABELS.keys()))
            sort_by = SORT_LABELS[sort_by_label]
            order = ORDER_LABELS[order_label]
            limit = st.number_input(
                "Όριο (Limit)", min_value=1, max_value=100, value=100
            )
            offset = st.number_input("Offset", min_value=0, value=0)

        load_clicked = st.button(
            "📥 Φόρτωση Δεδομένων", type="primary", use_container_width=True
        )

    params = {"sort_by": sort_by, "order": order, "limit": limit, "offset": offset}
    if filter_category != "Όλα":
        params["category"] = filter_category
    if filter_payment != "Όλα":
        params["payment_method"] = filter_payment
    if filter_min > 0:
        params["min_purchase"] = filter_min
    if filter_max > 0:
        params["max_purchase"] = filter_max

    return {"load_clicked": load_clicked, "params": params}


def render_expenses_table(data: list) -> None:
    df = pd.DataFrame(data)

    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        m1, m2, m3 = st.columns(3)
        m1.metric("Σύνολο Εξόδων", f"{df['amount'].sum():.2f} €")
        m2.metric("Μέσος Όρος", f"{df['amount'].mean():.2f} €")
        m3.metric("Πλήθος Εγγραφών", len(df))

    df_display = df.copy()
    if "payment_method" in df_display.columns:
        df_display["payment_method"] = (
            df_display["payment_method"]
            .map(PAYMENT_DISPLAY_MAP)
            .fillna(df_display["payment_method"])
        )
    if "category" in df_display.columns:
        df_display["category"] = (
            df_display["category"]
            .map(CATEGORY_DISPLAY_MAP)
            .fillna(df_display["category"])
        )

    st.dataframe(df_display, use_container_width=True, hide_index=True)

    if "category" in df.columns and "amount" in df.columns:
        st.subheader("📊 Έξοδα ανά Κατηγορία")
        st.bar_chart(df.groupby("category")["amount"].sum())


def render_expenses_list(client: ApiClient, auth_cookies: dict | None) -> None:
    st.divider()
    st.header("📋 Λίστα Εξόδων")

    filters = render_filters()

    if filters["load_clicked"]:
        if not auth_cookies:
            st.error("Απαιτείται νέα σύνδεση.")
            st.stop()

        with st.spinner("Φόρτωση..."):
            res = run_request(client.list_expenses, filters["params"])

        if res is None:
            st.session_state["expenses_data"] = None
        elif res.status_code == 200:
            st.session_state["expenses_data"] = res.json()
        elif handle_expired_session(res):
            st.session_state["expenses_data"] = None
        else:
            st.error("Σφάλμα κατά την ανάκτηση δεδομένων.")
            st.session_state["expenses_data"] = None

    data = st.session_state.get("expenses_data")
    if data:
        render_expenses_table(data)
    elif data == []:
        st.info("Δεν βρέθηκαν εγγραφές.")
    else:
        st.caption("Πατήστε «Φόρτωση Δεδομένων» για να δείτε τα έξοδά σας.")


def render_authenticated_app() -> None:
    token = st.session_state.get("token")
    auth_cookies = {"access_token": token} if token else None
    client = ApiClient(cookies=auth_cookies)

    render_sidebar(client, auth_cookies)

    st.title("💶 Διαχείριση Εξόδων")

    render_add_expense(client, auth_cookies)
    st.divider()
    render_edit_delete_expense(client, auth_cookies)
    render_summary(client, auth_cookies)
    render_expenses_list(client, auth_cookies)


def main() -> None:
    st.set_page_config(**PAGE_CONFIG)
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    client = ApiClient()
    url_token = st.query_params.get("token")

    if url_token:
        render_url_reset_page(client, url_token)
    elif "token" not in st.session_state:
        render_auth_page(client)
    else:
        render_authenticated_app()


if __name__ == "__main__":
    main()
