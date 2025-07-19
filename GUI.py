import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog

# =================================================================================
# Skema Warna & Font (Sesuai Desain)
# =================================================================================
APP_BG_COLOR = "#242134"
SIDEBAR_BG_COLOR = "#35314C"
FRAME_BG_COLOR = "#35314C"
WIDGET_BG_COLOR = "#4C4669"
WIDGET_HOVER_COLOR = "#625A86"
ACCENT_COLOR = "#A94364"
TEXT_COLOR = "#FFFFFF"

# =================================================================================
# Kelas Utama Aplikasi
# =================================================================================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Konfigurasi Window Utama
        self.title("PBL RKS-611")
        self.geometry("900x650")
        self.configure(fg_color=APP_BG_COLOR)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ==================================
        # Header Frame (PBL RKS-611)
        # ==================================
        self.header_frame = ctk.CTkFrame(self, fg_color=ACCENT_COLOR, corner_radius=0, height=60)
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        self.header_label = ctk.CTkLabel(self.header_frame, text="PBL RKS-611", text_color=TEXT_COLOR, font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.place(relx=0.5, rely=0.5, anchor="center")

        # ==================================
        # Sidebar Frame
        # ==================================
        self.sidebar_frame = ctk.CTkFrame(self, width=220, fg_color=SIDEBAR_BG_COLOR, corner_radius=15)
        self.sidebar_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1) # Spacer row at the bottom

        self.sidebar_label = ctk.CTkLabel(self.sidebar_frame, text="List Attack", text_color=TEXT_COLOR, font=ctk.CTkFont(size=18, weight="bold"))
        self.sidebar_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Tombol-tombol di Sidebar
        button_texts = ["WPA/WPA2 crack", "Capture packet", "Deauther", "Pico-ducky"]
        for i, text in enumerate(button_texts, start=1):
            button = ctk.CTkButton(
                self.sidebar_frame, text=text, fg_color=WIDGET_BG_COLOR,
                hover_color=WIDGET_HOVER_COLOR, text_color=TEXT_COLOR, corner_radius=8
            )
            button.grid(row=i, column=0, padx=20, pady=7, sticky="ew")

        # Info di Sidebar (posisi dinaikkan)
        self.current_info_label = ctk.CTkLabel(self.sidebar_frame, text="Current info", text_color=TEXT_COLOR, font=ctk.CTkFont(size=18, weight="bold"))
        self.current_info_label.grid(row=5, column=0, padx=20, pady=(30, 10))

        self.network_info_label = ctk.CTkLabel(self.sidebar_frame, text="Network :", text_color=TEXT_COLOR, anchor="w")
        self.network_info_label.grid(row=6, column=0, padx=20, pady=(0, 5), sticky="w")
        self.ssid_info_label = ctk.CTkLabel(self.sidebar_frame, text="current SSID", text_color=TEXT_COLOR, anchor="w", font=ctk.CTkFont(weight="bold"))
        self.ssid_info_label.grid(row=7, column=0, padx=20, pady=(0, 5), sticky="w")

        self.ip_info_label = ctk.CTkLabel(self.sidebar_frame, text="IP :", text_color=TEXT_COLOR, anchor="w")
        self.ip_info_label.grid(row=8, column=0, padx=20, pady=(10, 5), sticky="w")
        self.ip_value_label = ctk.CTkLabel(self.sidebar_frame, text="Current IP", text_color=TEXT_COLOR, anchor="w", font=ctk.CTkFont(weight="bold"))
        self.ip_value_label.grid(row=9, column=0, padx=20, pady=(0, 5), sticky="w")

        # ==================================
        # Main Content Frame
        # ==================================
        self.main_content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content_frame.grid(row=1, column=1, padx=(0, 20), pady=20, sticky="nsew")
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_rowconfigure(1, weight=1) # Allow network list to expand

        self.caught_network_label = ctk.CTkLabel(self.main_content_frame, text="CAUGHTED NETWORK", text_color=TEXT_COLOR, font=ctk.CTkFont(size=18, weight="bold"))
        self.caught_network_label.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="n")
        
        # Frame untuk daftar jaringan (dibuat scrollable)
        self.network_scrollable_frame = ctk.CTkScrollableFrame(self.main_content_frame, fg_color=FRAME_BG_COLOR, corner_radius=15)
        self.network_scrollable_frame.grid(row=1, column=0, sticky="nsew")
        self.network_scrollable_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        headers = ["ENC", "BSSID", "SSID", "Ch", ""]
        for i, header in enumerate(headers):
            header_label = ctk.CTkLabel(self.network_scrollable_frame, text=header, text_color=TEXT_COLOR, font=ctk.CTkFont(weight="bold"))
            header_label.grid(row=0, column=i, padx=10, pady=10, sticky="ew")

        # --- DATA DUMMY DIPERBANYAK ---
        self.network_data = [
            ("WPA2", "A1:B3:C5:DD:3E:01", "Jangkrik boss", "6"),
            ("WPA2", "B2:C4:D6:EE:4F:02", "Bude Underground", "10"),
            ("WPA2", "C3:D5:E7:FF:5A:03", "Pakde uppercut", "8"),
            ("WPA",  "D4:E6:F8:00:6B:04", "OOM jangan OM", "6"),
            ("WPA2", "E5:F7:09:11:7C:05", "acumalaka", "2"),
            ("WPA3", "F6:08:1A:22:8D:06", "Warkop Digital", "11"),
            ("WPA2", "07:19:2B:33:9E:07", "Free Wifi Tetangga", "1"),
            ("WPA2", "18:2A:3C:44:AF:08", "CyberJaya Hotspot", "9"),
            ("WEP",  "29:3B:4D:55:B0:09", "Jaringan Jadul", "3"),
            ("WPA2", "3A:4C:5E:66:C1:10", "Puskesmas Wifi", "5"),
            ("WPA2", "4B:5D:6F:77:D2:11", "Toko Sembako Barokah", "7"),
            ("WPA3", "5C:6E:70:88:E3:12", "Kantor Kelurahan", "1"),
            ("WPA2", "6D:7F:81:99:F4:13", "Rental PS 5", "11"),
            ("WPA",  "7E:80:92:AA:05:14", "IndoApril", "4"),
            ("WPA2", "8F:91:A3:BB:16:15", "AlfaMidi", "2"),
        ]
        
        self.selected_network_var = tk.StringVar()
        
        for i, (enc, bssid, ssid, ch) in enumerate(self.network_data, start=1):
            ctk.CTkLabel(self.network_scrollable_frame, text=enc, anchor="w").grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            ctk.CTkLabel(self.network_scrollable_frame, text=bssid, anchor="w").grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            ctk.CTkLabel(self.network_scrollable_frame, text=ssid, anchor="w").grid(row=i, column=2, padx=10, pady=5, sticky="ew")
            ctk.CTkLabel(self.network_scrollable_frame, text=ch, anchor="center").grid(row=i, column=3, padx=10, pady=5, sticky="ew")
            
            radio_button = ctk.CTkRadioButton(self.network_scrollable_frame, text="", variable=self.selected_network_var, value=bssid,
                                             fg_color=WIDGET_BG_COLOR, hover_color=WIDGET_HOVER_COLOR)
            radio_button.grid(row=i, column=4, padx=10, pady=5)
        # --- Akhir bagian dummy data ---

        # Frame untuk kontrol di bagian bawah (posisi dinaikkan)
        self.bottom_controls_frame = ctk.CTkFrame(self.main_content_frame, fg_color="transparent")
        self.bottom_controls_frame.grid(row=2, column=0, pady=(20, 0), sticky="ew")
        self.bottom_controls_frame.grid_columnconfigure((0,1), weight=1)

        # Kontrol Password List
        self.password_frame = ctk.CTkFrame(self.bottom_controls_frame, fg_color=FRAME_BG_COLOR, corner_radius=15)
        self.password_frame.grid(row=0, column=0, padx=(0,10), pady=15, sticky="ew")
        self.password_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.password_frame, text="Password List").grid(row=0, column=0, padx=20, pady=(10,0), sticky="w")
        entry_frame = ctk.CTkFrame(self.password_frame, fg_color=WIDGET_BG_COLOR, corner_radius=8)
        entry_frame.grid(row=1, column=0, padx=15, pady=(5,15), sticky="ew")
        entry_frame.grid_columnconfigure(0, weight=1)
        self.password_entry = ctk.CTkEntry(entry_frame, border_width=0, fg_color="transparent", placeholder_text="home/pbl/password.txt")
        self.password_entry.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self.browse_button = ctk.CTkButton(entry_frame, text="Browse", width=80, command=self.browse_file, fg_color=WIDGET_HOVER_COLOR, hover_color=ACCENT_COLOR, corner_radius=8)
        self.browse_button.grid(row=0, column=1, padx=5, pady=5)

        # Kontrol Start & Hasil Password
        self.start_frame = ctk.CTkFrame(self.bottom_controls_frame, fg_color=FRAME_BG_COLOR, corner_radius=15)
        self.start_frame.grid(row=0, column=1, padx=(10,0), pady=15, sticky="nsew")
        self.start_frame.grid_columnconfigure(0, weight=1)
        self.start_button = ctk.CTkButton(self.start_frame, text="Start", command=self.start_attack, fg_color=WIDGET_BG_COLOR, hover_color=ACCENT_COLOR, corner_radius=8)
        self.start_button.grid(row=0, column=0, padx=15, pady=(15,5), sticky="ew")
        cracked_frame = ctk.CTkFrame(self.start_frame, fg_color=WIDGET_BG_COLOR, corner_radius=8)
        cracked_frame.grid(row=1, column=0, padx=15, pady=(5,15), sticky="ew")
        self.cracked_password_value = ctk.CTkLabel(cracked_frame, text="Password cracked : ...")
        self.cracked_password_value.pack(padx=10, pady=10, anchor="w")

    def browse_file(self):
        # Implementasi fungsi browse file
        pass

    def start_attack(self):
        # Implementasi fungsi start attack
        pass

if __name__ == "__main__":
    app = App()
    app.mainloop()
