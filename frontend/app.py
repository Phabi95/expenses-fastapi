import streamlit as st
import requests
import pandas as pd

API_URL = "http://api:80"


def handle_expired_session(res: requests.Response) -> bool:
    """401 (InvalidTokenException / TokenExpiredException): καθαρίζει το session."""
    if res.status_code == 401:
        st.session_state.pop("token", None)
        st.error(
            f"{extract_detail(res, 'Η συνεδρία έληξε.')} Παρακαλώ συνδεθείτε ξανά."
        )
        st.rerun()
        return True
    return False


def extract_detail(res, fallback: str) -> str:
    """Εξάγει το 'detail' μήνυμα από HTTPException responses του FastAPI."""
    try:
        return res.json().get("detail", fallback)
    except ValueError:
        return fallback


def handle_expense_errors(res: requests.Response) -> bool:
    """401 λήξη session, 403 ExpenseAccessDenied, 404 ExpenseNotFound."""
    if handle_expired_session(res):
        return True
    if res.status_code == 403:
        st.error(extract_detail(res, "Δεν έχετε πρόσβαση σε αυτό το έξοδο."))
        return True
    if res.status_code == 404:
        st.error(extract_detail(res, "Δεν βρέθηκε έξοδο με αυτό το ID."))
        return True
    return False


