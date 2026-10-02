import streamlit as st
import os
import re
from collections import Counter


# =========================================================
# KONFIGURASI HALAMAN
# =========================================================

st.set_page_config(
    page_title="AI Tutor Bahasa Indonesia",
    page_icon="📚",
    layout="wide"
)


# =========================================================
# KONFIGURASI DATABASE
# =========================================================

FOLDER_DATABASE = "database"


# =========================================================
# FUNGSI MEMBACA DATABASE TXT
# =========================================================

def baca_database():

    data = []

    if not os.path.exists(FOLDER_DATABASE):
        os.makedirs(FOLDER_DATABASE)

    daftar_file = os.listdir(FOLDER_DATABASE)

    for nama_file in daftar_file:

        if nama_file.lower().endswith(".txt"):

            lokasi_file = os.path.join(
                FOLDER_DATABASE,
                nama_file
            )

            try:

                with open(
                    lokasi_file,
                    "r",
                    encoding="utf-8"
                ) as file:

                    isi = file.read()

                data.append({
                    "nama_file": nama_file,
                    "isi": isi
                })

            except Exception as error:

                st.error(
                    f"Gagal membaca {nama_file}: {error}"
                )

    return data


# =========================================================
# MEMBERSIHKAN TEKS
# =========================================================

def bersihkan_teks(teks):

    teks = teks.lower()

    teks = re.sub(
        r"[^a-zA-ZÀ-ÿ0-9\s]",
        " ",
        teks
    )

    teks = re.sub(
        r"\s+",
        " ",
        teks
    )

    return teks.strip()


# =========================================================
# STOPWORDS SEDERHANA
# =========================================================

STOPWORDS = {
    "yang",
    "dan",
    "di",
    "ke",
    "dari",
    "pada",
    "dengan",
    "untuk",
    "dalam",
    "adalah",
    "itu",
    "ini",
    "atau",
    "apa",
    "bagaimana",
    "mengapa",
    "sebutkan",
    "jelaskan",
    "jelaskanlah",
    "tentang",
    "suatu",
    "sebuah",
    "secara",
    "merupakan",
    "dapat",
    "akan",
    "sebagai",
    "oleh",
    "lebih",
    "juga",
    "tidak",
    "tersebut"
}


# =========================================================
# MENGAMBIL KATA KUNCI
# =========================================================

def ambil_kata_kunci(pertanyaan):

    teks = bersihkan_teks(pertanyaan)

    kata = teks.split()

    kata_kunci = []

    for item in kata:

        if len(item) > 2 and item not in STOPWORDS:

            kata_kunci.append(item)

    return kata_kunci


# =========================================================
# SISTEM PENILAIAN RELEVANSI
# =========================================================

def hitung_relevansi(pertanyaan, isi):

    kata_kunci = ambil_kata_kunci(pertanyaan)

    if len(kata_kunci) == 0:
        return 0

    teks_database = bersihkan_teks(isi)

    kata_database = teks_database.split()

    frekuensi = Counter(kata_database)

    skor = 0

    for kata in kata_kunci:

        if kata in frekuensi:

            jumlah = frekuensi[kata]

            if jumlah > 10:
                jumlah = 10

            skor += jumlah

    # Bonus jika frasa pertanyaan muncul
    pertanyaan_bersih = bersihkan_teks(
        pertanyaan
    )

    if pertanyaan_bersih in teks_database:

        skor += 20

    # Bonus jika kata kunci utama terdapat di judul
    baris_awal = teks_database[:500]

    for kata in kata_kunci:

        if kata in baris_awal:

            skor += 5

    return skor


# =========================================================
# MENCARI MATERI
# =========================================================

def cari_materi(pertanyaan, database):

    hasil = []

    for data in database:

        skor = hitung_relevansi(
            pertanyaan,
            data["isi"]
        )

        if skor > 0:

            hasil.append({
                "nama_file": data["nama_file"],
                "isi": data["isi"],
                "skor": skor
            })

    hasil.sort(
        key=lambda x: x["skor"],
        reverse=True
    )

    return hasil


# =========================================================
# MEMBUAT POTONGAN MATERI
# =========================================================

def ambil_potongan_relevan(
    pertanyaan,
    isi,
    jumlah_maksimal=1200
):

    kata_kunci = ambil_kata_kunci(
        pertanyaan
    )

    paragraf = re.split(
        r"\n\s*\n|\r\n",
        isi
    )

    paragraf_relevan = []

    for p in paragraf:

        p_bersih = bersihkan_teks(p)

        skor = 0

        for kata in kata_kunci:

            if kata in p_bersih:

                skor += 1

        if skor > 0:

            paragraf_relevan.append(
                (skor, p.strip())
            )

    paragraf_relevan.sort(
        key=lambda x: x[0],
        reverse=True
    )

    hasil = ""

    for skor, p in paragraf_relevan:

        if len(hasil) + len(p) <= jumlah_maksimal:

            hasil += p + "\n\n"

    if hasil.strip() == "":

        hasil = isi[:jumlah_maksimal]

    return hasil.strip()


