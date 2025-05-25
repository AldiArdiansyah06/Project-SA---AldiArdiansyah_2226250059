import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import threading

def load_data(csv_path, min_year, max_km, budget):
    df = pd.read_csv("used_cars.csv")
    
    df['price'] = df['price'].str.replace(r'[$,]', '', regex=True).astype(float)
    df['model_year'] = pd.to_numeric(df['model_year'], errors='coerce')
    df['milage'] = df['milage'].str.replace(r'[,. mi]', '', regex=True).astype(float)
    df = df.dropna(subset=['price', 'model_year', 'milage', 'brand', 'model', 'fuel_type', 'accident', 'clean_title'])
    
    duplicate_count = df.duplicated().sum()
    print(f"Jumlah data duplikat: {duplicate_count}")
    print('Missing Values per Column:\n', df.isnull().sum())
    print("Dataset Shape:", df.shape, flush=True)
    print("\nValue Counts for 'brand':\n", df['brand'].value_counts())
    print("\nValue Counts for 'model_year':\n", df['model_year'].value_counts())
    df_filtered = df[
        (df['model_year'] >= min_year) &
        (df['milage'] <= max_km) &
        (df['price'] <= budget)
    ].copy()

    if df_filtered.empty:
        return df_filtered

    df_filtered['norm_price'] = 1 - (df_filtered['price'] - df_filtered['price'].min()) / (df_filtered['price'].max() - df_filtered['price'].min())
    df_filtered['norm_year'] = (df_filtered['model_year'] - df_filtered['model_year'].min()) / (df_filtered['model_year'].max() - df_filtered['model_year'].min())
    df_filtered['norm_milage'] = 1 - (df_filtered['milage'] - df_filtered['milage'].min()) / (df_filtered['milage'].max() - df_filtered['milage'].min())
    df_filtered['score'] = 0.5 * df_filtered['norm_price'] + 0.3 * df_filtered['norm_year'] + 0.2 * df_filtered['norm_milage']

    return df_filtered

def cari_mobil_terbaik(df, budget, top_n=20):
    df_budget = df[df['price'] <= budget].copy()
    df_budget.sort_values(by='score', ascending=False, inplace=True)
    return df_budget.head(top_n)

def buat_gui():
    def on_submit():
        def run():
            try:
                if not budget_entry.get() or not min_year_entry.get() or not max_km_entry.get():
                    raise ValueError("Semua input harus diisi!")

                budget = int(budget_entry.get())
                min_year = int(min_year_entry.get())
                max_km = int(max_km_entry.get())

                for item in tree.get_children():
                    tree.delete(item)

                df = load_data(
                    r"C:\Semester 6\SA\Project Akhir SA\used_cars.csv",
                    min_year=min_year,
                    max_km=max_km,
                    budget=budget
                )

                if df.empty:
                    messagebox.showinfo("Info", "Tidak ada mobil yang cocok dengan kriteria.")
                    summary_label.config(text="Tidak ada data yang cocok.")
                    return

                selected = cari_mobil_terbaik(df, budget)

                if selected.empty:
                    messagebox.showinfo("Info", "Tidak ada mobil dalam budget.")
                    summary_label.config(text="Tidak ada data yang cocok.")
                    return

                total_price = selected['price'].sum()
                avg_score = round(selected['score'].mean() * 100, 2)

                for idx, (_, row) in enumerate(selected.iterrows(), 1):
                    tree.insert("", "end", values=(
                        idx,
                        row['brand'],
                        row['model'],
                        f"$ {int(row['price']):,}".replace(",", "."),
                        int(row['model_year']),
                        f"{int(row['milage']):,}".replace(",", "."),
                        row.get('fuel_type', '-'),
                        row.get('transmission', '-'),
                        row.get('accident', '-'),
                        row.get('engine', '-'),
                        f"{round(row['score'] * 100, 2)}%"
                    ))

                summary_label.config(
                    text=f"Total Harga: $ {int(total_price):,}".replace(",", ".") +
                         f" | Rata-rata Skor: {avg_score}%"
                )

            except Exception as e:
                messagebox.showerror("Error", str(e))

        threading.Thread(target=run).start()

    # 🎨 Warna tema mewah
    warna_bg = "#1B1F3B"       # dark navy
    warna_teks = "#F5F5F5"     # ivory
    warna_header = "#D4AF37"   # gold
    warna_tabel_bg = "#2C2F48" # slate gray
    warna_hover = "#B8860B"    # goldenrod for hover

    root = tk.Tk()
    root.title("Optimasi Mobil Bekas")
    root.geometry("1200x600")
    root.configure(bg=warna_bg)

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TLabel", background=warna_bg, foreground=warna_teks, font=("Segoe UI", 11))
    style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), background=warna_bg, foreground=warna_header)
    style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=6, background=warna_header, foreground=warna_bg)
    style.map("TButton",
              background=[('active', warna_hover)],
              foreground=[('active', warna_teks)])

    style.configure("Treeview",
                    background="white",
                    foreground="black",
                    rowheight=25,
                    fieldbackground="white",
                    font=("Segoe UI", 10))
    style.configure("Treeview.Heading",
                    font=("Segoe UI", 11, "bold"),
                    background=warna_header,
                    foreground=warna_bg)
    style.map('Treeview', background=[('selected', warna_hover)], foreground=[('selected', 'white')])

    input_frame = tk.Frame(root, bg=warna_bg)
    input_frame.pack(pady=20, padx=20, fill='x')

    label_title = ttk.Label(root, text="Cari Mobil Bekas Optimal", style="Header.TLabel")
    label_title.pack(pady=(10, 0))

    ttk.Label(input_frame, text="Masukkan Budget ($):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    budget_entry = ttk.Entry(input_frame, width=20)
    budget_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    ttk.Label(input_frame, text="Tahun Minimal:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    min_year_entry = ttk.Entry(input_frame, width=20)
    min_year_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

    ttk.Label(input_frame, text="Odometer Maksimal (KM):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    max_km_entry = ttk.Entry(input_frame, width=20)
    max_km_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

    btn_search = ttk.Button(input_frame, text="Cari Mobil Optimal", command=on_submit)
    btn_search.grid(row=3, column=0, columnspan=2, pady=15)

    tree_frame = tk.Frame(root)
    tree_frame.pack(padx=20, pady=10, fill="both", expand=True)

    columns = ("No", "Brand", "Model", "Harga", "Tahun", "KM", "Fuel", "Transmisi", "accident", "Mesin", "Skor (%)")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        if col in ["Model", "Brand", "Body", "Mesin"]:
            tree.column(col, anchor="w", width=140)
        else:
            tree.column(col, anchor="center", width=100)

    tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    summary_label = ttk.Label(root, text="", style="TLabel")
    summary_label.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    df_test = load_data(r"C:\Semester 6\SA\Project Akhir SA\used_cars.csv", 2015, 50000, 30000)

    buat_gui()
