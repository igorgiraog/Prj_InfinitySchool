import tkinter as tk
from tkinter import ttk
from pytz import timezone
import mysql.connector
from mysql.connector import Error
from tkcalendar import DateEntry
from tkinter import messagebox
from datetime import datetime

def verificar_substring(substring, string):
    return substring in string

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lista de Tarefas")
        self.root.configure(bg="#000")
        self.root.geometry('1200x700')

        self.connect_to_db()

        # Criar widgets
        self.tree = ttk.Treeview(self.root, columns=("ID", "Status", "Descrição", "Data Inicial", "Hora Inicial", "Data Final", "Hora Final"))
        self.tree.heading("#0", text="", anchor="w")
        self.tree.heading("ID", text="ID", anchor="center")
        self.tree.heading("Status", text="Status", anchor="center")
        self.tree.heading("Descrição", text="Descrição", anchor="center")
        self.tree.heading("Data Inicial", text="Data Inicial", anchor="center")
        self.tree.heading("Hora Inicial", text="Hora Inicial", anchor="center")
        self.tree.heading("Data Final", text="Data Final", anchor="center")
        self.tree.heading("Hora Final", text="Hora Final", anchor="center")

        # Definir larguras das colunas
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Status", width=100, anchor="center")
        self.tree.column("Descrição", width=600, anchor="center")
        self.tree.column("Data Inicial", width=100, anchor="center")
        self.tree.column("Hora Inicial", width=100, anchor="center")
        self.tree.column("Data Final", width=100, anchor="center")
        self.tree.column("Hora Final", width=100, anchor="center")

        self.task_id = tk.StringVar()
        self.status = tk.StringVar(value='Pendente')
        self.description = tk.StringVar()
        self.start_date = tk.StringVar()
        self.start_time = tk.StringVar(value=datetime.now().strftime("%H:%M:%S"))
        self.end_date = tk.StringVar()
        self.end_time = tk.StringVar()

        # Criar um Frame para organizar os campos verticalmente
        input_frame = tk.Frame(self.root)

        tk.Label(input_frame, text="ID:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Label(input_frame, text="Status:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Label(input_frame, text="Descrição:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Label(input_frame, text="Data Inicial:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        tk.Label(input_frame, text="Hora Inicial:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        tk.Label(input_frame, text="Data Final:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        tk.Label(input_frame, text="Hora Final:").grid(row=6, column=0, sticky="e", padx=5, pady=5)

        self.id_entry = tk.Entry(input_frame, textvariable=self.task_id, state='readonly', width=100)
        self.status_combobox = ttk.Combobox(input_frame, textvariable=self.status,
                                            values=["Pendente", "Em Andamento", "Concluído"], width=97)
        self.description_entry = tk.Entry(input_frame, textvariable=self.description, width=100)
        self.start_date_entry = DateEntry(input_frame, textvariable=self.start_date, width=97, date_pattern='yyyy-mm-dd')
        self.start_time_entry = tk.Entry(input_frame, textvariable=self.start_time, width=100)
        self.end_date_entry = DateEntry(input_frame, textvariable=self.end_date, width=97, date_pattern='yyyy-mm-dd')
        self.end_time_entry = tk.Entry(input_frame, textvariable=self.end_time, width=100)

        self.add_button = tk.Button(self.root, text="Adicionar Tarefa", command=self.add_task, bg="blue", fg="white")
        self.edit_button = tk.Button(self.root, text="Editar Tarefa", command=self.edit_task, bg="yellow", fg="black")
        self.delete_button = tk.Button(self.root, text="Deletar Tarefa", command=self.delete_task, bg="red", fg="white")
        self.reload_button = tk.Button(self.root, text="Atualizar", command=self.reload_task, bg="green", fg="black")
        self.finaliza_button = tk.Button(self.root, text="Finalizar", command=self.finaliza_task, bg="Purple", fg="white")

        # Posicionar widgets
        self.tree.pack(pady=10)
        input_frame.pack(pady=10)
        self.id_entry.grid(row=0, column=1, padx=5, pady=5)
        self.status_combobox.grid(row=1, column=1, padx=5, pady=5)
        self.description_entry.grid(row=2, column=1, padx=5, pady=5)
        self.start_date_entry.grid(row=3, column=1, padx=5, pady=5)
        self.start_time_entry.grid(row=4, column=1, padx=5, pady=5)
        self.end_date_entry.grid(row=5, column=1, padx=5, pady=5)
        self.end_time_entry.grid(row=6, column=1, padx=5, pady=5)
        self.add_button.pack(pady=5)
        self.edit_button.pack(pady=5)
        self.delete_button.pack(pady=5)
        self.reload_button.pack(pady=5)
        self.finaliza_button.pack(pady=5)

        # Carregar tarefas do banco de dados
        self.load_tasks_from_db()

        # Adicione um evento de seleção para chamar a função show_selected_task
        self.tree.bind("<ButtonRelease-1>", self.show_selected_task)

    def connect_to_db(self):
        try:
            self.connection = mysql.connector.connect(
                host="stylomisscris.com.br",
                user="stylom29_infinityschool",
                password="N!@2-0*#4MNfJ6eJhT",
                database="stylom29_infinityschool"
            )

            if self.connection.is_connected():
                print("Conectado ao banco de dados")
        except Error as e:
            print("Erro ao conectar ao banco de dados:", e)

    def close_db_connection(self):
        if self.connection.is_connected():
            self.connection.close()
            print("Conexão com o banco de dados fechada")

    def load_tasks_from_db(self):
        try:
            xQry = "SELECT "
            xQry += "	ID, "
            xQry += "	STS, "
            xQry += "	DESCRICAO, "
            xQry += "	CASE WHEN DT_INI = '//' THEN '' ELSE DT_INI END AS DT_INI, "
            xQry += "	HR_INI, "
            xQry += "	CASE WHEN DT_FIM = '//' THEN '' ELSE DT_FIM END AS DT_FIM, "
            xQry += "	HR_FIM "
            xQry += "FROM( "
            xQry += "	SELECT "
            xQry += "		ID, "
            xQry += "		STS, "
            xQry += "		DESCRICAO, "
            xQry += "		CONCAT(SUBSTRING(DT_INI,7,2),'/',SUBSTRING(DT_INI,5,2),'/',SUBSTRING(DT_INI,1,4)) AS DT_INI, "
            xQry += "		HR_INI, "
            xQry += "		CONCAT(SUBSTRING(DT_FIM,7,2),'/',SUBSTRING(DT_FIM,5,2),'/',SUBSTRING(DT_FIM,1,4)) AS DT_FIM, "
            xQry += "		HR_FIM "
            xQry += "	FROM TAREFAS "
            xQry += ")A "
            xQry += "ORDER BY ID "

            cursor = self.connection.cursor()
            cursor.execute(xQry)
            tasks = cursor.fetchall()

            for task in tasks:
                self.tree.insert("", tk.END, values=task)

            cursor.close()
        except Error as e:
            print("Erro ao carregar tarefas do banco de dados:", e)

    def add_task(self):
        task_data = [
            self.status.get(),
            self.description.get(),
            self.start_date.get(),
            self.start_time.get(),
            self.end_date.get(),
            self.end_time.get()
        ]

        if task_data[0] != "" and task_data[1] != "" and task_data[2] != "" and task_data[3] != "":
            self.tree.insert("", tk.END, values=task_data)
            self.insert_task_into_db(task_data)
            self.clear_entries()
            self.update_task_list()
        else:
            tk.messagebox.showwarning("Aviso", "Preencha todos os campos!")

    def insert_task_into_db(self, task_data):
        try:
            cursor = self.connection.cursor()

            xSts = task_data[0]
            xDes = task_data[1]
            xDtI = datetime.strptime(task_data[2], "%Y-%m-%d").strftime("%Y%m%d")
            xHrI = task_data[3]

            xValid = verificar_substring("-", task_data[4])
            if xValid:
                xDtF = datetime.strptime(task_data[4], "%Y-%m-%d").strftime("%Y%m%d")
                xHrF = task_data[5]
                if (xDtI == xDtF and xHrF == "") or (xDtF == "" and xHrF == ""):
                    xDtF = ""
                    xHrF = ""
            else:
                xVal = verificar_substring("/", task_data[4])
                if xVal:
                    xDtF = datetime.strptime(task_data[4], "%Y/%m/%d").strftime("%Y%m%d")
                    xHrF = task_data[5]
                    if (xDtI == xDtF and xHrF == "") or (xDtF == "" and xHrF == ""):
                        xDtF = ""
                        xHrF = ""
                else:
                    xDtF = ""
                    xHrF = ""

            xInsert = "INSERT INTO TAREFAS (STS, DESCRICAO, DT_INI, HR_INI, DT_FIM, HR_FIM) VALUES ('"+xSts+"', '"+xDes+"', '"+xDtI+"', '"+xHrI+"', '"+xDtF+"', '"+xHrF+"')"

            cursor.execute(xInsert)
            self.connection.commit()
            cursor.close()
        except Error as e:
            print("Erro ao inserir tarefa no banco de dados:", e)

    def edit_task(self):
        selected_item = self.tree.selection()
        if not selected_item:
            tk.messagebox.showwarning("Aviso", "Selecione uma tarefa para editar!")
            return

        task_data = [
            self.task_id.get(),
            self.status.get(),
            self.description.get(),
            self.start_date.get(),
            self.start_time.get(),
            self.end_date.get(),
            self.end_time.get()
        ]

        if task_data[0] != "" and task_data[1] != "" and task_data[2] != "" and task_data[3] != "" and task_data[4] != "":
            self.tree.item(selected_item, values=task_data)
            self.update_task_in_db(task_data, selected_item[0])
            self.clear_entries()
            self.update_task_list()
        else:
            tk.messagebox.showwarning("Aviso", "Preencha todos os campos!")

    def update_task_in_db(self, task_data, task_id):
        try:

            xIdd = task_data[0]
            xSts = task_data[1]
            xDes = task_data[2]
            xDtI = datetime.strptime(task_data[3], "%d/%m/%Y").strftime("%Y%m%d")
            xHrI = task_data[4]

            xValid = verificar_substring("-", task_data[5])
            if xValid:
                xDtF = datetime.strptime(task_data[5], "%Y-%m-%d").strftime("%Y%m%d")
                xHrF = task_data[6]
                if (xDtI == xDtF and xHrF == "") or (xDtF == "" and xHrF == ""):
                    xDtF = ""
                    xHrF = ""
            else:
                xVal = verificar_substring("/", task_data[5])
                if xVal:
                    xDtF = datetime.strptime(task_data[5], "%Y/%m/%d").strftime("%Y%m%d")
                    xHrF = task_data[6]
                    if (xDtI == xDtF and xHrF == "") or (xDtF == "" and xHrF == ""):
                        xDtF = ""
                        xHrF = ""
                else:
                    xDtF = ""
                    xHrF = ""

            xUpd = "UPDATE TAREFAS SET "
            xUpd += "   STS = '" + xSts + "', "
            xUpd += "   DESCRICAO = '" + xDes + "', "
            xUpd += "   DT_INI = '" + xDtI + "', "
            xUpd += "   HR_INI = '" + xHrI + "', "
            xUpd += "   DT_FIM = '" + xDtF + "', "
            xUpd += "   HR_FIM = '" + xHrF + "' "
            xUpd += "WHERE ID = " + xIdd

            cursor = self.connection.cursor()
            cursor.execute(xUpd)
            self.connection.commit()
            cursor.close()
        except Error as e:
            print("Erro ao atualizar tarefa no banco de dados:", e)

    def delete_task(self):
        selected_item = self.tree.selection()
        if not selected_item:
            tk.messagebox.showwarning("Aviso", "Selecione uma tarefa para deletar!")
            return

        task_data = [
            self.task_id.get()
        ]

        confirmation = tk.messagebox.askyesno("Confirmação", "Tem certeza que deseja deletar esta tarefa?")
        if confirmation:
            self.tree.item(selected_item, values=task_data)
            self.delete_task_in_db(task_data, selected_item[0])
            self.update_task_list()

    def delete_task_in_db(self, task_data, task_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM TAREFAS WHERE ID = "+task_data[0])
            self.connection.commit()
            cursor.close()
        except Error as e:
            print("Erro ao deletar tarefa do banco de dados:", e)

    def clear_entries(self):

        xDtNow = datetime.now()
        xTzone = timezone('America/Fortaleza')
        xDtTiz = xDtNow.astimezone(xTzone)
        xDtHj = xDtTiz.strftime('%Y-%m-%d')

        self.task_id.set("")
        self.status.set(value='Pendente')
        self.description.set('')
        self.start_date.set(value=xDtHj)
        self.start_time.set(value=datetime.now().strftime("%H:%M:%S"))
        self.end_date.set(value=xDtHj)
        self.end_time.set("")

    def show_selected_task(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            task_values = self.tree.item(selected_item)['values']
            if task_values:
                self.task_id.set(task_values[0])
                self.status.set(task_values[1])
                self.description.set(task_values[2])
                self.start_date.set(task_values[3])
                self.start_time.set(task_values[4])
                self.end_date.set(task_values[5])
                self.end_time.set(task_values[6])

    def update_task_list(self):
        # Limpa a árvore
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Recarrega as tarefas do banco de dados
        self.load_tasks_from_db()

    def reload_task(self):
        self.clear_entries()
        self.update_task_list()

    def finaliza_task(self):
        selected_item = self.tree.selection()
        if not selected_item:
            tk.messagebox.showwarning("Aviso", "Selecione uma tarefa para Finalizar!")
            return

        task_data = [
            self.task_id.get(),
            self.status.get(),
            self.description.get(),
            self.start_date.get(),
            self.start_time.get(),
            self.end_date.get(),
            self.end_time.get()
        ]

        if task_data[0] != "":
            self.tree.item(selected_item, values=task_data)
            self.finaliza_task_in_db(task_data, selected_item[0])
            self.clear_entries()
            self.update_task_list()
        else:
            tk.messagebox.showwarning("Aviso", "Preencha todos os campos!")

    def finaliza_task_in_db(self, task_data, task_id):
        try:

            xDtNow = datetime.now()
            xTzone = timezone('America/Fortaleza')
            xDtTiz = xDtNow.astimezone(xTzone)
            xDtHj = xDtTiz.strftime('%Y%m%d')

            xIdd = task_data[0]
            xSts = task_data[1]
            xDes = task_data[2]
            xDtI = datetime.strptime(task_data[3], "%d/%m/%Y").strftime("%Y%m%d")
            xHrI = task_data[4]

            xValid = verificar_substring("-", task_data[5])
            if xValid:
                xDtF = datetime.strptime(task_data[5], "%Y-%m-%d").strftime("%Y%m%d")
                xHrF = task_data[6]
                if (xDtI == xDtF and xHrF == "") or (xDtF == "" and xHrF == ""):
                    xDtF = ""
                    xHrF = ""
            else:
                xVal = verificar_substring("/", task_data[5])
                if xVal:
                    xDtF = datetime.strptime(task_data[5], "%Y/%m/%d").strftime("%Y%m%d")
                    xHrF = task_data[6]
                    if (xDtI == xDtF and xHrF == "") or (xDtF == "" and xHrF == ""):
                        xDtF = ""
                        xHrF = ""
                else:
                    xDtF = ""
                    xHrF = ""

            if xDtF == "":
                xDtF = xDtHj

            if xHrF == "":
                xHrF = datetime.now().strftime("%H:%M:%S")

            xUpd = "UPDATE TAREFAS SET "
            xUpd += "   STS = 'Concluído', "
            xUpd += "   DESCRICAO = '" + xDes + "', "
            xUpd += "   DT_INI = '" + xDtI + "', "
            xUpd += "   HR_INI = '" + xHrI + "', "
            xUpd += "   DT_FIM = '" + xDtF + "', "
            xUpd += "   HR_FIM = '" + xHrF + "' "
            xUpd += "WHERE ID = " + xIdd

            cursor = self.connection.cursor()
            cursor.execute(xUpd)
            self.connection.commit()
            cursor.close()
        except Error as e:
            print("Erro ao finalizar a tarefa no banco de dados:", e)

if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()
    app.close_db_connection()