# =========================================================
# KONFIGURASI LINK (ISI DENGAN LINK ASLI)
# =========================================================

LINK_ABSEN = "https://forms.gle/ISI_LINK_GOOGLE_FORM_ABSEN"
LINK_LKPD = "https://quizizz.com/join?gc=ISI_KODE_QUIZIZZ_1"
LINK_RUBRIK = "https://docs.google.com/spreadsheets/d/ISI_ID_SPREADSHEET/edit"
LINK_EVALUASI = "https://quizizz.com/join?gc=ISI_KODE_QUIZIZZ_2"


def tampilkan_link(label, url, ikon):
    """Menampilkan tombol link; memberi petunjuk jika link belum diisi."""

    if "ISI_" in url:
        st.info(
            "Link belum diisi. Ganti nilai link pada bagian "
            "KONFIGURASI LINK di file app.py."
        )

    st.link_button(
        f"{ikon} {label}",
        url,
        use_container_width=True
    )


def nama_materi(nama_file):

    return nama_file.replace(".txt", "").replace("_", " ").title()


# =========================================================
# LOAD DATABASE
# =========================================================

database = baca_database()


# =========================================================
# HEADER APLIKASI
# =========================================================

st.title("📚 AI Tutor Bahasa Indonesia")

st.write(
    "Sistem pembelajaran berbasis Python, "
    "Streamlit, dan Knowledge Base TXT."
)

st.divider()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("📖 Knowledge Base")

    st.write(
        "Database dibaca otomatis dari folder:"
    )

    st.code("database/")

    st.write(
        f"Jumlah file database: **{len(database)}**"
    )

    st.divider()

    if len(database) > 0:

        st.subheader("Materi tersedia")

        for data in database:

            nama = data["nama_file"]

            nama = nama.replace(
                ".txt",
                ""
            )

            nama = nama.replace(
                "_",
                " "
            )

            st.write(
                "📄 " + nama.title()
            )

    else:

        st.warning(
            "Belum ada file TXT di folder database."
        )



# =========================================================
# TAB MENU
# =========================================================

tab_tutor, tab_panduan, tab_absen, tab_materi, tab_lkpd, tab_rubrik, tab_evaluasi = st.tabs([
    "💬 Tutor AI",
    "📘 Panduan",
    "📝 Absen",
    "📚 Materi",
    "🧩 LKPD",
    "📊 Rubrik Penilaian",
    "✅ Evaluasi"
])


# =========================================================
# TAB 1: TUTOR AI (FITUR ASLI)
# =========================================================

with tab_tutor:

    # =========================================================
    # FORM PERTANYAAN
    # =========================================================

    st.subheader("💬 Tanyakan Sesuatu")

    pertanyaan = st.text_area(
        "Masukkan pertanyaan Anda:",
        placeholder=(
            "Contoh: Apa yang dimaksud "
            "dengan kalimat efektif?"
        ),
        height=120
    )


    # =========================================================
    # TOMBOL TANYAKAN
    # =========================================================

    tombol = st.button(
        "🔍 TANYAKAN",
        use_container_width=True
    )


    # =========================================================
    # PROSES PERTANYAAN
    # =========================================================

    if tombol:

        if pertanyaan.strip() == "":

            st.warning(
                "Silakan masukkan pertanyaan terlebih dahulu."
            )

        elif len(database) == 0:

            st.error(
                "Database TXT belum ditemukan."
            )

        else:

            with st.spinner(
                "Sedang mencari materi..."
            ):

                hasil = cari_materi(
                    pertanyaan,
                    database
                )


            # =================================================
            # JIKA MATERI DITEMUKAN
            # =================================================

            if len(hasil) > 0:

                hasil_utama = hasil[0]

                st.success(
                    "Materi yang paling relevan ditemukan."
                )

                st.subheader(
                    "💡 Jawaban"
                )

                jawaban = ambil_potongan_relevan(
                    pertanyaan,
                    hasil_utama["isi"]
                )

                st.info(jawaban)


                # =============================================
                # SUMBER MATERI
                # =============================================

                st.subheader(
                    "📚 Sumber Materi"
                )

                nama_file = hasil_utama[
                    "nama_file"
                ]

                st.write(
                    f"**{nama_file}**"
                )


                # =============================================
                # MATERI TERKAIT
                # =============================================

                if len(hasil) > 1:

                    st.subheader(
                        "📑 Materi Terkait"
                    )

                    for item in hasil[1:4]:

                        with st.expander(
                            item["nama_file"]
                        ):

                            potongan = (
                                ambil_potongan_relevan(
                                    pertanyaan,
                                    item["isi"],
                                    800
                                )
                            )

                            st.write(
                                potongan
                            )


            # =================================================
            # JIKA TIDAK DITEMUKAN
            # =================================================


            else:

                st.warning(
                    "Maaf, materi yang Anda tanyakan "
                    "belum ditemukan dalam database."
                )

                st.write(
                    "Coba gunakan kata kunci yang "
                    "lebih spesifik."
                )




