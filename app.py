import streamlit as st
import json
import os
import bcrypt
import pandas as pd
from datetime import datetime
import re
from PIL import Image
import base64
from io import BytesIO
from streamlit_option_menu import option_menu
import requests
import json
# from dotenv import load_dotenv
from dotenv.main import load_dotenv



load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GIST_ID = os.getenv("GIST_ID")  
RENTALS_FILENAME = "rentals.json"
USERS_FILENAME = "users.json"


HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def load_json_from_gist(filename):
    url = f"https://api.github.com/gists/{GIST_ID}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        gist_data = response.json()
        if filename in gist_data['files']:
            file_content = gist_data['files'][filename]['content']
            return json.loads(file_content)
        else:
            return {}
    else:
        return {}

def save_json_to_gist(data, filename):
    url = f"https://api.github.com/gists/{GIST_ID}"
    gist_patch = {
        "files": {
            filename: {
                "content": json.dumps(data, indent=4)
            }
        }
    }
    response = requests.patch(url, headers=HEADERS, data=json.dumps(gist_patch))
    return response.status_code == 200




st.set_page_config(layout="wide")

logo = Image.open("logo the jarrdin.png")
buffered = BytesIO()
logo.save(buffered, format="PNG")
img_base64 = base64.b64encode(buffered.getvalue()).decode()

# Tampilkan logo dan Judul
st.markdown(f"""
<div style='display: flex; align-items: center; gap: 16px;'>
    <img src='data:image/png;base64,{img_base64}' width='80' height='80' style='border-radius: 50%; object-fit: cover; border: 2px solid #004d40;'/>
    <h1 style='margin: 0; color: #008000; -webkit-text-stroke: 0.5px white; text-stroke: 0.5px white; font-weight: bold;'>
        Rusunami The Jarrdin Cihampelas
    </h1>
</div>
""", unsafe_allow_html=True)

# Garis putih sebagai pemisah antara judul dan subjudul
st.markdown("""
<hr style="border: 1px solid white; margin-top: 8px; margin-bottom: 16px;">
""", unsafe_allow_html=True)

# CSS 
st.markdown("""
<style>
[data-testid="stDownloadButton"] > button {
    background-color: #004d40 !important;
    color: white !important;
    border: 2px solid #004d40;
    border-radius: 8px;
    transition: all 0.3s ease;
}

[data-testid="stDownloadButton"] > button:hover {
    border-color: #ff6f00 !important;
    color: white !important;
    background-color: #004d40 !important;
}            

h1.the-jarrdin {
    color: #003f2f;
    -webkit-text-stroke: 0.8px white;
    text-stroke: 0.8px white;
    font-weight: bold;
}

div.stButton > button {
    background-color: #004d40 !important;
    color: white !important;
    border: 2px solid #004d40;
    border-radius: 8px;
    transition: all 0.3s ease;
}

div.stButton > button:hover {
    border-color: #ff6f00 !important;
    color: white !important;
    background-color: #004d40 !important;
}
</style>
""", unsafe_allow_html=True)







USER_FILE = "users.json"
RENTAL_FILE = "rentals.json"

pelanggaran_list = [
    "Ditemukan alat suntik di tempat sampah",
    "Ditemukan kondom dalam jumlah banyak",
    "Kerusakan parah pada fasilitas",
    "Kebisingan berlebihan di malam hari",
    "Penyalahgunaan alkohol/narkoba",
    "Kekerasan atau ancaman kepada penghuni lain",
    "Merokok di area terlarang"
]

