import sys
import threading
import tkinter.messagebox as messagebox
from pathlib import Path
import customtkinter as ctk

# Подключаем наши модули
sys.path.append(str(Path(__file__).parent / "src"))
from utils import slugify, load_json, save_json
from pdf_parser import extract_pdf_to_markdown
from indexer import index_source
from config import DATA_DIR, BASE_DIR

class AdminApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("RAG Admin Panel")
        self.geometry("600x700")
        
        # Пути к папкам
        self.roles_dir = BASE_DIR / "roles"
        self.sources_dir = BASE_DIR / "sources"
        self.profiles_dir = BASE_DIR / "profiles"
        self.data_dir = DATA_DIR
        
        # Список ролей для выпадающего меню
        self.available_roles = ["adult", "child"] 
        
        self.init_ui()

    def init_ui(self):
        # Заголовок
        header = ctk.CTkLabel(self, text="Загрузка новой библиотеки", font=("Arial", 24, "bold"))
        header.pack(pady=20)

        form_frame = ctk.CTkFrame(self, corner_radius=10)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 1. Название библиотеки
        lbl_name = ctk.CTkLabel(form_frame, text="Название библиотеки:", anchor="w")
        lbl_name.pack(fill="x", padx=20, pady=(20, 5))
        self.entry_name = ctk.CTkEntry(form_frame, placeholder_text="Например: Космос или Кулинария")
        self.entry_name.pack(fill="x", padx=20)

        # 2. Выбор роли
        lbl_role = ctk.CTkLabel(form_frame, text="Роль ответа:", anchor="w")
        lbl_role.pack(fill="x", padx=20, pady=(15, 5))
        self.option_menu_role = ctk.CTkOptionMenu(form_frame, values=self.available_roles)
        self.option_menu_role.set("child") # default
        self.option_menu_role.pack(fill="x", padx=20)

        # 3. Команда вызова
        lbl_cmd = ctk.CTkLabel(form_frame, text="Команда активации (для бота):", anchor="w")
        lbl_cmd.pack(fill="x", padx=20, pady=(15, 5))
        self.entry_command = ctk.CTkEntry(form_frame, placeholder_text='Например: "Вперед, динозавры!"')
        self.entry_command.pack(fill="x", padx=20)

        # 4. Загрузка файла
        lbl_file = ctk.CTkLabel(form_frame, text="Файл базы знаний (.pdf):", anchor="w")
        lbl_file.pack(fill="x", padx=20, pady=(15, 5))
        
        file_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        file_frame.pack(fill="x", padx=20)
        
        self.lbl_filename = ctk.CTkLabel(file_frame, text="Файл не выбран", anchor="w", text_color="gray")
        self.lbl_filename.pack(side="left", fill="x", expand=True)
        
        btn_browse = ctk.CTkButton(file_frame, text="Выбрать PDF", width=120, command=self.browse_file)
        btn_browse.pack(side="right")
        
        self.selected_pdf_path = None

        # Кнопка загрузки
        spacer = ctk.CTkFrame(form_frame, height=20, fg_color="transparent")
        spacer.pack()
        
        self.btn_upload = ctk.CTkButton(
            form_frame, 
            text="🚀 Загрузить и Индексировать", 
            font=("Arial", 16, "bold"),
            height=50,
            fg_color="#2cc96f",
            hover_color="#1e8c4b",
            command=self.start_processing_thread
        )
        self.btn_upload.pack(fill="x", padx=20, pady=20)

        # Лог процесса
        self.log_area = ctk.CTkTextbox(self, height=150, wrap="word")
        self.log_area.pack(fill="x", side="bottom", padx=20, pady=(0, 20))
        self.log("Готов к работе.")

    def log(self, message):
        self.log_area.insert("end", f"{message}\n")
        self.log_area.see("end")
        self.update_idletasks()

    def browse_file(self):
        from tkinter.filedialog import askopenfilename
        filename = askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if filename:
            self.selected_pdf_path = Path(filename)
            self.lbl_filename.configure(text=self.selected_pdf_path.name, text_color="white")

    def start_processing_thread(self):
        """Запускаем тяжелую работу в отдельном потоке, чтобы UI не вис"""
        if not self.validate_inputs():
            return
            
        self.btn_upload.configure(state="disabled", text="Обработка...")
        thread = threading.Thread(target=self.process_library)
        thread.daemon = True
        thread.start()

    def validate_inputs(self) -> bool:
        name = self.entry_name.get().strip()
        cmd = self.entry_command.get().strip()
        
        if not name:
            messagebox.showerror("Ошибка", "Введите название библиотеки")
            return False
        if not cmd:
            messagebox.showerror("Ошибка", "Введите команду вызова")
            return False
        if not self.selected_pdf_path:
            messagebox.showerror("Ошибка", "Выберите PDF файл")
            return False
            
        return True

    def process_library(self):
        try:
            raw_name = self.entry_name.get().strip()
            role_key = self.option_menu_role.get()
            command_phrase = self.entry_command.get().strip()
            
            # 1. Генерируем ID (slug)
            lib_slug = slugify(raw_name)
            collection_name = f"col_{lib_slug}"
            source_file_name = f"{lib_slug}.md"
            
            self.log(f"-> Slug создан: {lib_slug}")
            
            # 2. Конвертация PDF -> MD
            target_md_path = self.data_dir / source_file_name
            self.log(f"-> Извлекаем текст из PDF...")
            extract_pdf_to_markdown(self.selected_pdf_path, target_md_path)
            
            # 3. Создание Source Config
            source_config = {
                "id": lib_slug,
                "name": raw_name,
                "source_file": source_file_name,
                "collection": collection_name,
                "command_trigger": command_phrase
            }
            source_path = self.sources_dir / f"{lib_slug}.json"
            save_json(source_config, source_path)
            self.log(f"-> Сохранен конфиг источника: {source_path.name}")
            
            # 4. Создание Profile Config (связка Роль + Источник)
            profile_data = {
                "profile_id": lib_slug,
                "display_name": raw_name,
                "role_ref": role_key,      # ссылка на adult.json или child.json
                "source_ref": lib_slug     # ссылка на источник
            }
            profile_path = self.profiles_dir / f"{lib_slug}.json"
            save_json(profile_data, profile_path)
            self.log(f"-> Создан профиль: {profile_path.name}")
            
            # 5. ИНДЕКСАЦИЯ (Вызов существующего кода)
            self.log(f"-> Запуск векторизации (это может занять время)...")
            # index_source ожидает словарь source
            index_source(source_config) 
            
            self.log(f"✅ Библиотека '{raw_name}' успешно готова!")
            messagebox.showinfo("Успех", f"Библиотека '{raw_name}' загружена и проиндексирована.")
            
        except Exception as e:
            self.log(f"❌ ОШИБКА: {str(e)}")
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}")
        finally:
            self.after(0, lambda: self.btn_upload.configure(state="normal", text="🚀 Загрузить и Индексировать"))

if __name__ == "__main__":
    app = AdminApp()
    app.mainloop()