st.set_page_config(
    page_title="Διαχείριση Εξόδων",
    page_icon="💶",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    [data-testid="stMetric"] {
        background-color: #F1F3F4;
        padding: 15px 20px;
        border-radius: 12px;
        border: 1px solid #E0E0E0;
    }
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
    div.stButton > button[kind="primary"] {
        background-color: #2E7D32;
    }
    .block-container {
        padding-top: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

url_token = st.query_params.get("token")

if url_token:
    st.title("🔑 Επαναφορά Κωδικού")
    st.info("Το token βρέθηκε στο URL. Εισάγετε τον νέο σας κωδικό.")

    with st.form("reset_form_url"):
        new_password = st.text_input("Νέος Κωδικός", type="password")
        submit_reset = st.form_submit_button("Αποθήκευση Νέου Κωδικού", type="primary")

        if submit_reset:
            if not new_password:
                st.error("Συμπληρώστε τον νέο κωδικό.")
            else:
                with st.spinner("Ενημέρωση κωδικού..."):
                    data = {"token": url_token, "new_password": new_password}
                    try:
                        res = requests.post(
                            f"{API_URL}/auth/reset_password", json=data, timeout=5
                        )
                        if res.status_code == 200:
                            st.success(
                                "Ο κωδικός άλλαξε επιτυχώς! Μπορείτε να συνδεθείτε."
                            )
                            st.query_params.clear()
                        else:
                            st.error(
                                extract_detail(res, "Το link έχει λήξει ή είναι άκυρο.")
                            )
                    except requests.exceptions.ConnectionError:
                        st.error("Δεν βρέθηκε σύνδεση με το API.")


elif "token" not in st.session_state:
    left, mid, right = st.columns([1, 2, 1])
    with mid:
        st.title("💶 Διαχείριση Εξόδων")
        st.caption("Συνδεθείτε για να συνεχίσετε")

        tab_login, tab_register, tab_forgot, tab_reset = st.tabs(
            ["🔐 Σύνδεση", "📝 Εγγραφή", "❓ Ξέχασα Κωδικό", "🔄 Επαναφορά με Token"]
        )

        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Email")
                password = st.text_input("Password", type="password")
                login_submit = st.form_submit_button(
                    "Login", type="primary", use_container_width=True
                )

                if login_submit:
                    if not username or not password:
                        st.warning("Συμπληρώστε email και password.")
                    else:
                        with st.spinner("Σύνδεση..."):
                            try:
                                res = requests.post(
                                    f"{API_URL}/auth/login",
                                    data={"username": username, "password": password},
                                    timeout=5,
                                )
                                if res.status_code == 200:
                                    st.session_state["token"] = res.cookies.get(
                                        "access_token"
                                    )
                                    st.toast("Επιτυχής σύνδεση!", icon="✅")
                                    st.rerun()
                                else:
                                    st.error(
                                        extract_detail(res, "Λάθος στοιχεία σύνδεσης")
                                    )
                            except requests.exceptions.ConnectionError:
                                st.error("Δεν βρέθηκε σύνδεση με το API.")
                            except Exception as e:
                                st.error(f"Σφάλμα σύνδεσης: {e}")

        with tab_register:
            st.caption("Δημιουργήστε νέο λογαριασμό.")
            with st.form("register_form"):
                reg_email = st.text_input("Email", key="reg_email")
                reg_password = st.text_input(
                    "Κωδικός", type="password", key="reg_password"
                )
                reg_password_confirm = st.text_input(
                    "Επιβεβαίωση Κωδικού", type="password", key="reg_password_confirm"
                )
                register_submit = st.form_submit_button(
                    "Δημιουργία Λογαριασμού", type="primary", use_container_width=True
                )

                if register_submit:
                    if not reg_email or not reg_password:
                        st.warning("Συμπληρώστε email και κωδικό.")
                    elif reg_password != reg_password_confirm:
                        st.warning("Οι κωδικοί δεν ταιριάζουν.")
                    else:
                        with st.spinner("Δημιουργία λογαριασμού..."):
                            data = {"email": reg_email, "password": reg_password}
                            try:
                                res = requests.post(
                                    f"{API_URL}/register", json=data, timeout=5
                                )
                                if res.status_code in (200, 201):
                                    st.success(
                                        "Ο λογαριασμός δημιουργήθηκε! Μπορείτε να συνδεθείτε."
                                    )
                                    st.toast("Καλωσήρθατε!", icon="🎉")
                                elif res.status_code == 422:
                                    st.error("Μη έγκυρο email ή κωδικός.")
                                else:
                                    st.error(extract_detail(res, "Άγνωστο σφάλμα."))
                            except requests.exceptions.ConnectionError:
                                st.error("Δεν βρέθηκε σύνδεση με το API.")
                            except Exception as e:
                                st.error(f"Σφάλμα σύνδεσης: {e}")

        with tab_forgot:
            st.caption("Θα σας σταλεί email με link επαναφοράς.")
            with st.form("forgot_form"):
                email = st.text_input("Email")
                forgot_submit = st.form_submit_button(
                    "Αποστολή", use_container_width=True
                )

                if forgot_submit:
                    if not email:
                        st.warning("Συμπληρώστε email.")
                    else:
                        with st.spinner("Αποστολή..."):
                            try:
                                res = requests.post(
                                    f"{API_URL}/auth/forgot_password",
                                    json=email,
                                    timeout=5,
                                )
                                if res.status_code == 200:
                                    st.success("Ελέγξτε το email σας για οδηγίες.")
                                else:
                                    st.error("Σφάλμα επικοινωνίας")
                            except requests.exceptions.ConnectionError:
                                st.error("Δεν βρέθηκε σύνδεση με το API.")
                            except Exception as e:
                                st.error(f"Σφάλμα σύνδεσης: {e}")

        with tab_reset:
            st.caption("Επικολλήστε το token που λάβατε.")
            with st.form("reset_form_manual"):
                token = st.text_input("Reset Token")
                new_password = st.text_input(
                    "Νέος Κωδικός", type="password", key="manual_new_pw"
                )
                reset_submit = st.form_submit_button(
                    "Επαναφορά", use_container_width=True
                )

                if reset_submit:
                    if not token or not new_password:
                        st.warning("Συμπληρώστε token και νέο κωδικό.")
                    else:
                        with st.spinner("Ενημέρωση..."):
                            data = {"token": token, "new_password": new_password}
                            try:
                                res = requests.post(
                                    f"{API_URL}/auth/reset_password",
                                    json=data,
                                    timeout=5,
                                )
                                if res.status_code == 200:
                                    st.success("Ο κωδικός άλλαξε επιτυχώς!")
                                else:
                                    st.error(
                                        extract_detail(res, "Άκυρο token ή σφάλμα")
                                    )
                            except requests.exceptions.ConnectionError:
                                st.error("Δεν βρέθηκε σύνδεση με το API.")
                            except Exception as e:
                                st.error(f"Σφάλμα σύνδεσης: {e}")

else:
    token = st.session_state.get("token")
    auth_cookies = {"access_token": token} if token else None

    with st.sidebar:
        st.markdown("### 👤 Μενού Χρήστη")
        st.divider()

        with st.expander("🛡️ Πίνακας Διαχειριστή"):
            if st.button("Φόρτωση Admin Δεδομένων", use_container_width=True):
                if not auth_cookies:
                    st.error("Απαιτείται νέα σύνδεση.")
                else:
                    with st.spinner("Έλεγχος δικαιωμάτων..."):
                        try:
                            admin_res = requests.get(
                                f"{API_URL}/admin/dashboard",
                                cookies=auth_cookies,
                                timeout=5,
                            )
                            if admin_res.status_code == 200:
                                st.session_state["admin_data"] = admin_res.json()
                            elif handle_expired_session(admin_res):
                                st.session_state["admin_data"] = None
                            else:
                                st.session_state["admin_data"] = None
                                if admin_res.status_code == 403:
                                    st.error(
                                        extract_detail(
                                            admin_res,
                                            "Δεν έχετε δικαιώματα διαχειριστή.",
                                        )
                                    )
                                else:
                                    st.error(
                                        f"Σφάλμα {admin_res.status_code}: {extract_detail(admin_res, '')}"
                                    )
                        except requests.exceptions.ConnectionError:
                            st.error("Δεν βρέθηκε σύνδεση με το API.")

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

    st.title("💶 Διαχείριση Εξόδων")

    with st.expander("➕ Προσθήκη Νέου Εξόδου", expanded=False):
        with st.form("add_expense_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                purchase = st.number_input("Ποσό (€)", min_value=0.1, step=1.0)
            with c2:
                category_labels = {
                    "Σούπερ Μάρκετ": "supermarket",
                    "Ενοίκιο": "rent",
                    "Λογαριασμοί": "utilities",
                    "Ψυχαγωγία": "entertainment",
                    "Μετακίνηση": "transportation",
                    "Άλλο": "other",
                }
                category_label = st.selectbox("Κατηγορία", list(category_labels.keys()))
                category = category_labels[category_label]
            with c3:
                payment_method_labels = {
                    "Κάρτα": "card",
                    "Μετρητά": "cash",
                    "Τραπεζικό Έμβασμα": "bank_transfer",
                }
                payment_method_label = st.selectbox(
                    "Τρόπος Πληρωμής", list(payment_method_labels.keys())
                )
                payment_method = payment_method_labels[payment_method_label]

            submit = st.form_submit_button("Αποθήκευση", type="primary")

            if submit:
                if not auth_cookies:
                    st.error("Απαιτείται νέα σύνδεση.")
                    st.stop()
                data = {
                    "amount": purchase,
                    "category": category,
                    "payment_method": payment_method,
                }
                with st.spinner("Αποθήκευση..."):
                    try:
                        res = requests.post(
                            f"{API_URL}/expenses/",
                            json=data,
                            cookies=auth_cookies,
                            timeout=5,
                        )
                        if res.status_code in (200, 201):
                            st.toast("Το έξοδο αποθηκεύτηκε!", icon="✅")
                        elif handle_expired_session(res):
                            pass
                        else:
                            st.error(extract_detail(res, f"Σφάλμα {res.status_code}"))
                    except requests.exceptions.ConnectionError:
                        st.error("Δεν βρέθηκε σύνδεση με το API.")

    st.divider()

    with st.expander("✏️ Επεξεργασία ή Διαγραφή Εξόδου", expanded=False):
        edit_id = st.number_input(
            "ID Εξόδου", min_value=1, step=1, key="edit_expense_id"
        )

        if st.button("🔎 Φόρτωση Εξόδου", key="load_expense_btn"):
            if not auth_cookies:
                st.error("Απαιτείται νέα σύνδεση.")
            else:
                with st.spinner("Φόρτωση..."):
                    try:
                        res = requests.get(
                            f"{API_URL}/expenses/{int(edit_id)}",
                            cookies=auth_cookies,
                            timeout=5,
                        )
                        if res.status_code == 200:
                            st.session_state["edit_expense_data"] = res.json()
                        elif handle_expense_errors(res):
                            st.session_state["edit_expense_data"] = None
                        else:
                            st.session_state["edit_expense_data"] = None
                            st.error(extract_detail(res, f"Σφάλμα {res.status_code}"))
                    except requests.exceptions.ConnectionError:
                        st.error("Δεν βρέθηκε σύνδεση με το API.")

        edit_data = st.session_state.get("edit_expense_data")

        if edit_data:
            st.caption(f"Επεξεργασία εξόδου #{edit_data.get('id', edit_id)}")

            with st.form("update_expense_form"):
                ec1, ec2, ec3 = st.columns(3)
                with ec1:
                    upd_purchase = st.number_input(
                        "Ποσό (€)",
                        min_value=0.1,
                        step=1.0,
                        value=float(edit_data.get("amount", 0.1)),
                    )
                with ec2:
                    upd_category_labels = {
                        "Σούπερ Μάρκετ": "supermarket",
                        "Ενοίκιο": "rent",
                        "Λογαριασμοί": "utilities",
                        "Ψυχαγωγία": "entertainment",
                        "Μετακίνηση": "transportation",
                        "Άλλο": "other",
                    }
                    upd_cat_labels_list = list(upd_category_labels.keys())
                    upd_cat_values_list = list(upd_category_labels.values())
                    current_category = edit_data.get("category", "other")
                    cat_default_idx = (
                        upd_cat_values_list.index(current_category)
                        if current_category in upd_cat_values_list
                        else 0
                    )
                    upd_category_label = st.selectbox(
                        "Κατηγορία", upd_cat_labels_list, index=cat_default_idx
                    )
                    upd_category = upd_category_labels[upd_category_label]
                with ec3:
                    upd_payment_labels = {
                        "Κάρτα": "card",
                        "Μετρητά": "cash",
                        "Τραπεζικό Έμβασμα": "bank_transfer",
                    }
                    upd_labels_list = list(upd_payment_labels.keys())
                    upd_values_list = list(upd_payment_labels.values())
                    current_payment = edit_data.get("payment_method", "card")
                    default_idx = (
                        upd_values_list.index(current_payment)
                        if current_payment in upd_values_list
                        else 0
                    )
                    upd_payment_label = st.selectbox(
                        "Τρόπος Πληρωμής", upd_labels_list, index=default_idx
                    )
                    upd_payment_method = upd_payment_labels[upd_payment_label]

                save_update = st.form_submit_button(
                    "💾 Αποθήκευση Αλλαγών", type="primary", use_container_width=True
                )

                if save_update:
                    update_payload = {
                        "amount": upd_purchase,
                        "category": upd_category,
                        "payment_method": upd_payment_method,
                    }
                    with st.spinner("Ενημέρωση..."):
                        try:
                            res = requests.patch(
                                f"{API_URL}/expenses/{int(edit_id)}",
                                json=update_payload,
                                cookies=auth_cookies,
                                timeout=5,
                            )
                            if res.status_code == 200:
                                st.toast("Το έξοδο ενημερώθηκε!", icon="✅")
                                st.session_state["edit_expense_data"] = res.json()
                            elif handle_expense_errors(res):
                                pass
                            else:
                                st.error(
                                    extract_detail(res, f"Σφάλμα {res.status_code}")
                                )
                        except requests.exceptions.ConnectionError:
                            st.error("Δεν βρέθηκε σύνδεση με το API.")

            st.divider()
            confirm_delete = st.checkbox(
                "Επιβεβαιώνω ότι θέλω να διαγράψω αυτό το έξοδο",
                key="confirm_delete_expense",
            )
            if st.button(
                "🗑️ Διαγραφή Εξόδου",
                disabled=not confirm_delete,
                key="delete_expense_btn",
            ):
                with st.spinner("Διαγραφή..."):
                    try:
                        res = requests.delete(
                            f"{API_URL}/expenses/{int(edit_id)}",
                            cookies=auth_cookies,
                            timeout=5,
                        )
                        if res.status_code == 204:
                            st.toast("Το έξοδο διαγράφηκε!", icon="🗑️")
                            st.session_state["edit_expense_data"] = None
                            st.rerun()
                        elif handle_expense_errors(res):
                            pass
                        else:
                            st.error(extract_detail(res, f"Σφάλμα {res.status_code}"))
                    except requests.exceptions.ConnectionError:
                        st.error("Δεν βρέθηκε σύνδεση με το API.")

    # -- Σύνοψη εξόδων -----------------------------------------------------
    with st.expander("📈 Σύνοψη Εξόδων", expanded=False):
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            summary_category_labels = {
                "Όλες": "Όλες",
                "Σούπερ Μάρκετ": "supermarket",
                "Ενοίκιο": "rent",
                "Λογαριασμοί": "utilities",
                "Ψυχαγωγία": "entertainment",
                "Μετακίνηση": "transportation",
                "Άλλο": "other",
            }
            summary_category_label = st.selectbox(
                "Κατηγορία (προαιρετικό)",
                list(summary_category_labels.keys()),
                key="summary_category",
            )
            summary_category = summary_category_labels[summary_category_label]
        with sc2:
            summary_start = st.date_input("Από", value=None, key="summary_start")
        with sc3:
            summary_end = st.date_input("Έως", value=None, key="summary_end")

        if st.button("Υπολογισμός Συνόλου", use_container_width=True):
            if not auth_cookies:
                st.error("Απαιτείται νέα σύνδεση.")
            else:
                summary_params = {}
                if summary_category != "Όλες":
                    summary_params["category"] = summary_category
                if summary_start:
                    summary_params["start_date"] = summary_start.isoformat()
                if summary_end:
                    summary_params["end_date"] = summary_end.isoformat()

                with st.spinner("Υπολογισμός..."):
                    try:
                        res = requests.get(
                            f"{API_URL}/expenses/Purchases",
                            cookies=auth_cookies,
                            params=summary_params,
                            timeout=5,
                        )
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
                    except requests.exceptions.ConnectionError:
                        st.error("Δεν βρέθηκε σύνδεση με το API.")

    st.divider()
    st.header("📋 Λίστα Εξόδων")

    with st.expander("🔍 Φίλτρα & Ταξινόμηση", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_category_labels = {
                "Όλα": "Όλα",
                "Σούπερ Μάρκετ": "supermarket",
                "Ενοίκιο": "rent",
                "Λογαριασμοί": "utilities",
                "Ψυχαγωγία": "entertainment",
                "Μετακίνηση": "transportation",
                "Άλλο": "other",
            }
            filter_category_label = st.selectbox(
                "Κατηγορία", list(filter_category_labels.keys())
            )
            filter_category = filter_category_labels[filter_category_label]
            payment_labels = {
                "Όλα": "Όλα",
                "Κάρτα": "card",
                "Μετρητά": "cash",
                "Τραπεζικό Έμβασμα": "bank_transfer",
            }
            filter_payment_label = st.selectbox(
                "Τρόπος Πληρωμής", list(payment_labels.keys())
            )
            filter_payment = payment_labels[filter_payment_label]
        with col2:
            filter_min_purchase = st.number_input(
                "Ελάχιστο Ποσό", min_value=0.0, step=1.0
            )
            filter_max_purchase = st.number_input(
                "Μέγιστο Ποσό", min_value=0.0, step=1.0
            )
        with col3:
            sort_labels = {"Ημερομηνία": "created_at", "Ποσό": "amount"}
            order_labels = {
                "Νεότερα/Μεγαλύτερα πρώτα": "desc",
                "Παλαιότερα/Μικρότερα πρώτα": "asc",
            }
            sort_by_label = st.selectbox("Ταξινόμηση κατά", list(sort_labels.keys()))
            order_label = st.selectbox("Σειρά", list(order_labels.keys()))
            sort_by = sort_labels[sort_by_label]
            order = order_labels[order_label]
            limit = st.number_input(
                "Όριο (Limit)", min_value=1, max_value=100, value=100
            )
            offset = st.number_input("Offset", min_value=0, value=0)

        load_clicked = st.button(
            "📥 Φόρτωση Δεδομένων", type="primary", use_container_width=True
        )

    if load_clicked:
        if not auth_cookies:
            st.error("Απαιτείται νέα σύνδεση.")
            st.stop()

        query_params = {
            "sort_by": sort_by,
            "order": order,
            "limit": limit,
            "offset": offset,
        }
        if filter_category != "Όλα":
            query_params["category"] = filter_category
        if filter_payment != "Όλα":
            query_params["payment_method"] = filter_payment
        if filter_min_purchase > 0:
            query_params["min_purchase"] = filter_min_purchase
        if filter_max_purchase > 0:
            query_params["max_purchase"] = filter_max_purchase

        with st.spinner("Φόρτωση..."):
            try:
                res = requests.get(
                    f"{API_URL}/expenses/",
                    cookies=auth_cookies,
                    params=query_params,
                    timeout=5,
                )
                if res.status_code == 200:
                    st.session_state["expenses_data"] = res.json()
                elif handle_expired_session(res):
                    st.session_state["expenses_data"] = None
                else:
                    st.error("Σφάλμα κατά την ανάκτηση δεδομένων.")
                    st.session_state["expenses_data"] = None
            except requests.exceptions.ConnectionError:
                st.error("Δεν βρέθηκε σύνδεση με το API.")
                st.session_state["expenses_data"] = None

    # -- Εμφάνιση αποτελεσμάτων -------------------------------------------
    data = st.session_state.get("expenses_data")

    if data:
        df = pd.DataFrame(data)

        if "amount" in df.columns:
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

        if "amount" in df.columns:
            m1, m2, m3 = st.columns(3)
            m1.metric("Σύνολο Εξόδων", f"{df['amount'].sum():.2f} €")
            m2.metric("Μέσος Όρος", f"{df['amount'].mean():.2f} €")
            m3.metric("Πλήθος Εγγραφών", len(df))

        df_display = df.copy()
        if "payment_method" in df_display.columns:
            payment_display_map = {
                "card": "Κάρτα",
                "cash": "Μετρητά",
                "bank_transfer": "Τραπεζικό Έμβασμα",
            }
            df_display["payment_method"] = (
                df_display["payment_method"]
                .map(payment_display_map)
                .fillna(df_display["payment_method"])
            )
        if "category" in df_display.columns:
            category_display_map = {
                "supermarket": "Σούπερ Μάρκετ",
                "rent": "Ενοίκιο",
                "utilities": "Λογαριασμοί",
                "entertainment": "Ψυχαγωγία",
                "transportation": "Μετακίνηση",
                "other": "Άλλο",
            }
            df_display["category"] = (
                df_display["category"]
                .map(category_display_map)
                .fillna(df_display["category"])
            )

        st.dataframe(df_display, use_container_width=True, hide_index=True)

        if "category" in df.columns and "amount" in df.columns:
            st.subheader("📊 Έξοδα ανά Κατηγορία")
            chart_data = df.groupby("category")["amount"].sum()
            st.bar_chart(chart_data)
    elif data == []:
        st.info("Δεν βρέθηκαν εγγραφές.")
    else:
        st.caption("Πατήστε «Φόρτωση Δεδομένων» για να δείτε τα έξοδά σας.")