def load_json(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r") as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def is_valid_email(email):
    pattern = r"[^@]+@[^@]+\.[^@]+"
    return re.match(pattern, email)

users = load_json_from_gist(USERS_FILENAME)
rentals = load_json_from_gist(RENTALS_FILENAME)


if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "login"

if st.session_state.user is None:
    if st.session_state.page == "login":
        st.subheader("🔐 Login Agen")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if email in users and check_password(password, users[email]):
                st.session_state.user = email
                st.session_state.page = "main"
                st.session_state.login_time = datetime.now()  # Simpan waktu login
                st.rerun()
            else:
                st.error("Email atau password salah")

        st.markdown("Belum punya akun?")
        if st.button("👉 Daftar di sini", key="signup_link"):
            st.session_state.page = "signup"
            st.rerun()

    elif st.session_state.page == "signup":
        st.subheader("📝 Daftar Agen Baru")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        valid_email = is_valid_email(email)
        valid_password = len(password) >= 8

        if email and not valid_email:
            st.error("Email tidak valid")
        if password and not valid_password:
            st.error("Password harus minimal 8 karakter")

        if st.button("Daftar"):
            if not email:
                st.error("Email harus diisi")
            elif not valid_email:
                st.error("Email tidak valid")
            elif not password:
                st.error("Password harus diisi")
            elif not valid_password:
                st.error("Password harus minimal 8 karakter")
            elif email in users:
                st.error("Email sudah terdaftar")
            else:
                users[email] = hash_password(password)
                success_users = save_json_to_gist(users, USERS_FILENAME)
                if success_users:
                    st.success("Registrasi berhasil! Silakan login")
                else:
                    st.error("Gagal menyimpan data ke Gist!")
                st.session_state.page = "login"
                st.rerun()

        st.markdown("Sudah punya akun?")
        if st.button("🔑 Login di sini", key="login_link"):
            st.session_state.page = "login"
            st.rerun()

else:
    
    with st.sidebar:
        st.markdown(f"**👤 {st.session_state.get('user', 'Guest')}**")
        menu = option_menu(
            menu_title="Menu", 
            options=["Input Data Penyewa", "Lihat/Edit Data Penyewa"],
            icons=["clipboard-plus", "table"],
            menu_icon="cast", 
            default_index=0,
            styles={
                "container": {"padding": "5px", "background-color": "#030200"},
                "icon": {"color": "#99FAA9", "font-size": "17px"},
                "nav-link": {
                    "font-size": "15px",
                    "text-align": "left",
                    "margin": "5px",
                },
                "nav-link-selected": {
                    "background-color": "#049521",
                    "color": "white"
                },
            }
        )

        


        st.markdown("---")
        if st.button("Logout"):
            st.session_state.user = None
            st.session_state.page = "login"
            st.rerun()
            


    if menu == "Input Data Penyewa":
        # Cek waktu login dan waktu sekarang
        if "login_time" in st.session_state:
            elapsed = (datetime.now() - st.session_state.login_time).total_seconds()
        else:
            elapsed = 9999  # default agar tidak muncul

        if elapsed < 10:
            st.success(f"Selamat datang, {st.session_state.user}")
        else:
            # Jika sudah lewat 10 detik, hapus login_time agar pesan hilang
            if "login_time" in st.session_state:
                del st.session_state.login_time


        nama = st.text_input("Nama Penyewa")
        tower = st.selectbox("Tower", ["A", "B", "C", "D"])
        lantai = st.text_input("Lantai")
        unit = st.text_input("Nomor Unit")
        status_kewarganegaraan = st.selectbox("Status Kewarganegaraan", ["WNI", "WNA"])

        metode = st.selectbox("Metode Pembayaran", ["Cash", "Kartu Kredit", "Kartu Debit", "QRIS", "Others"])
        metode_lain = ""
        if metode == "Others":
            metode_lain = st.text_input("Metode Pembayaran Lainnya")

        tanggal_checkin = st.date_input("Tanggal Check-In", value=datetime.now().date())
        waktu_checkin_str = st.text_input("Waktu Check-In (format: HH:MM)", value=datetime.now().strftime("%H:%M"))
        tanggal_checkout = st.date_input("Tanggal Check-Out")

        if tanggal_checkin > tanggal_checkout:
            st.error("Tanggal check-in/tanggal check-out tidak valid.")

        lama = (tanggal_checkout - tanggal_checkin).days
        st.markdown(f"**Lama Menginap: {lama} hari**")

        if st.button("Simpan Data Penyewa"):
            try:
                waktu_checkin = datetime.strptime(waktu_checkin_str, "%H:%M").time()
                checkin_datetime = datetime.combine(tanggal_checkin, waktu_checkin)
                metode_final = metode_lain if metode == "Others" else metode

                data = {
                    "nama": nama,
                    "agen": st.session_state.user,
                    "tower": tower,
                    "lantai": lantai,
                    "unit": unit,
                    "status_kewarganegaraan": status_kewarganegaraan,
                    "metode_pembayaran": metode_final,
                    "checkin": checkin_datetime.isoformat(),
                    "tanggal_checkout": str(tanggal_checkout),
                    "waktu_checkout": None,
                    "lama_menginap": lama,
                    "komentar": []
                }

                if "data" not in rentals:
                    rentals["data"] = []
                rentals["data"].append(data)
                success_rentals = save_json_to_gist(rentals, RENTALS_FILENAME)
                if success_rentals:
                    st.success("Data penyewa berhasil disimpan!")
                else:
                    st.error("Gagal menyimpan data ke Gist!")

            except ValueError:
                st.error("Format waktu check-in tidak valid. Gunakan format HH:MM.")

    elif menu == "Lihat/Edit Data Penyewa":
        if "refresh_table" in st.session_state:
            del st.session_state.refresh_table

        st.subheader("Data Penyewa")
        data_list = rentals.get("data", [])

        if not data_list:
            st.info("Belum ada data.")
        else:
            df = pd.DataFrame(data_list)
            df["tanggal_checkin"] = pd.to_datetime(df["checkin"]).dt.date
            df["waktu_checkin"] = pd.to_datetime(df["checkin"]).dt.time
            df["komentar_str"] = df["komentar"].apply(lambda x: ", ".join(x) if isinstance(x, list) else "")
            df["diedit_oleh"] = df.get("diedit_oleh", "")

            show_cols = [
                "nama", "status_kewarganegaraan", "tower", "lantai", "unit",
                "metode_pembayaran", "tanggal_checkin", "waktu_checkin",
                "tanggal_checkout", "waktu_checkout", "lama_menginap",
                "komentar_str", "agen", "diedit_oleh"
            ]

            col_rename = {
                "nama": "Nama Penyewa",
                "status_kewarganegaraan": "Status Kewarganegaraan",
                "tower": "Tower",
                "lantai": "Lantai",
                "unit": "Unit",
                "metode_pembayaran": "Metode Pembayaran",
                "tanggal_checkin": "Tanggal Check-in",
                "waktu_checkin": "Waktu Check-in",
                "tanggal_checkout": "Tanggal Check-out",
                "waktu_checkout": "Waktu Check-out",
                "lama_menginap": "Lama Menginap (hari)",
                "komentar_str": "Komentar",
                "agen": "Agen",
                "diedit_oleh": "Diedit Oleh"
            }

            df_display = df[show_cols].rename(columns=col_rename)

            csv = df_display.to_csv(index=False).encode("utf-8")
            col1, col2 = st.columns([3.6, 1])
            with col1:
                st.download_button("📥 Download CSV", data=csv, file_name="data_penyewa.csv", mime="text/csv")
            with col2:
                if st.button("🔄 Refresh Tabel"):
                    st.session_state.refresh_table = True
                    st.rerun()

            st.dataframe(df_display)

            st.markdown("---")
            st.write("**Input Waktu Check-out dan Komentar**")
            for i, d in enumerate(data_list):
                with st.expander(f"Penyewa ke-{i+1}: {d['nama']} (diinput oleh {d['agen']})"):
                    waktu_checkout = st.text_input(
                        "Isi Waktu Check-out (format HH:MM)",
                        value=d.get("waktu_checkout") or "",
                        key=f"wkt_txt_{i}"
                    )
                    if st.button("Simpan Waktu Check-out", key=f"btn_co_{i}"):
                        try:
                            if waktu_checkout:
                                datetime.strptime(waktu_checkout, "%H:%M")
                            d["waktu_checkout"] = waktu_checkout
                            d["diedit_oleh"] = st.session_state.user
                            # Save to Gist instead of local file
                            success_rentals = save_json_to_gist(rentals, RENTALS_FILENAME)
                            if success_rentals:
                                st.success("Waktu check-out disimpan")
                            else:
                                st.error("Gagal menyimpan data ke Gist!")
                        except ValueError:
                            st.error("Format waktu check-out tidak valid. Gunakan format HH:MM.")

                    st.markdown("**Komentar**")
                    selected_komentar = []
                    for k in pelanggaran_list:
                        if st.checkbox(k, value=k in d.get("komentar", []), key=f"kom_{i}_{k}"):
                            selected_komentar.append(k)
                    if st.button("Simpan Komentar", key=f"kom_save_{i}"):
                        d["komentar"] = selected_komentar
                        d["diedit_oleh"] = st.session_state.user
                        # Save to Gist instead of local file
                        success_rentals = save_json_to_gist(rentals, RENTALS_FILENAME)
                        if success_rentals:
                            st.success("Komentar diperbarui")
                        else:
                            st.error("Gagal menyimpan data ke Gist!")