# =========================================================
# TAB 2: PANDUAN PENGGUNAAN AI PEMBELAJARAN
# =========================================================

with tab_panduan:

    st.subheader("📘 Panduan Penggunaan AI Pembelajaran")

    st.markdown(
        """
**Langkah-langkah belajar dengan AI Tutor Bahasa Indonesia:**

1. **Isi absen** pada tab **Absen** (Google Form) sebelum memulai pembelajaran.
2. **Pelajari materi** pada tab **Materi**, lalu pilih topik yang ingin dipelajari.
3. **Tanyakan hal yang belum dipahami** pada tab **Tutor AI**. Gunakan kata kunci yang jelas,
   misalnya: *"Apa yang dimaksud dengan kalimat efektif?"*
4. **Kerjakan LKPD** pada tab **LKPD** (Quizizz 1) untuk melatih pemahaman.
5. **Lihat Rubrik Penilaian** pada tab **Rubrik Penilaian** agar tahu aspek yang dinilai.
6. **Kerjakan Evaluasi** pada tab **Evaluasi** (Quizizz 2) sebagai penilaian akhir.
        """
    )

    st.markdown("**Tips bertanya kepada AI Tutor:**")

    st.markdown(
        """
- Gunakan kalimat pertanyaan yang spesifik.
- Gunakan istilah yang ada di materi (misalnya *morfologi*, *teks prosedur*, *ejaan*).
- Jika jawaban belum sesuai, coba ubah kata kunci pertanyaan.
        """
    )


# =========================================================
# TAB 3: ABSEN (LINK GOOGLE FORM)
# =========================================================

with tab_absen:

    st.subheader("📝 Absen")

    st.write(
        "Silakan isi daftar hadir melalui Google Form berikut."
    )

    tampilkan_link(
        "Isi Absen (Google Form)",
        LINK_ABSEN,
        "📝"
    )


# =========================================================
# TAB 4: MATERI
# =========================================================

with tab_materi:

    st.subheader("📚 Materi")

    if len(database) == 0:

        st.warning(
            "Belum ada file TXT di folder database."
        )

    else:

        daftar_nama = sorted(
            [d["nama_file"] for d in database],
            key=nama_materi
        )

        pilihan = st.selectbox(
            "Pilih materi:",
            daftar_nama,
            format_func=nama_materi
        )

        isi_materi = next(
            d["isi"] for d in database
            if d["nama_file"] == pilihan
        )

        st.markdown("### " + nama_materi(pilihan))

        with st.container(height=500, border=True):

            st.text(isi_materi)

        st.download_button(
            "⬇️ Unduh Materi (TXT)",
            data=isi_materi,
            file_name=pilihan,
            mime="text/plain"
        )


# =========================================================
# TAB 5: LKPD (LINK QUIZIZZ 1)
# =========================================================

with tab_lkpd:

    st.subheader("🧩 LKPD")

    st.write(
        "Kerjakan Lembar Kerja Peserta Didik (LKPD) "
        "melalui Quizizz berikut."
    )

    tampilkan_link(
        "Kerjakan LKPD (Quizizz 1)",
        LINK_LKPD,
        "🧩"
    )


# =========================================================
# TAB 6: RUBRIK PENILAIAN (SPREADSHEET)
# =========================================================

with tab_rubrik:

    st.subheader("📊 Rubrik Penilaian")

    st.write(
        "Rubrik penilaian dapat dilihat pada spreadsheet berikut."
    )

    tampilkan_link(
        "Buka Rubrik Penilaian (Spreadsheet)",
        LINK_RUBRIK,
        "📊"
    )


# =========================================================
# TAB 7: EVALUASI (LINK QUIZIZZ 2)
# =========================================================

with tab_evaluasi:

    st.subheader("✅ Evaluasi")

    st.write(
        "Kerjakan evaluasi akhir pembelajaran "
        "melalui Quizizz berikut."
    )

    tampilkan_link(
        "Kerjakan Evaluasi (Quizizz 2)",
        LINK_EVALUASI,
        "✅"
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "AI Tutor Bahasa Indonesia | "
    "Python + Streamlit + TXT Knowledge Base"
)